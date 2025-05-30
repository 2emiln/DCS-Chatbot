# Mirage F1 RAG Chatbot

This project is a Retrieval-Augmented Generation (RAG) chatbot for answering questions about the Mirage F1 flight manual, specifically Chapter 4: Checklists and Procedures.

It uses the Gemini API to semantically embed and retrieve information from the manual, and answer questions via a Streamlit web app.

---

## Features

* Full pipeline: extract → chunk → embed → search → generate
* Structured checklist support ("What is the first checklist?")
* Semantic fallback using Gemini 1.5 Flash
* Evaluation script to measure chatbot accuracy

---

## How to Run

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Add your API key

Create a file named `.env` in the root folder:

```
API_KEY=your-gemini-api-key-here
```

Use the `.env.example` file as a template.

### 3. Launch the chatbot

```
streamlit run 6_main.py
```

### 4. Run evaluation (optional)

```
python 7_evaluate.py
```

---

## Project Structure

```text
DCS-Chatbot/
├── app/
│   ├── 4_vectorstore.py     # Vector search over embedded chunks
│   └── 5_rag.py             # Main generate_answer() logic
├── preprocess/
│   ├── 1_extract.py         # Extract and clean Chapter 4
│   ├── 2_chunk.py           # Chunk sections into step-by-step format
│   └── 3_embed.py           # Embed chunks with Gemini
├── data/
│   ├── manuals/             # Contains Mirage-F1.pdf
│   ├── sections/            # Cleaned .txt files by section
│   └── chunks/              # Parquet + .txt of chunked steps
├── embeddings/
│   └── embedded_checklists.parquet
├── 6_main.py                # Streamlit chatbot interface
├── 7_evaluate.py            # Test accuracy of chatbot responses
├── .env.example             # Template for your API key
├── requirements.txt         # All needed libraries
└── README.md
```

---

## Evaluation

Run `7_evaluate.py` to:

* Test rule-based questions (e.g. "What is the first checklist?")
* Test semantic understanding (e.g. "How do I start the Mirage F1?")
* Check keyword presence and section accuracy

Results are printed to console with pass/fail markers.

---

## API Key Notice

This project uses Google Gemini. You must create your own API key at:
[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

Your API key should go in a `.env` file:

```
API_KEY=your-key-here
```

Never commit this file. Use `.env.example` as a template.

---

## Done

You are now ready to extract, chunk, embed, evaluate and chat with the Mirage F1 manual.

---

Created by Emil Nilsson.
