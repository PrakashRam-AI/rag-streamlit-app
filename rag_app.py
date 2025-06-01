import streamlit as st
import pandas as pd
import PyPDF2
import openai
import io

# --- Page Config ---
st.set_page_config(page_title="RAG App", layout="wide")
st.title("📄 Retrieval-Augmented Generation (RAG) App")

# --- User Inputs ---
openai_api_key = st.text_input("🔑 Enter your OpenAI API key:", type="password")

uploaded_file = st.file_uploader("📂 Upload a PDF, TXT, or Excel file", type=["pdf", "txt", "xlsx"])

query = st.text_area("❓ Ask a question about the file:", height=100)

# --- Extract Text from Files ---
def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")
    elif file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
        text = df.to_string(index=False)
    else:
        text = ""
    return text

# --- Generate Response using OpenAI 0.28 syntax ---
def generate_response(text, query, api_key):
    openai.api_key = api_key

    prompt = f"""You are a helpful assistant. Use the following document to answer the question.

    Document:
    {text[:4000]}

    Question:
    {query}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message["content"].strip()

# --- Run RAG Flow ---
if st.button("🧠 Generate Response"):
    if not openai_api_key:
        st.error("Please enter your OpenAI API key.")
    elif not uploaded_file:
        st.error("Please upload a file.")
    elif not query.strip():
        st.error("Please enter a question.")
    else:
        with st.spinner("Reading and analyzing the file..."):
            file_text = extract_text(uploaded_file)
            if not file_text:
                st.error("Failed to extract text from the uploaded file.")
            else:
                response = generate_response(file_text, query, openai_api_key)
                st.success("✅ Response Generated")
                st.markdown("### 📝 Answer:")
                st.write(response)
