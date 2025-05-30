# main.py

# === Imports for setting up local module paths ===
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Enable imports from local app/

# === Streamlit UI and RAG backend ===
import streamlit as st
from app.vectorstore import VectorStore  # Custom search engine for embedded checklist chunks
from app.rag import generate_answer     # Main logic to answer user questions using Gemini

# === Streamlit App Configuration ===
st.set_page_config(page_title="Mirage F1 Chatbot")
st.title("Mirage F1 Procedure Assistant")

# === User Input Field ===
query = st.text_input("Ask a question about the Mirage F1:")

# === Answer Generation ===
if query:
    # Load previously embedded chunks
    vs = VectorStore("embeddings/embedded_checklists.parquet")

    # Generate answer from user query
    answer = generate_answer(query, vs)

    # Display the result in markdown format
    st.markdown(answer)
