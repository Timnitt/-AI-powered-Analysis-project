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
 
## Project Folder Structure
```text
AI-powered-Analysis-project/
├── .env                  # Stores your API key securely
├── requirements.txt      # List of libraries to install
├── app.py                # Your main Streamlit code
└── data/
    └── Superstore_clean_sample data.csv  # Your test data
```


## How to Use

1. Open `http://localhost:8501` in your browser
2. Upload a `.xlsx` or `.csv` file using the sidebar
3. Type a plain-English question - e.g. *"What is last week sales"*
4. Click **Generate response**
5. View the result and download as PDF or plain text

---
## How to Run for developers

1. The Requirements File (requirements.txt)
Paste this into your requirements.txt file. These are the tools we need:
    - Plaintext
    - streamlit
    - pandas
    - requests
    - python-dotenv
2. run using git bash command
    - Open the Terminal in VS Code - Press Ctrl +  ` (the backtick key) or go to Terminal > New Terminal.
      - In the top-right corner of the terminal window, ensure the dropdown menu says bash. If it says powershell or cmd, click the arrow next to the + and select Git Bash.
    - Navigate to Your Project Folder - cd /c/path/to/your/folder/ai_retail_analyst
    - Activate the environment - source venv/Scripts/activate
    - Verify Your Environment - pip install -r requirements.txt
    - Run the Streamlit App - streamlit run app.py
3. Summary of Commands (The "Quick Restart" List)
Next time you open VS Code, just run these three lines in your Git Bash terminal:
    - source venv/Scripts/activate
    - streamlit run app.py


## License

MIT License - free to use, modify, and distribute.

---

*Solo Project · Week 5 · AI Data Assistant*
