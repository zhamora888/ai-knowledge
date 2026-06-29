# Phase 2 — Persistent Conversation Memory

## Goal

Survive a restart. Save the conversation history to disk after every reply, and reload it on startup so the assistant remembers previous sessions.

## What Changed

Two functions were added to `src/chat.py`:

```python
def load_messages() -> list:
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def save_messages(messages: list) -> None:
    MEMORY_FILE.write_text(
        json.dumps(messages, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
```

`save_messages()` is called after every assistant reply. `load_messages()` is called once at startup.

## How It Works

The `messages` list is serialized to `memory/conversation.json` as plain JSON. On the next run, it is deserialized back into the same list and handed straight to Ollama — the model receives the full history exactly as before.

The file looks like this:

```json
[
  { "role": "system",    "content": "You are a helpful assistant..." },
  { "role": "user",      "content": "What is a binary tree?" },
  { "role": "assistant", "content": "A binary tree is a data structure..." },
  { "role": "user",      "content": "Give me a Python example." },
  { "role": "assistant", "content": "Sure! Here's a simple implementation..." }
]
```

## The Key Insight: Memory Belongs to the Application

The model has no awareness of past sessions. It does not store anything. When you reload the JSON and send it, the model simply sees a long conversation that appears to have happened — it cannot tell the difference between a live conversation and one loaded from a file.

This makes an important point clear: **the model is a function, not a stateful agent**. It takes input and produces output. State management — what to remember, how long to keep it, when to clear it — is entirely the application's responsibility.

## Startup Behaviour

| Situation | What happens |
|---|---|
| First run (no JSON file) | Initialises with just the system prompt |
| Subsequent runs (JSON exists) | Loads full history, prints message count |

The message count shown on startup excludes the system prompt (which is always index 0), so it reflects the number of actual conversation turns.

## What This Doesn't Solve

The conversation grows forever. Every turn adds two messages (user + assistant), and the entire list is sent to the model on every call. LLMs have a **context window limit** — if the conversation gets long enough, it will either be truncated or cause an error.

Phase 4 begins to address this by being selective about what context is injected. A future phase could add summarisation or a rolling window to cap memory size.

## File Reference

| File | Purpose |
|---|---|
| `src/chat.py` | Updated with `load_messages()` and `save_messages()` |
| `memory/conversation.json` | Persisted messages list (gitignored — stays local) |
