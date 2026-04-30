import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure the API client
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.error("Missing GOOGLE_API_KEY in .env file!")


# User Interface Setup
st.set_page_config(page_title="AI Data Assistant", layout="wide")
st.title("📊 AI Data Assistant")

# Simple File Upload in the main page
uploaded_file = st.file_uploader("Upload your CSV to begin", type="csv")

if uploaded_file:
    # Read the data
    df = pd.read_csv(uploaded_file, encoding='latin1')
    
    st.divider()

    # Interaction Area
    user_question = st.text_input(
        "Ask about your data (e.g., 'Show me regional sales' or 'Compare categories'):",
        placeholder="Type your question here..."
    )
    
    generate_btn = st.button("Generate Response")

    if generate_btn:
        if not user_question:
            st.warning("Please enter a question first!")
        else:
            with st.spinner("Analyzing..."):
                try:
                    # Provide Gemini 2.5 with a high-level summary of the dataset
                    data_context = f"""
                    You are a retail data expert. Use these facts from the uploaded file:
                    - Dataset Columns: {', '.join(df.columns.tolist())}
                    - Row Count: {len(df)}
                    - Total Sales: ${df['Sales'].sum():,.2f}
                    - Total Profit: ${df['Profit'].sum():,.2f}
                    - Regions available: {', '.join(df['Region'].unique())}
                    """
                    
                    full_prompt = f"{data_context}\n\nUser Question: {user_question}"
                    
                    response = model.generate_content(full_prompt)
                    
                    #display
                    st.markdown("### 📝 Analysis")
                    st.info(response.text)
                    
                except Exception as e:
                    st.error(f"Analysis Error: {str(e)}")

else:
    st.info("👋 Welcome! Please upload a CSV file above to start analyzing your data.")