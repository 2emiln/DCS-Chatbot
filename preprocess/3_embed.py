# embed.py

# === Imports ===
import os
import polars as pl  # For saving the output embeddings
from tqdm import tqdm  # For progress bar
from google import generativeai as genai  # Gemini API
from typing import List

# === Configure API key ===
genai.configure(api_key=os.getenv("API_KEY"))

# === Load all text chunks from previous step ===
def load_chunks(input_parquet: str) -> List[dict]:
    df = pl.read_parquet(input_parquet)
    return df.to_dicts()

# === Embed each chunk's text using Gemini embeddings ===
def embed_chunks(chunks: List[dict], model: str = "models/embedding-001") -> List[dict]:
    embedded = []
    for chunk in tqdm(chunks, desc="Embedding chunks"):
        response = genai.embed_content(
            model=model,
            content=chunk["text"],
            task_type="SEMANTIC_SIMILARITY"
        )
        chunk["embedding"] = response["embedding"]
        embedded.append(chunk)
    return embedded

# === Save all embedded chunks to .parquet ===
def save_to_parquet(chunks: List[dict], output_path: str) -> None:
    df = pl.DataFrame(chunks)
    df.write_parquet(output_path)
    print(f"Saved {len(chunks)} embedded chunks to {output_path}")

# === Script entry point ===
if __name__ == "__main__":
    input_path = "data/chunks/checklists_chunked.parquet"  # Input: raw checklist chunks
    output_path = "embeddings/embedded_checklists.parquet"  # Output: with embeddings

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    chunks = load_chunks(input_path)
    embedded = embed_chunks(chunks)
    save_to_parquet(embedded, output_path)
