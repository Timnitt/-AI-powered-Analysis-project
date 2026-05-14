from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
from openai import OpenAI
import os
import io
import traceback
from dotenv import load_dotenv

# 1. Environment & App Setup
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
#OpenRouter Configuration
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)
MODEL_ID = "google/gemini-2.5-flash"

# 3. Helper Function to generate chat responses from OpenRouter.
def get_ai_response(prompt_text):
    """Utility to handle OpenRouter API calls using the client object"""
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0  #Keeping it deterministic for math accuracy
    )
    return response.choices[0].message.content


def fix_python_syntax(code: str) -> str:
    """Utility to automatically fix missing colons in AI-generated code"""
    lines = code.split('\n')
    fixed_lines = []
    for line in lines:
        clean_line = line.rstrip()
        if (clean_line.startswith('for ') or clean_line.startswith('if ')) and not clean_line.endswith(':'):
            fixed_lines.append(clean_line + ':')
        else:
            fixed_lines.append(line)
    return '\n'.join(fixed_lines)

@app.post("/analyze")
async def analyze_data(
    file: UploadFile = File(...), 
    prompt: str = Form(...),
    history: str = Form("") # Receive chat history
):
    try:
        # File Handling
        # Read a chunk to check size without loading the whole thing into RAM at once
        contents = await file.read() 
        if len(contents) > 200 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. upload a file with size less than 200MB.")
        
        # Reset cursor so pandas can read it afterward
        file_data = io.BytesIO(contents)
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_data, encoding='latin-1')
        else:
            df = pd.read_excel(file_data)

        # --- STEP 1: CLEANING (Using helper) ---
            # Audit data to identify messy columns (hidden spaces, $, % signs)
        data_audit = {
            "columns": df.columns.tolist(), 
            "dtypes": df.dtypes.astype(str).to_dict()
            }
        cleaning_prompt = f"Write Python code to clean this DataFrame 'df': {data_audit}. Output ONLY code."
        
        clean_raw = get_ai_response(cleaning_prompt)
        clean_code = fix_python_syntax(clean_raw.strip().replace('```python', '').replace('```', ''))
        
        # Execute cleaning with a safety scope
        cleaning_scope = {"df": df, "pd": pd}
        try:
            exec(clean_code, {}, cleaning_scope)
            df = cleaning_scope.get("df") 
        except Exception as e:
            print(f"Cleaning failed: {e}")

        # --- STEP 2: ANALYSIS ---
        code_prompt = f"""
            You are a Deterministic Data Engine. 
            DataFrame 'df' Columns: {df.columns.tolist()}

            CHAT HISTORY:
            {history}

            CURRENT USER QUESTION: "{prompt}"

            INSTRUCTION: 
            1. Look at the CHAT HISTORY to see what data we were just discussing.
            2. Write Python code to calculate the answer for the CURRENT QUESTION.
            3. Store the result in 'result'.
            4. Output ONLY valid Python code.
            """
        
        analysis_raw = get_ai_response(code_prompt)
        code = fix_python_syntax(analysis_raw.strip().replace('```python', '').replace('```', ''))

        local_scope = {"df": df, "pd": pd}
        exec(code, {}, local_scope)
        final_numeric_result = local_scope.get("result", "No result")

        # --- STEP 3: INSIGHT ---
        insight_prompt = f"Question: {prompt}\nResult: {final_numeric_result}\nProvide 2-sentence business insight."
        insight_text = get_ai_response(insight_prompt)
        return {"insight": insight_text}

    except Exception as e:
        # Debug print to catch connection issues in terminal
        print(f"Backend Error: {str(e)}")
        return {"insight": f"System Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)