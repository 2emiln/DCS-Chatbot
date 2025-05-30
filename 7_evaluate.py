# evaluate.py

from app.vectorstore import VectorStore
from app.rag import generate_answer

# === Load vector store ===
vs = VectorStore("embeddings/embedded_checklists.parquet")

# === Hardcoded test cases ===
test_cases = [
    {
        "query": "What is the first checklist?",
        "expected_section": "ENTERING COCKPIT"
    },
    {
        "query": "How do I start the Mirage F1?",
        "expected_section": "STARTUP",
        "expected_keywords": ["starter", "throttle", "fuel"]
    },
    {
        "query": "What comes after TAKEOFF?",
        "expected_section": "CLIMB"
    },
    {
        "query": "What is the last checklist?",
        "expected_section": "ON PARKING AREA"
    },
    {
        "query": "List all checklists",
        "expected_keywords": ["ENTERING COCKPIT", "LANDING"]
    }
]

# === Evaluation ===
print("\nRunning chatbot evaluation...\n")

pass_count = 0
for case in test_cases:
    query = case["query"]
    expected_section = case.get("expected_section")
    expected_keywords = case.get("expected_keywords", [])

    answer = generate_answer(query, vs).lower()

    section_match = expected_section is None or expected_section.lower() in answer
    keyword_match = all(k.lower() in answer for k in expected_keywords)
    passed = section_match and keyword_match

    print(f"[{'✓' if passed else '✗'}] Q: {query}")
    if expected_section:
        print(f"    Expected section: {expected_section} — {'✅' if section_match else '❌'}")
    if expected_keywords:
        print(f"    Expected keywords: {expected_keywords} — {'✅' if keyword_match else '❌'}")
    print()

    if passed:
        pass_count += 1

# === Summary ===
total = len(test_cases)
print(f"Evaluation complete: {pass_count}/{total} passed ({(pass_count/total)*100:.1f}%)")
