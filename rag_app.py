import streamlit as st
import openai
import PyPDF2
import pandas as pd

st.set_page_config(page_title="RAG App", layout="wide")
st.title("📄🧠 Retrieval-Augmented Generation App")

# API key input
api_key = st.text_input("🔑 Enter your OpenAI API key", type="password")
if not api_key:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()
openai.api_key = api_key

# File uploader
uploaded_files = st.file_uploader("📁 Upload PDF, TXT, or Excel files", type=["pdf", "txt", "xlsx"], accept_multiple_files=True)

# Extract text from files
def extract_text(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        df = pd.read_excel(file)
        return df.to_string(index=False)
    return ""

corpus = ""
if uploaded_files:
    for file in uploaded_files:
        file_text = extract_text(file)
        if file_text:
            corpus += file_text + "\n"

# User query
query = st.text_area("💬 Ask a question based on the uploaded documents")

# Submit and generate response
if st.button("🧠 Generate Response") and query:
    with st.spinner("Generating answer..."):
        prompt = f"""You are an assistant that answers questions based on the following document content:

{corpus}

Question: {query}
Answer:"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            st.success(response.choices[0].message["content"].strip())
        except Exception as e:
            st.error(f"Error: {str(e)}")
