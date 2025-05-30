# rag.py

# === Imports and Setup ===
import os
import re
import sys
import google.generativeai as genai
from typing import List

# Ensure project root is in path for import to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.vectorstore import VectorStore  # Handles semantic search over embedded chunks
from preprocess.chunk import SECTION_ORDER  # Predefined checklist order for procedural logic

# === Gemini API Configuration ===
genai.configure(api_key=os.getenv("API_KEY"))

# === System Prompt for Gemini ===
SYSTEM_PROMPT = (
    "You are an expert on DCS aircraft procedures. "
    "When the user asks for a checklist, return the full checklist step-by-step if possible. "
    "If not possible, ask if they want it step-by-step. Do not summarize unless explicitly asked."
)

# === Format the retrieved chunks into a prompt-friendly string ===
def format_context(chunks: List[dict]) -> str:
    formatted = []
    for c in chunks:
        header = f"[{c['chunk_id']} | {c['section']}]"
        formatted.append(f"{header}\n{c['text']}")
    return "\n\n".join(formatted)

# === Main function to generate the answer ===
def generate_answer(query: str, vectorstore: VectorStore, top_k: int = 3) -> str:
    query_lower = query.strip().lower()

    # === Rule-based overrides for structural questions ===

    # 1. First checklist
    if query_lower in {"what is the first checklist?", "what's the first checklist?"}:
        chunks = vectorstore.get_chunks_by_checklist_number(1)
        return format_context(chunks)

    # 2. Last checklist
    max_number = max(vectorstore.df["checklist_number"])
    if query_lower in {"what is the last checklist?", "what's the last checklist?"}:
        chunks = vectorstore.get_chunks_by_checklist_number(max_number)
        return format_context(chunks)

    # 3. What comes after [section]?
    match = re.match(r"what comes after (.+?)\??$", query_lower)
    if match:
        current_section = match.group(1).replace("-", " ").strip().upper()
        try:
            idx = SECTION_ORDER.index(current_section)
            next_section = SECTION_ORDER[idx + 1]
            chunks = vectorstore.get_chunks_by_section(next_section)
            return format_context(chunks)
        except (ValueError, IndexError):
            return "Sorry, I couldn't find what comes after that section."

    # 4. List all checklists
    if query_lower in {"list all checklists", "show all checklists"}:
        return "Here are all checklists in order:\n\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(SECTION_ORDER))

    # === Default RAG pipeline ===
    retrieved = vectorstore.search(query, top_k=top_k)
    context = format_context(retrieved)

    model = genai.GenerativeModel("gemini-1.5-flash")
    full_prompt = f"{SYSTEM_PROMPT}\n\nQuery: {query}\n\nContext:\n{context}"

    response = model.generate_content([
        {
            "role": "user",
            "parts": [full_prompt]
        }
    ])

    return response.text
