from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
import google.generativeai as genai
import os
import io
import traceback
from dotenv import load_dotenv

# Environment & App Setup
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model Configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

generation_config = {
    "temperature": 0,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    generation_config=generation_config
)

@app.post("/analyze")
async def analyze_data(
    file: UploadFile = File(...), 
    prompt: str = Form(...),
    history: str = Form("") # New: Receive chat history
):
    try:
       # Read file with size check to prevent memory issues
        MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB in bytes
    
        # Read a chunk to check size without loading the whole thing into RAM at once
        contents = await file.read() 
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Max 200MB.")
        
        # Reset cursor so pandas can read it afterward
        file_data = io.BytesIO(contents)

        # ... proceed to pd.read_csv(file_data)
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents), encoding='latin-1')
        else:
            df = pd.read_excel(io.BytesIO(contents))
            

        # Audit data to identify messy columns (hidden spaces, $, % signs)
        data_audit = {
            "columns": df.columns.tolist(),
            "sample_rows": df.head(2).to_dict(),
            "dtypes": df.dtypes.astype(str).to_dict()
        }

        cleaning_prompt = f"""
        You are a Data Cleaning Agent. Analyze this data profile: {data_audit}
        
        Write Python code to clean the DataFrame 'df':
        1. Strip leading/trailing spaces from all column names and string cells.
        2. Identify numeric columns currently stored as strings (with $, %, or commas) and convert them to floats.
        3. Ensure no empty strings remain (convert to NaN).
        
        RULES:
        - Output ONLY valid Python code.
        - Use 4-space indentation for any loops or conditionals.
        - The final cleaned dataframe must remain as variable 'df'.
        - Do NOT add any code for analysis or insights in this block. Focus solely on cleaning the data as per the instructions above.
        - PII PROTECTION: If you detect Personal Identifiable Information (like specific Names, Emails, or Phone numbers), replace them with generic placeholders (e.g., [PERSON_A], [USER_EMAIL]) in the 'df' before returning it.
        - If you encounter any columns that are completely empty or contain only null values, drop those columns from 'df'.

        """
        
        clean_resp = model.generate_content(cleaning_prompt)
        clean_code = clean_resp.text.strip().replace('```python', '').replace('```', '')
        
        # --- FIX FOR CLEANING BLOCK INDENTATION ---
        clean_lines = clean_code.split('\n')
        fixed_clean_lines = []
        for line in clean_lines:
            clean_line = line.rstrip()
            # Fix missing colons in cleaning loops/conditionals
            if (clean_line.startswith('for ') or clean_line.startswith('if ')) and not clean_line.endswith(':'):
                fixed_clean_lines.append(clean_line + ':')
            else:
                fixed_clean_lines.append(line)
        clean_code = '\n'.join(fixed_clean_lines)
        # --- END FIX ---


        # Execute cleaning with a safety scope
        cleaning_scope = {"df": df, "pd": pd}
        try:
            exec(clean_code, {}, cleaning_scope)
            df = cleaning_scope.get("df") 
        except Exception as e:
            print(f"Cleaning failed, proceeding with raw data: {e}")
            # If cleaning fails, we keep the original df to avoid a total crash
        # --- END OF CLEANING BLOCK ---

        # 'No-Guessing' Logic with Context
        code_prompt = f"""
        You are a Deterministic Data Engine. 
        DataFrame 'df' Columns: {df.columns.tolist()}
        
        CHAT HISTORY:
        {history}
        
        CURRENT USER QUESTION: "{prompt}"
        
        TASK: Write Python code to calculate the exact answer for the CURRENT QUESTION. 
        If the user says "them" or "that", refer to the CHAT HISTORY above to understand the context.
        
        CRITICAL RULES:
        1. DO NOT estimate. Use the 'df' object.
        2. Store the FINAL result in a variable named 'result'.
        3. ONLY return valid Python code.
        """


        error_log = ""
        final_numeric_result = None
        # Attempt to get the correct code with retries/ validation loop
        for attempt in range(3):
            try:
                response = model.generate_content(code_prompt + error_log)
                # Clean the response to ensure it is strictly code
                code = response.text.strip().replace('```python', '').replace('```', '')

                # --- ADD THIS FIX HERE ---
                # This ensures common colon-omissions are fixed before execution
                lines = code.split('\n')
                fixed_lines = []
                for line in lines:
                    # If a line starts with 'for' or 'if' and doesn't end with a colon, add one
                    clean_line = line.rstrip()
                    if (clean_line.startswith('for ') or clean_line.startswith('if ')) and not clean_line.endswith(':'):
                        fixed_lines.append(clean_line + ':')
                    else:
                        fixed_lines.append(line)
                code = '\n'.join(fixed_lines)
                # --- END OF FIX ---

                # Execute in the trusted local scope
                local_scope = {"df": df, "pd": pd}
                exec(code, {}, local_scope)
                
                if "result" in local_scope:
                    final_numeric_result = local_scope["result"]
                    break
                else:
                    raise Exception("Variable 'result' was not defined in the code.")
            
            except Exception as e:
                error_log = f"\n\nRetry {attempt+1}: Your previous code failed with: {str(e)}. Fix it."

        # The Final Insight Logic
        insight_prompt = f"""
        User Question: {prompt}
        Mathematical Result: {final_numeric_result}
        
        Instruction: 
        - Provide a 2-sentence professional insight based ONLY on the Mathematical Result above. 
        - If the result is {final_numeric_result}, you MUST use that exact number.
        - CRITICAL: Use standard English spacing. Do NOT concatenate words.
        - Ensure there is a space after every comma and period.
        - Do NOT add any assumptions or estimates beyond what the number directly indicates.
        - If the result is a number, interpret it in a business context. For example, if the result is 1000, you might say "The total sales amount to $1000, which indicates...".
        - If the result is a string, provide an insight based on that string. For example, if the result is "New York", you might say "The top-selling region is New York, suggesting...".
        - ONLY return the insight text. No code or heavy technical explanations.
        - If the result is not a valid number or string, respond with "The result is not interpretable for insights."
        - ask the model to be very specific and avoid generic insights. For example, instead of saying "This is a good result", it should say "The total sales of $1000 suggest a strong performance in Q1, likely driven by the new marketing campaign."
        - you tone should be professional and data-driven. Avoid vague language. Be specific about what the number means in a business context.
        - use words like "suggests", "indicates", "implies" to connect the mathematical result to the insight, but do not make assumptions beyond what the number directly indicates.
        - use words that non-technical business users would understand. For example, instead of saying "The mean sales is $1000", say "The average sales amount to $1000, which suggests a strong performance in that category."
        - use the current date to make the insight timely. For example, "As of 2024, the total sales of $1000 suggest..."
        - use the appropriate units if the result is a number. For example, if the result is 1000 and it represents sales in thousands, say "The total sales amount to $1 million..."
        - if the result is a string that represents a category, say "The top-selling category is X, which suggests..., and the least-selling category is Y, which indicates..."
        - if the result is a string that represents a date, say "The peak sales occurred
        - if the user asks for a question out of the context like hi, how are you, the model should respond with "I am designed to provide insights based on the uploaded data. Please upload a file and ask a specific question about it. be polite and professional in your response. For example, you could say "What is the total sales for Q1?" or "Which region has the highest revenue?" 
        - be also prepared for accurate follow-up questions. For example, if the user first asks "What is the total sales?" and then asks "how about by regions?", you should be able to provide insights for both questions based on the mathematical results.
        """
        
        insight_response = model.generate_content(insight_prompt)
        return {"insight": insight_response.text}

    except Exception as e:
        # Debug print to catch connection issues in terminal
        print(f"Backend Error: {str(e)}")
        return {"insight": f"System Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)