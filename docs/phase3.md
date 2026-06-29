# Phase 3 — Knowledge Base with Keyword Retrieval

## Goal

Give the assistant access to your own notes. When you ask a question, the app finds relevant Markdown files and injects their content into the prompt before calling the model. This is the simplest form of RAG (Retrieval-Augmented Generation).

## What We Built

### knowledge/ folder
Three Markdown files the assistant can draw from:
- `software_architecture.md` — layered, hexagonal, microservices, event-driven, CQRS
- `design_patterns.md` — creational, structural, behavioural patterns
- `solid_principles.md` — SRP, OCP, LSP, ISP, DIP

You can add any `.md` file here and it becomes part of the knowledge base immediately.

### src/search.py
A retrieval module with four responsibilities:

| Function | What it does |
|---|---|
| `load_notes()` | Reads all `.md` files from `knowledge/` into memory |
| `extract_keywords(query)` | Tokenises the query, strips stop words and punctuation |
| `search_notes(query)` | Returns notes whose content contains any keyword |
| `build_context(matches)` | Formats matched notes into a single string for injection |

### src/chat.py — build_prompt()
A new function sits between the user's input and the Ollama call:

```python
def build_prompt(user_input: str) -> str:
    matches = search_notes(user_input)
    if not matches:
        return user_input

    context = build_context(matches)
    return (
        f"[Relevant notes from knowledge base]\n\n"
        f"{context}\n\n"
        f"[Question]\n{user_input}"
    )
```

When notes are found, the user message sent to the model looks like this:

```
[Relevant notes from knowledge base]

--- solid_principles.md ---
# SOLID Principles
...full note content...

--- design_patterns.md ---
# Design Patterns
...full note content...

[Question]
What is the Dependency Inversion Principle?
```

The model never receives the raw user input alone — it receives the input *plus* your notes as context.

## How Retrieval Works

```
User types: "What is the Dependency Inversion Principle?"
         ↓
extract_keywords() → {"dependency", "inversion", "principle"}  (stop words removed)
         ↓
search_notes()     → scans all notes for any keyword match
                   → solid_principles.md matches ("Dependency Inversion Principle")
         ↓
build_context()    → formats matched notes into a string
         ↓
build_prompt()     → prepends context to user question
         ↓
call_ollama()      → model answers using your notes as grounding
```

The terminal shows which files were retrieved on each turn:
```
You: What is the Dependency Inversion Principle?
  [retrieved: solid_principles.md]
```

## The Key Insight: Context Is Engineered, Not Automatic

The model does not search your notes. Your application does. The model only sees what you put in the prompt. This means:

- **You control what the model knows** — inject the right notes and it answers well; inject nothing and it falls back to training data only
- **Context quality is everything** — a model given accurate, relevant notes will outperform the same model given nothing, regardless of model size
- **The retrieval step is a first-class concern** — in production RAG systems, most engineering effort goes into making retrieval better, not making the model bigger

## Limitations (What Phase 4 Will Fix)

Right now, if a note matches, the *entire* file is injected. Ask about "patterns" and the full `design_patterns.md` goes into the prompt — even sections that aren't relevant.

This wastes context window space and can confuse the model with irrelevant content. Phase 4 improves retrieval by selecting only the *sections* of a note that match, rather than the whole file.

## File Reference

| File | Purpose |
|---|---|
| `src/search.py` | Keyword extraction, note loading, context formatting |
| `src/chat.py` | Updated with `build_prompt()` — retrieves and injects context |
| `knowledge/*.md` | Your knowledge base — add any Markdown file to extend it |
