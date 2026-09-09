# AI Data Assistant

[![CI](https://github.com/Timnitt/-AI-powered-Analysis-project/actions/workflows/ci.yml/badge.svg)](https://github.com/Timnitt/-AI-powered-Analysis-project/actions/workflows/ci.yml)

> Upload a spreadsheet, ask questions in plain English, get verified business insights — no Excel or SQL required.

**[Live Demo](https://ai-data-assistant-47sw.onrender.com)** · [Problem Statement](#problem-statement) · [Developer Setup](#developer-setup)

> *The live demo is hosted on Render's free tier — the first load may take 30–60 seconds while the server wakes up.*

---

## Architecture

```
┌─────────────────┐       POST /analyze        ┌─────────────────────────────┐
│                 │  ───────────────────────►  │                             │
│    Streamlit    │   file + question + history │       FastAPI Backend       │
│    Frontend     │                            │                             │
│                 │  ◄───────────────────────  │  1. Parse CSV / Excel       │
│  • File upload  │       JSON { insight }     │  2. AI → cleaning code      │
│  • Chat UI      │                            │  3. AI → analysis code      │
│  • DOCX export  │                            │  4. Execute Python (exec)   │
└─────────────────┘                            │  5. AI → plain-English      │
                                               │     business insight        │
                                               └──────────┬──────────────────┘
                                                          │
                                                          │ OpenAI-compatible API
                                                          ▼
                                               ┌─────────────────────────────┐
                                               │   Google Gemini 2.5 Flash   │
                                               │   (via OpenAI SDK)          │
                                               └─────────────────────────────┘
```

**Key design decision:** The AI does not guess answers. It writes deterministic Python code that runs against the real data, so every number is mathematically verified — not hallucinated.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit (Python) |
| **Backend** | FastAPI + Uvicorn |
| **AI Model** | Google Gemini 2.5 Flash via OpenAI-compatible API |
| **Data Processing** | Pandas, openpyxl |
| **Export** | python-docx (Word reports) |
| **CI/CD** | GitHub Actions (ruff lint + pytest) |
| **Deployment** | Docker Compose · Render |

---

## How It Works

1. **Upload** — CSV or Excel file (up to 200 MB) via the sidebar
2. **Ask** — Type a plain-English question (e.g. *"What were the top 3 loss-making products?"*)
3. **AI Pipeline** — The backend runs three LLM calls:
   - **Clean** — generates Python to fix data types, nulls, formatting
   - **Analyze** — generates Python to compute the answer, stores it in `result`
   - **Explain** — translates the numeric result into a 2-sentence business insight
4. **Chat** — Ask follow-up questions; the full conversation history is passed to the model
5. **Export** — Download the session as a `.docx` report

---

## Developer Setup

### Prerequisites

Create `.env` files from the examples:

```bash
cp backend/.env.example backend/.env    # add your GOOGLE_API_KEY
cp frontend/.env.example frontend/.env
```

Get an API key at [Google AI Studio](https://aistudio.google.com/apikey).

### Run with Docker (recommended)

```bash
docker compose up --build
```

Frontend: http://localhost:8501 · Backend: http://localhost:8000

### Run manually

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

### Run tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
ruff check .
```

---

## Problem Statement

Operational staff — sales, marketing, support, and managers — depend daily on data stored in spreadsheets. But accessing that data requires Excel skills or SQL knowledge most non-technical employees don't have. The result: dependence on manual analysis, long delays, and gut-feeling decisions.

This problem hits small companies hardest, where there's no dedicated data analyst.

### The Pain Points

> Figures drawn from published industry research ([sources below](#sources)), not internal data.

- Knowledge workers spend **30–50% of their time** cleaning, reformatting, and hunting for data
- **94% of spreadsheets** contain at least one error (Panko, *What We Know About Spreadsheet Errors*)
- Analysts without self-service tools spend **50–70% of their time** on ad-hoc requests
- Most employees report only basic Excel proficiency — PivotTables, VLOOKUP, and Power Query go unused

### Sources

- [Why Are Knowledge Workers Still Cleaning Data? – Reworked](https://www.reworked.co/digital-workplace/why-are-knowledge-workers-still-cleaning-data/)
- [What We Know About Spreadsheet Errors – Panko](http://panko.shidler.hawaii.edu/SSR/Mypapers/whatknow.htm)
- [Avoiding Analyst Burnout – Metabase](https://www.metabase.com/blog/ad-hoc-analysis-tips)
- [Handling Ad-hoc Requests – OWOX](https://www.owox.com/blog/articles/analysts-guide-managing-one-off-ad-hoc-requests)

---

## Triage Log

Problems encountered during development and how they were resolved are tracked in [`TRIAGE_LOG.md`](./TRIAGE_LOG.md).

---

## License

MIT License — free to use, modify, and distribute.

Timnit
