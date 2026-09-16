# AI Data Assistant

[![CI](https://github.com/Timnitt/-AI-powered-Analysis-project/actions/workflows/ci.yml/badge.svg)](https://github.com/Timnitt/-AI-powered-Analysis-project/actions/workflows/ci.yml)

> Upload a spreadsheet, ask questions in plain English, get verified business insights — no Excel or SQL required.

**[Live Demo](https://ai-data-assistant-47sw.onrender.com)** · [Problem Statement](#problem-statement) · [Developer Setup](#developer-setup)

> *The live demo is hosted on Render's free tier — the first load may take 30–60 seconds while the server wakes up.*

---

## Architecture

```
┌─────────────────────┐    POST /analyze       ┌──────────────────────────────────┐
│                     │  ─────────────────►    │          FastAPI Backend          │
│  Streamlit Frontend │  file + question       │                                  │
│                     │                        │  1. Parse CSV / Excel            │
│  • File upload      │  ◄─────────────────    │  2. AI → cleaning code           │
│  • Chat UI          │  JSON { insight,       │  3. AI → analysis code           │
│  • Chart display    │         chart }        │  4. Sandboxed exec() ─┐          │
│  • DOCX export      │                        │  5. AI → business     │ 3-layer  │
│  • Data quality     │    POST /data-quality   │     insight           │ sandbox  │
│    sidebar panel    │  ─────────────────►    │  6. AI → matplotlib   │ security │
│                     │  ◄─────────────────    │     chart (base64)  ──┘          │
│                     │  JSON { nulls,         │                                  │
│                     │    duplicates,          │  /data-quality                   │
│                     │    outliers }           │  • Null analysis                 │
└─────────────────────┘                        │  • Duplicate detection            │
                                               │  • Outlier detection (IQR)       │
                                               └──────────────┬───────────────────┘
                                                              │
                                                              │ OpenAI-compatible API
                                                              ▼
                                               ┌──────────────────────────────────┐
                                               │    Google Gemini 3.6 Flash       │
                                               │    (via OpenAI SDK)              │
                                               └──────────────────────────────────┘
```

**Key design decisions:**
- The AI does not guess answers. It writes deterministic Python code that runs against the real data, so every number is mathematically verified — not hallucinated.
- All AI-generated code runs inside a **3-layer sandbox** (static blocklist, restricted builtins, thread-based timeout) — never raw `exec()`.
- Data quality is assessed **before** the user asks any question, surfacing issues like nulls and outliers upfront.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit (Python) |
| **Backend** | FastAPI + Uvicorn |
| **AI Model** | Google Gemini 3.6 Flash via OpenAI-compatible API |
| **Data Processing** | Pandas, openpyxl |
| **Visualization** | Matplotlib (AI-generated charts) |
| **Security** | 3-layer sandboxed `exec()` (blocklist + restricted builtins + timeout) |
| **Export** | python-docx (Word reports) |
| **Testing** | pytest (58 tests) + ruff linter |
| **CI/CD** | GitHub Actions (lint + test on every push) |
| **Deployment** | Docker Compose · Render |

---

## Features

- **Natural Language Queries** — Ask questions about your data in plain English
- **AI-Generated Charts** — Every insight comes with an auto-generated matplotlib visualization
- **Data Quality Report** — Automatic scan for nulls, duplicates, and outliers on upload
- **Sandboxed Execution** — AI-generated code runs in a 3-layer security sandbox
- **Conversation Memory** — Follow-up questions carry full chat history for contextual answers
- **Word Export** — Download the full analysis session as a `.docx` report
- **58 Unit Tests** — Full coverage across API, sandbox, prompts, and data quality

---

## How It Works

1. **Upload** — CSV or Excel file (up to 200 MB) via the sidebar
2. **Quality Check** — The system automatically scans for missing values, duplicates, and outliers (IQR method) and displays a report in the sidebar
3. **Ask** — Type a plain-English question (e.g. *"What were the top 3 loss-making products?"*)
4. **AI Pipeline** — The backend runs four LLM calls, each sandboxed:
   - **Clean** — generates Python to fix data types, nulls, formatting
   - **Analyze** — generates Python to compute the answer, stores it in `result`
   - **Explain** — translates the numeric result into a plain-English business insight
   - **Visualize** — generates a matplotlib chart to accompany the insight (returned as base64 PNG)
5. **Chat** — Ask follow-up questions; the full conversation history is passed to the model
6. **Export** — Download the session as a `.docx` report

---

## Try It Out

A sample dataset is included in the [`sample_data/`](./sample_data/) folder — a Superstore sales CSV with columns like Sales, Profit, Category, Region, and more. Upload it to the app and try questions like:

- *"What are the total sales?"*
- *"What is the total profit?"*
- *"Show total profit per category"*
- *"Which region has the highest sales?"*
- *"What are the top 5 most profitable products?"*
- *"Compare sales and profit by region"*

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
