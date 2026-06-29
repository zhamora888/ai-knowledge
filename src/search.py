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


def split_sections(content: str) -> tuple:
    """Return (file_title, list of {heading, content} dicts) for a note."""
    file_title = ""
    sections = []
    current_heading = ""
    current_lines = []

    for line in content.split("\n"):
        if line.startswith("# ") and not line.startswith("## "):
            file_title = line.lstrip("#").strip()
        elif line.startswith("## "):
            if current_lines:
                sections.append({
                    "heading": current_heading,
                    "content": "\n".join(current_lines).strip(),
                })
            current_heading = line.lstrip("#").strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append({
            "heading": current_heading,
            "content": "\n".join(current_lines).strip(),
        })

    return file_title, sections


def search_notes(query: str) -> list:
    """Return matching sections (not whole files) for the given query."""
    keywords = extract_keywords(query)
    if not keywords:
        return []

    matches = []
    for note in load_notes():
        _, sections = split_sections(note["content"])
        for section in sections:
            text = (section["heading"] + " " + section["content"]).lower()
            if any(kw in text for kw in keywords):
                matches.append({
                    "filename": note["filename"],
                    "heading": section["heading"],
                    "content": section["content"],
                })
    return matches


def build_context(matches: list) -> str:
    if not matches:
        return ""
    sections = [
        f"--- {m['filename']} > {m['heading']} ---\n{m['content'].strip()}"
        for m in matches
    ]
    return "\n\n".join(sections)
