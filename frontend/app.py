import base64
import os
from io import BytesIO

import requests
import streamlit as st
from docx import Document
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
MAX_FILE_SIZE_MB = 200


# Page configuration
st.set_page_config(page_title="AI Data Assistant", page_icon="📊", layout="wide")

# Style the app with custom CSS
st.markdown(
    """
<style>
    [data-testid="stAppViewContainer"]
        { background-color: #F0F2F6; }
    .stAppDeployButton { 
        display: none; }
    header { 
        visibility: hidden; }
    [data-testid="stSidebar"] 
        { background-color: #2E7BCF; color: #ffffff; }
    [data-testid="stSidebar"] 
    [data-testid="stImage"] { display: block; margin-left: auto; margin-right: auto; }
    [data-testid="stSidebar"] .stMarkdown { text-align: center; }
    [data-testid="stWidgetLabel"] p { color: white; font-weight: bold; }
    [data-testid="stFileUploaderDropzone"] button {
        text-indent: -9999px; line-height: 0; background-color: #2E7BCF;
        color: #ffffff; border: none; padding: 13px 20px; border-radius: 5px;
        }
    [data-testid="stFileUploaderDropzone"] button::after { content: "Upload File"; text-indent: 0; line-height: initial; display: block; }

   .stDownloadButton > button {
        width: 100%;
        border-radius: 8px;
        color: #ffffff;
        background-color: #4CAF50; /* Modern Green */
        border: none;
        padding: 0.6rem;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    .stDownloadButton > button:hover {
        background-color: #45a049;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-1px);
        color: #ffffff;
    }
    .stChatMessage {
        border: 2px solid #cbd5e1 !important; 
        border-radius: 8px !important;
        background-color: #ffffff !important;
        color: #1e293b !important; }
    .stChatMessage.user { background-color: #DCF8C6; align-self: flex-end; }
    .stChatMessage.assistant { background-color: #ffffff; align-self: flex-start; }
        
    [data-testid="stChatInput"] > div {
        border: 1px solid #1E6091 !important; /* Forces your blue color */
        border-radius: 20px !important;
        padding-left: 10px !important;
        height: 60px;
        background-color: white !important;
    }

    [data-testid="stChatInput"] div[role="textbox"] {
        border: none !important;
        box-shadow: none !important;
    }

    [data-testid="stChatInput"] :focus-within {
        border-color: #1E6091 !important;
        box-shadow: none !important;
        outline: none !important;
        border: none !important;
    }

    [data-testid="stChatInput"] textarea {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    [data-testid="stChatInput"] button {
        right: 10px !important;
        background-color: transparent !important;
        align-self: center !important;
    }
    /* 4. Improve overall font and spacing */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #1E1E1E;
    }
    </style>""",
    unsafe_allow_html=True,
)


# --- Helper Function for Word Export ---
def generate_docx(messages):
    doc = Document()
    doc.add_heading("AI Data Analysis Report", 0)

    for msg in messages:
        role = "User" if msg["role"] == "user" else "AI Assistant"
        p = doc.add_paragraph()
        p.add_run(f"{role}: ").bold = True
        p.add_run(msg["content"])

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


# --- SIDEBAR ---
with st.sidebar:
    st.image("logo.png", width=120)
    st.markdown("Your AI Data Assistant")
    st.markdown("---")
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file", type=["csv", "xlsx", "xls"]
    )
    st.caption(f"Max file size: {MAX_FILE_SIZE_MB}MB")

if "messages" in st.session_state and st.session_state.messages:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Export Results")

    docx_file = generate_docx(st.session_state.messages)

    st.sidebar.download_button(
        label="📄 Download Report (.docx)",
        data=docx_file,
        file_name="analysis_report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )
    st.markdown("---")

# --- MAIN PAGE ---
st.title(" 📊 AI Data Assistant")
st.markdown("##### *Transforming raw data into deterministic business insights.*")

# --- CHAT INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("chart"):
            st.image(base64.b64decode(message["chart"]))

if prompt := st.chat_input("Ask about your data..."):
    if uploaded_file is None:
        st.error("Please upload a CSV or Excel file first.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Analyzing..."):
            history_context = "\n".join(
                [f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]]
            )
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            data = {"prompt": prompt, "history": history_context}

            try:
                response = requests.post(
                    f"{BACKEND_URL}/analyze", files=files, data=data
                )
                if response.status_code == 200:
                    resp_data = response.json()
                    insight = resp_data["insight"]
                    chart_b64 = resp_data.get("chart")
                    with st.chat_message("assistant"):
                        st.markdown(insight)
                        if chart_b64:
                            st.image(base64.b64decode(chart_b64))
                    msg = {"role": "assistant", "content": insight}
                    if chart_b64:
                        msg["chart"] = chart_b64
                    st.session_state.messages.append(msg)
                else:
                    st.error(f"Backend Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
else:
    st.markdown("""
    ### Hi 👋 , Welcome to your AI Data Assistant.
    1. **Upload** your File using the sidebar on the left.
    2. **Chat** with the AI to get deterministic insights.
    """)
