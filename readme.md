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
- **Zero Excel knowledge required** - Any user can get a professional audit and analysis just by clicking **Upload** and **Show**

---
## Definition of Done

- [ ] User uploads a `.xlsx` or `.csv` successfully
- [ ] System auto-cleans dirty data
- [ ] System answers at least 5 test queries correctly
- [ ] Plain-English report generated and downloadable
- [ ] Tested by at least 3 non-technical users
- [ ] Results returned in under 60 seconds
- [ ] Demo completed in under 2 minutes

---
## How to Use

1. Open `http://localhost:8501` in your browser
2. Upload a `.xlsx` or `.csv` file using the sidebar
3. Type a plain-English question - e.g. *"What were the top 5 products last month?"*
4. Click **Show**
5. View the result and download as PDF or plain text

---

## License

MIT License - free to use, modify, and distribute.

---

*Solo Project · Week 5 · AI Data Assistant*