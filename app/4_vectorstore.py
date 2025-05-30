# vectorstore.py

# === Imports ===
import os
import polars as pl  # For fast DataFrame handling
import google.generativeai as genai  # For Gemini embedding API
import numpy as np  # For cosine similarity math
from typing import List, Dict

# === Gemini API Configuration ===
genai.configure(api_key=os.getenv("API_KEY"))

# === Main VectorStore Class ===
class VectorStore:
    def __init__(self, parquet_path: str):
        # Load all embedded chunks from .parquet
        self.df = pl.read_parquet(parquet_path)
        # Convert list-of-lists to NumPy array for similarity
        self.embeddings = np.array(self.df["embedding"].to_list())

    # === Embed a query into the same space as the chunks ===
    def embed_query(self, query: str, model: str = "models/embedding-001") -> List[float]:
        response = genai.embed_content(
            model=model,
            content=query,
            task_type="SEMANTIC_SIMILARITY"
        )
        return response["embedding"]

    # === Find top-k chunks most similar to the query ===
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        query_vector = np.array(self.embed_query(query))
        scores = self.embeddings @ query_vector / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_vector) + 1e-9
        )
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [
            {
                "chunk_id": self.df["chunk_id"][int(i)],
                "section": self.df["section"][int(i)],
                "score": float(scores[i]),
                "text": self.df["text"][int(i)],
                "checklist_number": self.df["checklist_number"][int(i)],
            }
            for i in top_indices
        ]

    # === Retrieve all chunks from a specific checklist number ===
    def get_chunks_by_checklist_number(self, number: int) -> List[Dict]:
        filtered = self.df.filter(pl.col("checklist_number") == number)
        return [
            {
                "chunk_id": row["chunk_id"],
                "section": row["section"],
                "text": row["text"],
                "checklist_number": row["checklist_number"]
            }
            for row in filtered.iter_rows(named=True)
        ]

    # === Retrieve all chunks from a specific section name ===
    def get_chunks_by_section(self, section: str) -> List[Dict]:
        filtered = self.df.filter(pl.col("section") == section)
        return [
            {
                "chunk_id": row["chunk_id"],
                "section": row["section"],
                "text": row["text"],
                "checklist_number": row["checklist_number"]
            }
            for row in filtered.iter_rows(named=True)
        ]
