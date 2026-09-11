import base64
import io
import logging
import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from prompts import analysis_prompt, chart_prompt, cleaning_prompt, insight_prompt
from sandbox import SandboxTimeout, SandboxViolation, safe_exec

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-data-assistant")

MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024
MODEL_ID = "gemini-3.6-flash"
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
MODEL_ID = "gemini-3.6-flash"


def get_ai_response(prompt_text: str) -> str:
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0,
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                wait = min(5 * (attempt + 1), 30)
                logger.info(
                    "Rate limited, waiting %ds (attempt %d/5)",
                    wait, attempt + 1,
                )
                time.sleep(wait)
            else:
                raise
    raise Exception("API rate limit exceeded. Please try again in a minute.")


def fix_python_syntax(code: str) -> str:
    lines = code.split("\n")
    fixed_lines = []
    for line in lines:
        clean_line = line.rstrip()
        if clean_line.startswith(("for ", "if ")) and not clean_line.endswith(":"):
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
            safe_exec(clean_code, cleaning_scope)
            df = cleaning_scope.get("df", df)
        except SandboxViolation as e:
            logger.warning("Cleaning code blocked by sandbox: %s", e)
        except SandboxTimeout:
            logger.warning("Cleaning code timed out, using raw data")
        except Exception as e:
            logger.warning("Data cleaning step failed, continuing with raw data: %s", e)

        time.sleep(2)
        analysis_raw = get_ai_response(
            analysis_prompt(df.columns.tolist(), history, prompt)
        )
        code = fix_python_syntax(strip_code_fences(analysis_raw))

        local_scope = {"df": df, "pd": pd}
        safe_exec(code, local_scope)
        final_numeric_result = local_scope.get("result", "No result")

        time.sleep(2)
        insight_text = get_ai_response(insight_prompt(prompt, final_numeric_result))

        chart_b64 = None
        try:
            time.sleep(2)
            chart_raw = get_ai_response(
                chart_prompt(df.columns.tolist(), prompt, final_numeric_result)
            )
            chart_code = fix_python_syntax(strip_code_fences(chart_raw))
            plt.close("all")
            chart_scope = {"df": df, "pd": pd, "plt": plt}
            safe_exec(chart_code, chart_scope)
            fig = chart_scope.get("fig", plt.gcf())
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
            plt.close("all")
            buf.seek(0)
            chart_b64 = base64.b64encode(buf.getvalue()).decode()
        except Exception as e:
            logger.warning("Chart generation failed, returning text only: %s", e)

        return {"insight": insight_text, "chart": chart_b64}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to analyze uploaded file")
        return {"insight": f"System Error: {e!s}"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
