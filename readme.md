# AI Data Assistant

> AI-powered data analysis for small companies and non-technical staff

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Scope (User Stories)](#scope-user-stories)
- [Definition of Done](#definition-of-done)
- [How to Use](#how-to-use)
- [Developer Setup](#developer-setup)
  - [Prerequisites](#prerequisites)
  - [Backend](#backend-fastapi)
  - [Frontend](#frontend-streamlit)
- [Triage Log](#triage-log)

---

## Problem Statement

Operational staff - sales, marketing, support, and managers - depend daily on data stored in spreadsheets and databases. But accessing that data requires Excel skills or SQL knowledge that most non-technical employees simply don't have. The result: dependence on manual analysis, long delays, and gut-feeling decisions.

This problem hits small companies hardest, where there's no dedicated data analyst to absorb the load.

### The Pain Points

> These figures are drawn from published industry research (linked in [Sources](#sources) below), not internal data. They're used to frame the size of the problem, not as claims about any specific customer.

- Knowledge workers spend an estimated **30–50% of their time** acting as "data janitors" - cleaning, reformatting, and hunting for data across disconnected sources
- Academic research on operational spreadsheets found that **94% of spreadsheets contain at least one error** (Panko, *What We Know About Spreadsheet Errors*)
- In organizations without self-service analytics tools, analysts can spend **50–70% of their time** on one-off, ad-hoc requests rather than higher-value analysis
- A large share of employees report only basic proficiency in Excel, meaning core features like PivotTables, VLOOKUP, and Power Query go largely unused day-to-day

### The Impact

- Delayed decisions and reduced productivity across the business
- Non-technical staff develop "data dread," defaulting to instinct over evidence
- Low-value formatting tasks crowd out meaningful, strategic work

### Sources

- [Why Are Knowledge Workers Still Cleaning Data? – Reworked](https://www.reworked.co/digital-workplace/why-are-knowledge-workers-still-cleaning-data/)
- [What We Know About Spreadsheet Errors – Panko, University of Hawai'i](http://panko.shidler.hawaii.edu/SSR/Mypapers/whatknow.htm)
- [Avoiding Analyst Burnout: How to Streamline Ad Hoc Requests – Metabase](https://www.metabase.com/blog/ad-hoc-analysis-tips)
- [An Analyst's Guide to Handling Ad-hoc Requests – OWOX](https://www.owox.com/blog/articles/analysts-guide-managing-one-off-ad-hoc-requests)

---

## Objectives

| Goal | Description |
|------|-------------|
| **One-Click Analysis** | Upload a `.xlsx` or `.csv` and receive a structured summary - no formulas required |
| **Natural Language Reporting** | Results delivered in plain English, e.g. *"Your sales peaked on Wednesday due to Category X"* |
| **Zero Excel Knowledge Required** | Any user can get a professional analysis in three steps: **Upload → Chat → Generate** |

---

## Scope (User Stories)

Written from the perspective of the primary persona: a non-technical operational employee at a small business.

### Must Have

- As a user, I want to **upload a `.csv` or `.xlsx` file**, so that I can analyze my own data without asking IT or a data analyst for help.
- As a user, I want to **ask questions in plain English**, so that I don't need to know Excel formulas or SQL.
- As a user, I want the **AI's calculations to be mathematically verified** (run as real code, not guessed by the model), so that I can trust the numbers in a business decision.
- As a user, I want a **plain-English insight**, not just a raw number, so that I understand what the result means for my business.

### Should Have

- As a user, I want to **ask follow-up questions** that reference earlier parts of the conversation, so that I can explore my data conversationally instead of starting over each time.
- As a user, I want to **export my analysis session as a Word document**, so that I can share results with my manager or team.
- As a user, I want to **see the maximum upload size before I upload**, so that I don't waste time uploading a file that will be rejected.

### Could Have

- As a user, I want to **see a chart alongside the written insight**, so that I can visually confirm trends.
- As a user, I want to **save and reload past sessions**, so that I don't lose my analysis when I close the browser tab.
- As a user, I want **automatic detection and flagging of data quality issues** (duplicates, missing values) before analysis, so that I understand how trustworthy my results are.

### Won't Have (this iteration)

- Multi-user accounts, authentication, and permissions
- Persistent server-side storage of uploaded data (files are processed in-memory per request)
- Real-time collaboration between multiple users on the same session
- Support for data sources beyond flat files (e.g. live database connections)

---

## Definition of Done

A feature is considered **done** when it meets all of the following acceptance criteria:

- [ ] Code is merged to `main` and runs without errors on a clean install (`pip install -r requirements.txt`)
- [ ] The feature has been manually tested against at least 5 representative user queries
- [ ] Errors (bad file type, oversized file, malformed query) fail gracefully with a user-facing message - never a raw stack trace
- [ ] No secrets, API keys, or hardcoded environment-specific URLs are committed to the repository
- [ ] The README and/or Triage Log is updated to reflect any setup or behavior change
- [ ] The end-to-end demo (upload → ask → insight) completes in under 2 minutes

---

## How to Use

1. **Upload** - Use the sidebar to upload a `.csv` or `.xlsx` file (max size: **200MB**)
2. **Chat** - Type a plain-English question in the chat input (e.g. *"What were the total sales last month?"*)
3. **Generate** - The AI generates a deterministic Python script, executes it, and returns a verified insight
4. **Insights** - View the result and continue the conversation with follow-up questions
5. **Export** - Download the full conversation as a `.docx` report from the sidebar

**Example questions to try:**

- *"What is the total sales?"*
- *"What is the profit?"*
- *"How many orders had a negative profit, and what were the top 3 loss-making products?"*

---

## Developer Setup

This project is split into a **Backend (FastAPI)** and a **Frontend (Streamlit)**.

### Prerequisites

Create a `.env` file inside the `backend/` directory (see `backend/.env.example`):

```env
GOOGLE_API_KEY=your_actual_key_here
# Comma-separated list of allowed frontend origins for CORS
ALLOWED_ORIGINS=http://localhost:8501
```

Get a key at [Google AI Studio](https://aistudio.google.com/apikey).

Create a `.env` file inside the `frontend/` directory (see `frontend/.env.example`):

```env
BACKEND_URL=http://127.0.0.1:8000
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
pandas
python-dotenv
openai==1.12.0
httpx==0.27.0
openpyxl
python-multipart
```

The backend talks to Gemini via [Google's OpenAI-compatible endpoint](https://ai.google.dev/gemini-api/docs/openai), using the `openai` client pointed at `generativelanguage.googleapis.com` — not the `google-generativeai` SDK.

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
pydantic
requests
python-docx
python-dotenv
```

---
#### Docker (optional)

Run both services together with Docker Compose instead of setting up two separate virtual environments:

```bash
docker compose up --build
```
Frontend: http://localhost:8501
Backend: http://localhost:8000

---

## Triage Log

Problems encountered during development and how they were resolved are tracked in [`TRIAGE_LOG.md`](./TRIAGE_LOG.md).

---

## License

MIT License - free to use, modify, and distribute.

Timnit
---
