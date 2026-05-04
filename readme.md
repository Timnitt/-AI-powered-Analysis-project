# AI Data Assistant

> AI-Powered analysis for small companies and non-technical staff.

---
## Problem Statement

In many companies, operational staff - sales, marketing, support, and managers - rely on data stored in Excel and other databases. Accessing this data requires Excel skills or SQL knowledge that most non-technical employees don't have. As a result, they depend on manual analysis or data analysts for even simple queries.

This is especially true for small companies that don't have the capacity to employ professional analysts.

**The problem:**

- Small retail companies without data analysts struggle to do basic analysis
- Non-technical staff experience slow, manual analysis
- Delays of hours slow down decision-making
- Constant need for a technical employee

**Evidence:**

- Over 80% of small business data is stored in dirty spreadsheets with inconsistent formatting, duplicate entries, or missing values
- Operational staff spend 4–6 hours per week just formatting and cleaning data before they can ask a question
- Less than 15% of staff can perform advanced Excel functions like Pivot Tables, VLOOKUPs, or Power Query
- Internal data teams report that 40–70% of incoming requests are simple queries

**Impact:**

- Delayed decisions, reduced productivity, and uninformed operations
- Small companies fail to spot leaky buckets - products losing money or inefficient marketing spend - because data is too messy to read
- Non-technical staff experience "data dread," leading to gut-feeling decisions rather than data-driven ones
- Time wasted on low-value tasks and missed business opportunities

---
## Objectives

- **One-Click Analysis** - Users upload a standard `.xlsx` or `.csv` and receive a structured summary without writing a single formula
- **Natural Language Reporting** - Deliver a final report in plain English, e.g. *"Your sales peaked on Wednesday because of Category X"*
- **Zero Excel knowledge required** - Any user can get a professional audit and analysis just by clicking **Upload** ,**Chat** and **Generate**

---
## Definition of Done
- [ ] User uploads a .xlsx or .csv successfully.
- [ ] System auto-cleans messy data.
- [ ] System answers at least 5 test queries correctly.
- [ ] Plain-English report generated based on mathematical facts.
- [ ] Results returned in under 60 seconds.
- [ ] Demo completed in under 2 minutes.
---

## How to Use
1. Upload: Use the sidebar to upload a .csv or .xlsx file[cite: 7].
2. Chat: Type a plain-English question in the chat input (e.g., "What were the total sales ?").
3. Generate: The AI will generate a deterministic Python script, execute it, and provide a verified insight.
4. Insight: View the result and continue the conversation.
---
## How to Run for developers

This project is split into a **Frontend (Streamlit)** and a **Backend (FastAPI)**.

### 1. Prerequisites
Ensure you have a `.env` file in your **backend** directory:
GOOGLE_API_KEY=your_actual_key_here 

---
### 2. Backend Setup

Navigate to the backend folder: cd backend
- Install dependencies: pip install -r requirements.txt
- Start the server: python main.py
- Runs on: http://127.0.0.1:8000

Dependencies:

FastAPI
uvicorn
google-generativeai
pandas
python-dotenv
openpyxl

### 3. Frontend Setup (Streamlit)
- Navigate to the frontend folder: cd frontend
- Install dependencies: pip install -r requirements.txt
- Start the app: streamlit run app.py
- Runs on: http://localhost:8501

Dependencies:

streamlit
requests

---

## License

MIT License - free to use, modify, and distribute.

---

*Solo Project · AI Data Assistant*