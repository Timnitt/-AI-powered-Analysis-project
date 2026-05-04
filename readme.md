# AI Data Assistant

> AI-powered data analysis for small companies and non-technical staff - no formulas, no SQL, no friction.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Definition of Done](#definition-of-done)
- [How to Use](#how-to-use)
- [Developer Setup](#developer-setup)
  - [Prerequisites](#prerequisites)
  - [Backend](#backend-fastapi)
  - [Frontend](#frontend-streamlit)
- [License](#license)

---

## Problem Statement

Operational staff - sales, marketing, support, and managers- depend daily on data stored in spreadsheets and databases. But accessing that data requires Excel skills or SQL knowledge that most non-technical employees simply don't have. The result: dependence on manual analysis, long delays, and gut-feeling decisions.

This problem hits small companies hardest, where there's no dedicated data analyst to absorb the load.

### The Pain Points

- Small businesses without data analysts struggle to perform even basic analysis
- Non-technical staff spend **4–6 hours per week** just formatting and cleaning data before they can ask a single question
- Over **80% of small business data** lives in dirty spreadsheets with inconsistent formatting, duplicates, or missing values
- Fewer than **15% of staff** can use advanced Excel features like Pivot Tables, VLOOKUPs, or Power Query
- Internal data teams report that **40–70% of incoming requests are simple queries** that shouldn't require specialist time

### The Impact

- Delayed decisions and reduced productivity across the business
- Non-technical staff develop "data dread," defaulting to instinct over evidence
- Low-value formatting tasks crowd out meaningful, strategic work

---

## Objectives

| Goal | Description |
|------|-------------|
| **One-Click Analysis** | Upload a `.xlsx` or `.csv` and receive a structured summary - no formulas required |
| **Natural Language Reporting** | Results delivered in plain English, e.g. *"Your sales peaked on Wednesday due to Category X"* |
| **Zero Excel Knowledge Required** | Any user can get a professional analysis in three steps: **Upload → Chat → Generate** |

---

## Definition of Done

- [ ] User can upload a `.xlsx` or `.csv` file successfully
- [ ] System auto-cleans messy or inconsistent data
- [ ] System answers at least 5 test queries correctly
- [ ] Plain-English report generated from verified, mathematical facts
- [ ] Results returned in under 60 seconds
- [ ] End-to-end demo completable in under 2 minutes

---

## How to Use

1. **Upload** - Use the sidebar to upload a `.csv` or `.xlsx` file
2. **Chat** - Type a plain-English question in the chat input (e.g. *"What were the total sales last month?"*)
3. **Generate** - The AI generates a deterministic Python script, executes it, and returns a verified insight
4. **Insights** - View the result and continue the conversation with follow-up questions

---

## Developer Setup

This project is split into a **Backend (FastAPI)** and a **Frontend (Streamlit)**.

### Prerequisites

Create a `.env` file inside the `backend/` directory:

```env
GOOGLE_API_KEY=your_actual_key_here
```

---

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Runs on: `http://127.0.0.1:8000`

**Dependencies:**

```
fastapi
uvicorn
google-generativeai
pandas
python-dotenv
openpyxl
```

---

### Frontend (Streamlit)

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Runs on: `http://localhost:8501`

**Dependencies:**

```
streamlit
requests
```

---

## License

MIT License — free to use, modify, and distribute.

---

*Solo Project · AI Data Assistant*
