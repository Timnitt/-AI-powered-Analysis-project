from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import pandas as pd
import google.generativeai as genai
import os
import io
import traceback
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

#API configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

MAX_RETRIES = 3

@app.post("/analyze")
async def analyze_data(file: UploadFile = File(...), prompt: str = Form(...)):
    try:
        # 1. Read file into memory
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents), encoding='latin-1')
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        
        # Initial prompt for the AI
        current_prompt = f"""
        You are a Data Scientist. DataFrame 'df' has columns: {df.columns.tolist()}.
        Task: 
        1. Clean the data (handle NaNs,missing values,format,types for numeric columns).
        2. Answer: "{prompt}"
        
        Rules:
        - Store final answer in 'result'.
        - ONLY output code. No prose.
        - If you encounter an error, fix it and try again. You have {MAX_RETRIES} attempts to get it right.
        - If you can't answer the question with the data, set 'result' to a clear message explaining why.
        - Always ensure the code is syntactically correct and can run without errors.
        - If you need to perform calculations, create visualizations, or do any data manipulation, do it in the code. The user only sees the final 'result'.
        - Remember, the user is not a programmer. They only want insights from their data, not technical details. Keep 'result' focused on the insight, not the code or process.
        - If you encounter an error during execution, capture the full error message and include it in your next code attempt to help you debug.
        - If after {MAX_RETRIES} attempts you still can't get it right, set 'result' to a message saying you couldn't analyze the data and include the last error message for transparency.
        - Make sure to handle edge cases, such as empty data, all values being the same, or non-numeric data when numeric is expected.
        - Make sure twice the data is cleaned before you attempt to answer the question. Cleaning is a crucial step and should not be overlooked.
        - Make sure to consider the user's question carefully and ensure that your code is directly addressing it. If the question is ambiguous, make a reasonable assumption but clearly state it in the code comments.
        - Think step by step and ensure that your code is logically structured to first clean the data, then perform any necessary analysis, and finally set the 'result' variable to the insight that directly answers the user's question.
        - Make sure the cleaning process is robust and can handle common data issues such as missing values, outliers, and incorrect data types. This will ensure that the analysis is based on high-quality data and the insights are reliable.
        - Make sure the data cleaning is accurate and thorough. This is a critical step that will impact the quality of the insights. Handle missing values appropriately, convert data types as needed, and ensure that the data is in a format suitable for analysis before attempting to answer the user's question.
        - For the cleaning process, consider the following steps: 
            - Standardizing formatting across datasets 
            - Removing duplicate records  
            - Eliminating spelling, naming conventions, or categorization inconsistencies 
            - Validating data against rules and benchmarks.
            never autofill missing values in numbers, instead analyze the pattern of missingness and decide on a case-by-case basis whether to drop those rows, fill them with a placeholder, or use another strategy. Always explain your reasoning in code comments.
        """

        raw_result = None
        error_history = ""
        
        # --- THE VALIDATION LOOP ---
        for attempt in range(MAX_RETRIES):
            try:
                # Ask AI for code (include error history if this is a retry)
                full_request = current_prompt + error_history
                code_response = model.generate_content(full_request)
                code = code_response.text.strip().replace('```python', '').replace('```', '')

                # Execution Sandbox
                local_scope = {"df": df, "pd": pd}
                exec(code, {}, local_scope)
                
                # If we get here, the code worked!
                raw_result = local_scope.get("result")
                break 

            except Exception as e:
                # Capture the error and tell the AI what went wrong
                error_msg = traceback.format_exc()
                error_history = f"\n\nPrevious code failed with this error:\n{error_msg}\nPlease fix the code and try again."
                if attempt == MAX_RETRIES - 1:
                    raise Exception(f"AI could not fix the code after {MAX_RETRIES} attempts.")

        # 2. Convert raw result to Insight
        insight_prompt = f"The user asked: '{prompt}'. The result was: '{raw_result}'. Give a professional insight. Hide the technical details."
        insight_response = model.generate_content(insight_prompt)
        
        return {"insight": insight_response.text}

    except Exception as e:
        return {"insight": f"I tried to analyze your data but encountered a persistent issue: {str(e)}"}