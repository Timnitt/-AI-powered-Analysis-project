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


def chart_prompt(columns: list, question: str, result) -> str:
    return f"""
You are a data visualization expert.
DataFrame 'df' has columns: {columns}

USER QUESTION: "{question}"
COMPUTED RESULT: {result}

Write Python code using matplotlib to create a chart that best visualizes
the answer. Use 'df' (already loaded) and 'plt' (already imported).

Rules:
- Pick the most appropriate chart type (bar, line, pie, scatter, etc.).
- Use plt.figure(figsize=(8, 5)) to start.
- Add a clear title, axis labels, and clean styling.
- Use plt.tight_layout() at the end.
- Store the figure in a variable called 'fig' (fig = plt.gcf()).
- Do NOT call plt.show().
- Output ONLY valid Python code.
"""
