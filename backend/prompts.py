"""LLM prompt templates for AI Data Assistant."""


def cleaning_prompt(data_audit: dict) -> str:
    return (
        f"Write Python code to clean this DataFrame 'df': "
        f"{data_audit}. Output ONLY code."
    )


def analysis_prompt(columns: list, history: str, question: str) -> str:
    return f"""
You are a Deterministic Data Engine.
DataFrame 'df' Columns: {columns}

CHAT HISTORY:
{history}

CURRENT USER QUESTION: "{question}"

INSTRUCTION:
1. Look at the CHAT HISTORY to see what data we were just discussing.
2. Write Python code to calculate the answer for the CURRENT QUESTION.
3. Store the result in 'result'.
4. Output ONLY valid Python code.
"""


def insight_prompt(question: str, result) -> str:
    return (
        f"Question: {question}\nResult: {result}\nProvide 2-sentence business insight."
    )
