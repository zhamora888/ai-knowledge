# Local AI Knowledge Assistant

A Software Architecture Assistant built on a local LLM (Ollama), built in nine incremental phases to learn LLM application architecture from first principles — no frameworks, no black boxes.

It retrieves relevant knowledge semantically, calls tools to read and search its own notes, critiques its own answers via an independent reviewer pass, and can persist new knowledge back into its knowledge base when explicitly instructed.

See [docs/summary.md](docs/summary.md) for the full write-up of what was built and what it taught.

## Requirements

- [Ollama](https://ollama.com/download) installed and running
- Python 3.8+

## Setup

Pull the models:
```
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

Install dependencies:
```
pip install -r requirements.txt
```

## Usage

```
python src/chat.py
```

Flags:
| Flag | Effect |
|---|---|
| `--reset` | Clear conversation memory and start fresh |
| `--reindex` | Rebuild the vector index from everything in `knowledge/` |

Type `quit`, `exit`, or `q` to end a session.

## Project Structure

```
knowledge/   Markdown notes — the assistant's domain knowledge
memory/      Conversation history and vector index (gitignored, regenerated locally)
src/
  chat.py          Main loop — system prompt, agentic loop, architect/reviewer flow
  search.py        Markdown loading and section splitting
  embeddings.py     Ollama embedding calls and cosine similarity
  vector_index.py   Build/load the vector index, semantic search
  tools.py          Tool definitions and execution (list_documents, read_file, search_notes, write_file)
docs/        One write-up per phase, plus docs/summary.md
```

## How It Works

Every conversation turn:
1. Your message is added to the conversation history (`messages` — see [docs/phase1.md](docs/phase1.md), [docs/phase2.md](docs/phase2.md))
2. The Architect runs an agentic loop, calling tools as needed to search or read the knowledge base ([docs/phase7.md](docs/phase7.md), [docs/phase9.md](docs/phase9.md))
3. A Reviewer independently critiques the Architect's answer ([docs/phase6.md](docs/phase6.md))
4. Both are shown to you and saved to memory

Knowledge retrieval is semantic, not keyword-based — notes are split into sections, embedded with `nomic-embed-text`, and matched against your query by cosine similarity ([docs/phase9.md](docs/phase9.md)).

## Phase-by-Phase Docs

| Phase | Topic |
|---|---|
| [1](docs/phase1.md) | Basic chat loop with Ollama |
| [2](docs/phase2.md) | Persistent conversation memory |
| [3](docs/phase3.md) | Knowledge base with keyword retrieval |
| [4](docs/phase4.md) | Section-level retrieval |
| [5](docs/phase5.md) | Software Architecture Assistant role |
| [6](docs/phase6.md) | Reviewer pass |
| [7](docs/phase7.md) | Tool calling |
| [8](docs/phase8.md) | Persisting new knowledge |
| [9](docs/phase9.md) | Embeddings and a hand-built vector database |

## What's Not Built

This is a learning project, not a production system. Deliberately left out: input validation on tool arguments, a systematic evaluation harness, real observability/logging, and approximate nearest-neighbor indexing (the vector index does a linear scan, fine at this scale, not at production scale). See [docs/summary.md](docs/summary.md#whats-deliberately-not-built) for the full list.
