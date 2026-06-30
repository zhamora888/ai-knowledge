# Phase 9 — Embeddings and a Vector Database

## Goal

Replace keyword retrieval with semantic search. Instead of matching exact words, represent text as vectors and find the closest meaning, not just the closest spelling. This is what "production-grade RAG" actually means.

We built the vector store ourselves rather than using a library like ChromaDB — the same philosophy as every phase before this: no black boxes, see every moving part.

## What Changed

### src/embeddings.py (new)

Two functions, nothing else:

```python
def embed(text: str) -> list:
    # calls Ollama's /api/embed endpoint, returns a 768-number vector

def cosine_similarity(a: list, b: list) -> float:
    # measures the angle between two vectors — 1.0 = identical meaning, 0 = unrelated
```

We use `nomic-embed-text`, a dedicated embedding model (not an LLM — it doesn't generate text, it only converts text into vectors). It's ~274MB, much lighter than even `llama3.2:1b`.

### src/vector_index.py (new)

The "vector database," built from plain Python and JSON:

| Function | What it does |
|---|---|
| `build_index()` | Splits every note into sections (reusing Phase 4's `split_sections`), embeds each section, saves everything to `memory/vector_index.json` |
| `load_index()` | Loads the saved index, or builds it if missing |
| `semantic_search(query, top_k=3)` | Embeds the query, computes cosine similarity against every indexed section, returns the closest matches |

The index file looks like this:
```json
[
  {
    "filename": "solid_principles.md",
    "heading": "D — Dependency Inversion Principle",
    "content": "High-level modules should not depend...",
    "embedding": [0.0463, 0.0358, -0.1693, ...]
  }
]
```

768 numbers per section, one entry per section across the whole knowledge base.

### tools.py — search_notes now uses embeddings

`search_notes_tool()` now calls `vector_index.semantic_search()` instead of the Phase 4 keyword matcher. `write_file()` now rebuilds the index automatically after saving a new note, so anything the assistant writes (Phase 8) becomes semantically searchable immediately.

### chat.py — --reindex flag

```
py src/chat.py --reindex
```
Forces a full rebuild of the vector index — useful after manually editing files in `knowledge/`.

## How Semantic Search Works

```
"What pattern should I use for multiple payment providers?"
         ↓
embed() → [0.021, -0.087, 0.143, ...]   (768 numbers representing meaning)
         ↓
compare against every section's embedding using cosine_similarity()
         ↓
0.632  solid_principles.md > D — Dependency Inversion Principle
0.590  design_patterns.md > Structural Patterns
0.578  design_patterns.md > When to Apply Patterns
         ↓
top 3 returned, ranked by similarity score
```

Notice the top result: the query never says "dependency inversion," but the SOLID notes happen to use a `PaymentGateway` example under that exact heading. The embedding model captured that **meaning** connects "payment providers" to "PaymentGateway," even though the words don't match.

## Why This Beats Keyword Search

Recall Phase 4's documented limitation:

| Problem | Keyword search (Phase 3-8) | Semantic search (Phase 9) |
|---|---|---|
| Vocabulary mismatch | "inversion of control" ≠ "dependency injection" | Recognizes they're related concepts |
| Synonyms | "decoupling" ≠ "separation" | Captures shared meaning |
| Ranking | No ranking — every match is equal | Cosine similarity gives a real relevance score |
| Short queries | Fragile — too broad or too narrow | More stable — meaning is preserved regardless of phrasing |

Every result now comes with a similarity score (0 to 1), visible in the retrieved context: `(similarity: 0.632)`. This makes retrieval quality observable instead of binary match/no-match.

## What a Vector Database Actually Does

Every concept here — embed, store, compare, rank — is exactly what a real vector database (Pinecone, ChromaDB, Weaviate, pgvector) does internally. The difference is purely engineering at scale:

- They use approximate nearest-neighbor algorithms (HNSW, IVF) instead of comparing against every vector — necessary once you have millions of entries, not 20
- They persist to disk efficiently and support concurrent reads/writes
- They handle filtering, metadata queries, and incremental updates without a full rebuild

The underlying math — cosine similarity between embeddings — is identical. You now know what's happening beneath the abstraction.

## Limitations

- `build_index()` re-embeds everything on every call — fine for 20 sections, would be slow for thousands. A real vector DB only re-embeds what changed.
- Comparing against every vector (linear scan) doesn't scale past a few thousand entries — real vector DBs use indexing structures to avoid this.
- No persistence optimization — we're writing the whole JSON file each time.

These are exactly the problems real vector databases solve. Now that you've built the simple version, you'd recognize immediately what a production vector DB is optimizing for.

## What to Try

```
py src/chat.py --reindex
```

Then ask something where the phrasing deliberately avoids your notes' exact vocabulary:
```
How do I keep my code testable when swapping out external services?
```
This should surface SOLID's Dependency Inversion Principle and the Adapter pattern — neither of which mention "testable" or "swapping" directly.

## File Reference

| File | Purpose |
|---|---|
| `src/embeddings.py` | `embed()` and `cosine_similarity()` |
| `src/vector_index.py` | Build/load the index, run semantic search |
| `src/tools.py` | `search_notes_tool()` now uses semantic search; `write_file()` reindexes |
| `src/chat.py` | `--reindex` flag |
| `memory/vector_index.json` | The vector index (gitignored — regenerable via `--reindex`) |
