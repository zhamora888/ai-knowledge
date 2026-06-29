from pathlib import Path

KNOWLEDGE_DIR = Path("knowledge")

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "to", "of", "in", "on", "at", "by",
    "for", "with", "about", "from", "into", "through", "and", "or", "but",
    "if", "as", "it", "its", "this", "that", "these", "those", "i", "you",
    "he", "she", "we", "they", "what", "which", "who", "me", "him", "her",
    "us", "them", "not", "so", "up", "out", "no", "just", "then", "than",
    "how", "all", "also", "very", "when", "where", "there", "here",
}


def load_notes() -> list:
    notes = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        notes.append({
            "filename": path.name,
            "content": path.read_text(encoding="utf-8"),
        })
    return notes


def extract_keywords(query: str) -> set:
    words = query.lower().split()
    return {
        w.strip(".,?!:;\"'()")
        for w in words
        if w.strip(".,?!:;\"'()") not in STOP_WORDS and len(w) > 2
    }


def search_notes(query: str) -> list:
    keywords = extract_keywords(query)
    if not keywords:
        return []

    matches = []
    for note in load_notes():
        text = (note["filename"] + " " + note["content"]).lower()
        if any(kw in text for kw in keywords):
            matches.append(note)
    return matches


def build_context(matches: list) -> str:
    if not matches:
        return ""
    sections = [
        f"--- {note['filename']} ---\n{note['content'].strip()}"
        for note in matches
    ]
    return "\n\n".join(sections)
