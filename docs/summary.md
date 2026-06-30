# Project Summary

## What This Is

A local AI assistant built incrementally with Ollama, with no frameworks, to understand LLM application architecture from first principles. Every phase added one concept, in isolation, so the mechanism behind it stayed visible instead of being hidden behind a library.

Final result: a Software Architecture Assistant that retrieves relevant knowledge semantically, calls tools to fetch and persist information, critiques its own answers via a second independent pass, and can extend its own knowledge base when explicitly instructed to.

## The Nine Phases

| Phase | Built | Core Concept |
|---|---|---|
| [1](phase1.md) | Basic chat loop (`src/chat.py`) | The model is stateless. `messages` is just a Python list sent in full on every call. |
| [2](phase2.md) | JSON persistence (`load_messages`/`save_messages`) | Memory belongs to the application, not the model. |
| [3](phase3.md) | Knowledge base + keyword retrieval (`src/search.py`) | Basic RAG — inject relevant notes into the prompt before calling the model. |
| [4](phase4.md) | Section-level retrieval (`split_sections`) | Context quality matters more than context quantity. |
| [5](phase5.md) | Software Architecture Assistant role | The system prompt is the primary lever for shaping model behaviour. |
| [6](phase6.md) | Reviewer pass (`run_reviewer`) | Same model, different prompt, different role — multi-agent via orchestration, not separate models. |
| [7](phase7.md) | Tool calling (`src/tools.py`, `run_agent`) | The model requests actions; the application decides what's allowed and executes them. |
| [8](phase8.md) | `write_file` with explicit-instruction guardrail | The assistant can extend its own knowledge — but only with a human in the loop as the quality gate. |
| [9](phase9.md) | Embeddings + hand-built vector index (`src/embeddings.py`, `src/vector_index.py`) | Meaning can be represented as geometry. Semantic search beats keyword matching by comparing vectors, not exact words. |

## What Actually Works

- Ollama (`llama3.2:1b`) for chat and tool calling, `nomic-embed-text` for embeddings — both used as pretrained, untouched models
- Conversation memory survives restarts (`memory/conversation.json`, gitignored)
- Semantic retrieval over `knowledge/*.md`, ranked by cosine similarity, rebuilt automatically when new notes are written
- A working agentic loop: the model can call `list_documents`, `read_file`, `search_notes`, and `write_file`, and the application executes exactly what's requested — nothing more
- An Architect/Reviewer pattern: every answer gets a second, independent critique pass

## Key Realizations Along the Way

**Everything is inference.** Memory, tool use, multi-agent behaviour, reasoning — none of it is the model doing something special. It's the same `call_ollama()` function, called repeatedly with different inputs. What looks like capability is really input engineering: shaping the prompt, context, and role to make the desired output more probable.

**Deterministic orchestration vs. probabilistic inference.** Your code controls what happens — what gets retrieved, what tools exist, what order things run in, what's allowed to execute. The model controls what it outputs, and that part is never guaranteed, no matter how good the input is. This is the line named in the original project plan, and it's the central tension in every agentic system.

**RAG vs. fine-tuning.** Specializing a general-purpose model doesn't require retraining it. Keep the weights frozen, inject domain knowledge at inference time through retrieval. Cheap, instant to update, fully auditable — at the cost of being bounded by what fits in context and by the base model's reasoning ability.

**Embeddings are distributional semantics, operationalized.** Converting words to vectors that capture meaning, then matching via geometry (cosine similarity) instead of exact text, traces back to the same statistical idea behind classical NLP (e.g. SMT alignment models) — refined through word2vec into dense, trainable vector spaces. The math at query time is trivial; the hard part was training the embedding model, which here was rented (pretrained), not built.

**No guarantee, ever.** A perfectly curated knowledge base and accurate retrieval do not guarantee a correct answer, because generation is still sampling from a probability distribution. We watched this directly — the model echoing notes verbatim instead of synthesizing them, fabricating fake tool-call JSON instead of using the real protocol, and drifting into hallucinated "phases" once conversation history got too cluttered. Mitigations (bigger models, the Reviewer pass, lower temperature, citation verification, human review) reduce the error rate. None eliminate it.

**AI engineering is software engineering, plus a new kind of untrusted input.** The architecture, scaling, and concepts in this project are the same shape used in production systems — only the model size and knowledge base size differ. What separates a pet project from a production system isn't the architecture; it's the engineering discipline wrapped around the probabilistic component: validating tool arguments instead of trusting them blindly, systematic evaluation instead of eyeballing output, real observability instead of `print()` statements, and graceful handling of malformed or unexpected model output.

## What's Deliberately Not Built

This project stayed a learning tool, not a production system. Left out on purpose:

- **Input validation** on tool arguments — `tools.execute()` trusts whatever the model sends
- **Evaluation harness** — no test set of known-correct answers to measure retrieval or answer quality systematically
- **Real observability** — `print()` statements instead of structured logging/tracing
- **Approximate nearest-neighbor indexing** — `vector_index.py` does a linear scan over every embedding; fine for ~20 sections, would not scale to a real corpus
- **Incremental indexing** — `build_index()` re-embeds everything every time, rather than only what changed

These are the natural next layer if this ever needed to move beyond a local pet project.

## Repository

[github.com/zhamora888/ai-knowledge](https://github.com/zhamora888/ai-knowledge) — one commit per phase, `docs/phaseN.md` for the full reasoning behind each one.
