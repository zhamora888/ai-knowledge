# Phase 4 — Section-Level Retrieval

## Goal

Inject less context, but better context. Instead of loading an entire Markdown file when any keyword matches, split each note into sections by `##` heading and only inject the sections that actually match.

## What Changed

### src/search.py — split_sections()

A new function parses a Markdown file into its constituent sections:

```python
def split_sections(content: str) -> tuple:
    # returns (file_title, [{heading, content}, ...])
```

It walks the file line by line and splits on `##` headings. Each section becomes its own searchable unit with an independent heading and body.

### search_notes() — now returns sections, not files

Before (Phase 3):
```
query: "dependency inversion"
→ solid_principles.md matches → inject entire file (all 5 principles)
```

After (Phase 4):
```
query: "dependency inversion"
→ solid_principles.md > D — Dependency Inversion Principle matches
→ inject that section only
```

The model now receives only what is relevant, not everything that is tangentially related.

### build_context() — updated format

Sections are labelled with their file and heading:
```
--- solid_principles.md > D — Dependency Inversion Principle ---
High-level modules should not depend on low-level modules...
```

The terminal output now shows the same granularity:
```
You: What is dependency inversion?
  [retrieved: solid_principles.md > D — Dependency Inversion Principle]
```

## Why Context Quality Matters

LLMs do not filter their input — they process everything you give them. If you inject five principles when the user only asked about one, the model must decide which parts to use. That increases the chance of:
- Answers that drift toward the wrong section
- Longer, less focused responses
- Wasted context window space

Sending the right 100 tokens beats sending 1000 tokens where 100 are relevant. This is one of the most important practical lessons in building RAG systems.

## The Limits of Keyword Retrieval

Even with section-level precision, keyword matching has structural weaknesses:

| Problem | Example |
|---|---|
| Vocabulary mismatch | User asks "inversion of control", note says "dependency injection" — no match |
| Synonyms | "decoupling" vs "separation" — different words, same concept |
| No ranking | All matches are equal; no sense of which is *most* relevant |
| Fragile on short queries | Single-word queries match too broadly or too narrowly |

Phase 9 replaces keyword search with embeddings — vector representations that capture meaning rather than exact words, solving the vocabulary mismatch problem.

## File Reference

| File | Purpose |
|---|---|
| `src/search.py` | Updated with `split_sections()` and section-level `search_notes()` |
| `src/chat.py` | Retrieval display updated to show `filename > heading` |
