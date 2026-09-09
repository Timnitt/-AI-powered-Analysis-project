import io
import logging
import os

import pandas as pd
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from prompts import analysis_prompt, cleaning_prompt, insight_prompt

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-data-assistant")

MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024
MODEL_ID = "google/gemini-2.5-flash"

app = FastAPI()

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GOOGLE_API_KEY"),
)
MODEL_ID = "gemini-2.5-flash"


def get_ai_response(prompt_text: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0,
    )
    return response.choices[0].message.content


def fix_python_syntax(code: str) -> str:
    lines = code.split("\n")
    fixed_lines = []
    for line in lines:
        clean_line = line.rstrip()
        if clean_line.startswith(("for ", "if ")) and not clean_line.endswith(
            ":"
        ):
            fixed_lines.append(clean_line + ":")
        else:
            fixed_lines.append(line)
    return "\n".join(fixed_lines)


def strip_code_fences(raw: str) -> str:
    return raw.strip().replace("```python", "").replace("```", "")


@app.post("/analyze")
async def analyze_data(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    history: str = Form(""),
):
    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File too large. Upload a file with size less than 200MB.",
            )

        file_data = io.BytesIO(contents)
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file_data, encoding="latin-1")
        else:
            df = pd.read_excel(file_data)

        data_audit = {
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
        }
        clean_raw = get_ai_response(cleaning_prompt(data_audit))
        clean_code = fix_python_syntax(strip_code_fences(clean_raw))

        cleaning_scope = {"df": df, "pd": pd}
        try:
            exec(clean_code, {}, cleaning_scope)
            df = cleaning_scope.get("df", df)
        except Exception as e:
            logger.warning("Data cleaning step failed, continuing with raw data: %s", e)

        analysis_raw = get_ai_response(
            analysis_prompt(df.columns.tolist(), history, prompt)
        )
        code = fix_python_syntax(strip_code_fences(analysis_raw))

        local_scope = {"df": df, "pd": pd}
        exec(code, {}, local_scope)
        final_numeric_result = local_scope.get("result", "No result")

        insight_text = get_ai_response(insight_prompt(prompt, final_numeric_result))
        return {"insight": insight_text}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to analyze uploaded file")
        return {"insight": f"System Error: {e!s}"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
