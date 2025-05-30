# extract.py

# === Imports ===
import os
import fitz  # PyMuPDF: for reading and extracting text from PDF
import re

# === Extract text from a given page range in a PDF ===
def extract_text_by_page_range(pdf_path, start, end):
    doc = fitz.open(pdf_path)
    return [doc[i].get_text() for i in range(start - 1, end)]

# === Clean extracted text ===
def clean_text(text):
    # Remove header lines like "DCS: Mirage F1 Flight Manual"
    text = re.sub(r'(?i)^DCS: Mirage F1 Flight Manual.*$', '', text, flags=re.MULTILINE)
    # Remove version lines like "Version 1.0"
    text = re.sub(r'(?i)^Version\s+\d+\.\d+.*$', '', text, flags=re.MULTILINE)
    # Remove page numbers (lines that are just numbers)
    text = re.sub(r'^\d{1,4}\s*$', '', text, flags=re.MULTILINE)
    # Normalize spacing
    return re.sub(r'\n{2,}', '\n', text.strip())

# === Split the full chapter text into named sections ===
def split_sections(text, section_titles):
    # Create a pattern to split text based on section title appearance
    pattern = r'(?=^(' + '|'.join(re.escape(title) for title in section_titles) + r')\b)'
    parts = re.split(pattern, text, flags=re.MULTILINE)

    # Combine titles with their body text
    chunks = []
    for i in range(1, len(parts), 2):
        title = parts[i].strip().replace(" ", "_").upper()
        body = parts[i + 1].strip()
        chunks.append((title, body))
    return chunks

# === Save each section into its own .txt file ===
def save_sections(sections, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for title, content in sections:
        filename = f"{output_dir}/{title}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

# === Script entry point ===
if __name__ == "__main__":
    manual_path = "data/manuals/Mirage-F1.pdf"
    output_dir = "data/sections"

    # Define the expected checklist sections (in correct order)
    section_titles = [
        "ENTERING COCKPIT", "CABIN CHECKS", "STARTUP", "AFTER START",
        "BEFORE TAXI", "DURING TAXIING", "BEFORE LINE-UP", "TAKEOFF",
        "CLIMB", "CEILING", "CRUISE", "COMBAT", "DESCENT", "PATTERNS",
        "LANDING", "GO-AROUND", "USE OF THE AUTOPILOT",
        "RETURNING TO PARKING AREA", "AFTER CLEARING THE RUNWAY",
        "ON PARKING AREA"
    ]

    print("Extracting Chapter 4 pages...")
    text_pages = extract_text_by_page_range(manual_path, 143, 155)
    chapter_text = clean_text("\n".join(text_pages))

    print("Splitting into sections...")
    sections = split_sections(chapter_text, section_titles)

    print(f"Saving {len(sections)} sections to {output_dir}/...")
    save_sections(sections, output_dir)

    print("Done.")
