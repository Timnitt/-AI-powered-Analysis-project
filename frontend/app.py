import streamlit as st
import requests

st.set_page_config(page_title="AI Data Assistant", layout="centered")
st.title("🧠 AI Data Assistant")

# 1. File Uploading in UI
uploaded_file = st.file_uploader("Upload your data (CSV or Excel)", type=["csv", "xlsx", "xls"])

if uploaded_file:
    query = st.text_input("What would you like to know about this data?")
    
    if st.button("Generate response"):
        if not query:
            st.warning("Please enter a question.")
        else:
            with st.spinner("AI is examining the data..."):
                # Prepare the file and data for the backend
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                data = {"prompt": query}
                
                try:
                    response = requests.post("http://localhost:8000/analyze", files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.subheader("Analysis Results")
                        st.write(result["insight"])
                    else:
                        st.error("The backend couldn't process the request.")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
else:
    st.info("Please upload a file to begin your analysis.")