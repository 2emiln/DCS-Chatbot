# chunk.py

# === Imports ===
import os
import glob
import re
import polars as pl
from typing import List, Dict
from tqdm import tqdm

# === Predefined order of all checklist sections ===
SECTION_ORDER = [
    "ENTERING COCKPIT", "CABIN CHECKS", "STARTUP", "AFTER START",
    "BEFORE TAXI", "DURING TAXIING", "BEFORE LINE-UP", "TAKEOFF",
    "CLIMB", "CEILING", "CRUISE", "COMBAT", "DESCENT", "PATTERNS",
    "LANDING", "GO-AROUND", "USE OF THE AUTOPILOT",
    "RETURNING TO PARKING AREA", "AFTER CLEARING THE RUNWAY",
    "ON PARKING AREA"
]

# === Split a section's text into smaller step-based chunks ===
def chunk_checklist(text: str, section: str, source: str, checklist_number: int, max_steps: int = 10) -> List[Dict]:
    # Detect steps like "1. Turn on the battery"
    pattern = re.compile(r'(?=^\d{1,3}[\.\\)]?\s)', re.MULTILINE)
    parts = pattern.split(text)
    parts = [p.strip() for p in parts if p.strip()]

    chunks: List[Dict] = []
    for i in range(0, len(parts), max_steps):
        sub_steps = parts[i:i + max_steps]
        chunk_text = "\n\n".join(sub_steps)
        chunk_index = i // max_steps + 1
        chunk_id = f"{section}_{chunk_index}"

        chunk = {
            "chunk_id": chunk_id,
            "section": section,
            "source": source,
            "checklist_number": checklist_number,
            "start_step": i + 1,
            "end_step": i + len(sub_steps),
            "text": chunk_text,
        }
        chunks.append(chunk)

    return chunks

# === Main chunking function: loads all .txt sections and processes them ===
def chunk_all_sections(input_folder: str, output_path: str) -> None:
    txt_files = sorted(glob.glob(f"{input_folder}/*.txt"))
    all_chunks: List[Dict] = []

    for path in tqdm(txt_files, desc="Chunking checklists"):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        raw_section = os.path.splitext(os.path.basename(path))[0]
        section = raw_section.replace("_", " ").upper()
        source = os.path.basename(path)
        checklist_number = SECTION_ORDER.index(section) + 1  # 1-based

        chunks = chunk_checklist(text, section, source, checklist_number)
        all_chunks.extend(chunks)

    # Save to .parquet
    df = pl.DataFrame(all_chunks)
    df.write_parquet(output_path)
    print(f"Saved {len(all_chunks)} checklist chunks to {output_path}")

    # === Optional: also save a readable .txt version ===
    txt_output_path = output_path.replace(".parquet", ".txt")
    with open(txt_output_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(f"[{chunk['chunk_id']} | {chunk['section']} | steps {chunk['start_step']}-{chunk['end_step']}]\n")
            f.write(chunk["text"])
            f.write("\n\n" + "=" * 60 + "\n\n")

# === Entry point ===
if __name__ == "__main__":
    input_folder = "data/sections"
    output_path = "data/chunks/checklists_chunked.parquet"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    chunk_all_sections(input_folder, output_path)
