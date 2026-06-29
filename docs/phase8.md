# Phase 8 — Persistent Knowledge via write_file

## Goal

Close the loop. The knowledge base started as something only you could add to. Now the assistant can extend it — but only when you explicitly instruct it to.

## What Changed

### System prompt — write_file rules

Three rules were added to the system prompt:

```
- Use write_file ONLY when the user explicitly asks you to save, add, or update a note.
  Never write to the knowledge base on your own initiative.
  When writing, produce well-structured Markdown with a clear title and ## sections.
```

That's the entire Phase 8 code change. The `write_file` tool was already wired up in Phase 7. This phase is about constraining *when* it gets used, not adding new capability.

## How It Works

When you say something like:
```
Save a note about the Facade pattern with a practical example.
```

The model calls:
```python
write_file("facade_pattern.md", "# Facade Pattern\n\n## Intent\n...")
```

Your app writes the file to `knowledge/`. On the next question, `search_notes` and `read_file` will find it — the new knowledge is immediately available.

The loop is now closed:
```
You add notes manually       → knowledge/ → retrieved by search
Assistant saves notes        → knowledge/ → retrieved by search (same pipeline)
```

## The Human-in-the-Loop Principle

The model only writes when explicitly instructed. This is intentional and important.

A model that saves autonomously introduces two risks:

**Accuracy risk** — The model can be wrong. If it saves a flawed explanation and that file gets retrieved in a future answer, the error compounds. Bad knowledge is worse than no knowledge because it actively misleads.

**Duplication/drift risk** — Without curation, the knowledge base fills with overlapping, inconsistent notes. Retrieval quality degrades as the signal-to-noise ratio drops.

The rule "only write when asked" keeps a human in the loop as the quality gate. You decide what is worth saving. The model decides how to format and write it.

This is not a limitation of Phase 8 — it is the correct design for this stage of the system.

## The Deeper Problem

Your instinct to ask "which knowledge deserves to be saved?" is the right question. It is genuinely unsolved in production RAG systems. Current approaches include:

| Approach | What it does |
|---|---|
| Human approval | User reviews before writing (what we do) |
| Deduplication check | Compare against existing notes before saving |
| Confidence threshold | Only save if the model's certainty is high enough |
| Separate curator agent | A second model reviews proposed knowledge before it's committed |

Phase 9 (embeddings) makes deduplication more tractable — you can check semantic similarity before writing, not just filename matching.

## What to Try

```
Save a note about the Repository pattern — what it is, when to use it, and a short example.
```

Then verify it was created:
```
What do my notes say about the Repository pattern?
```

The model should call `search_notes` or `read_file` and find the note it just wrote.

## File Reference

| File | Purpose |
|---|---|
| `src/chat.py` | System prompt updated with write_file usage rules |
| `src/tools.py` | `write_file()` implementation (unchanged from Phase 7) |
| `knowledge/` | Where new notes land — immediately searchable after creation |
