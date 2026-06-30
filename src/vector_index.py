import json
from pathlib import Path

from search import load_notes, split_sections
from embeddings import embed, cosine_similarity

INDEX_FILE = Path("memory/vector_index.json")


def build_index() -> list:
    """Embed every section of every note and save the index to disk."""
    index = []
    for note in load_notes():
        _, sections = split_sections(note["content"])
        for section in sections:
            text = f"{section['heading']}\n{section['content']}"
            vector = embed(text)
            index.append({
                "filename": note["filename"],
                "heading": section["heading"],
                "content": section["content"],
                "embedding": vector,
            })

    INDEX_FILE.write_text(json.dumps(index), encoding="utf-8")
    return index


def load_index() -> list:
    if INDEX_FILE.exists():
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    return build_index()


def semantic_search(query: str, top_k: int = 3) -> list:
    """Return the top_k sections most semantically similar to the query."""
    index = load_index()
    if not index:
        return []

    query_vector = embed(query)

    scored = [
        (cosine_similarity(query_vector, entry["embedding"]), entry)
        for entry in index
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)

    return [
        {**entry, "score": round(score, 3)}
        for score, entry in scored[:top_k]
    ]


def build_context(matches: list) -> str:
    if not matches:
        return ""
    sections = [
        f"--- {m['filename']} > {m['heading']} (similarity: {m['score']}) ---\n{m['content'].strip()}"
        for m in matches
    ]
    return "\n\n".join(sections)
