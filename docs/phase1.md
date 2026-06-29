# Phase 1 — Basic Chat with Ollama

## Goal

Build the simplest possible working chat loop with a local LLM. No frameworks, no abstractions — just Python and HTTP.

## What We Built

A single script (`src/chat.py`) that:
- Sends messages to a locally running Ollama model
- Maintains a conversation history across turns
- Accepts a system prompt that sets the assistant's behaviour

## How It Works

### The Ollama API

Ollama runs as a local HTTP server on `http://localhost:11434`. We call its `/api/chat` endpoint with a POST request.

The request body looks like this:

```json
{
  "model": "llama3.2:1b",
  "messages": [
    { "role": "system",    "content": "You are a helpful assistant." },
    { "role": "user",      "content": "What is a binary tree?" },
    { "role": "assistant", "content": "A binary tree is..." },
    { "role": "user",      "content": "Can you give an example?" }
  ],
  "stream": false
}
```

The response contains the model's reply in `response["message"]["content"]`.

### The Messages List

The most important concept in Phase 1 is the `messages` list. Every conversation turn is a dictionary with two keys: `role` and `content`.

There are three roles:
- `system` — sets the assistant's persona and instructions (sent once, at the start)
- `user` — what you typed
- `assistant` — what the model replied

After each exchange, both the user message and the assistant reply are appended to the list. On the next call, the entire list is sent again. This is how the model "remembers" earlier turns.

### The Key Insight: The Model Is Stateless

The LLM has no memory between calls. It does not store your conversation. Every time you send a request, you are providing the full context from scratch.

What feels like "memory" during a conversation is actually your application reconstructing the context on every API call. The model sees the whole history as a single long input and generates the next message.

This is why the `messages` list grows with every turn — it is the conversation's memory, and it lives in your Python process, not in the model.

```
Turn 1:  [system, user1]                          → reply1
Turn 2:  [system, user1, reply1, user2]           → reply2
Turn 3:  [system, user1, reply1, user2, reply2, user3] → reply3
```

### The System Prompt

The system prompt is the first message in the list with `role: "system"`. It is the primary way to shape the model's behaviour — its tone, focus, constraints, and persona. It is injected once at the start and carried forward in every subsequent call.

In Phase 1 we use a simple generic prompt:
```
You are a helpful assistant. Answer clearly and concisely.
```

Later phases will replace this with a more specific role (e.g. Software Architecture Assistant).

## Running It

```bash
py src/chat.py
```

Type `quit`, `exit`, or `q` to end the session.

## Limitations (What Phase 2 Will Fix)

When you quit and restart, the conversation is gone. The `messages` list only exists in memory for the duration of the Python process. Phase 2 adds persistence by saving and loading this list as a JSON file.

## File Reference

| File | Purpose |
|---|---|
| `src/chat.py` | The chat loop — model call, message history, system prompt |
| `requirements.txt` | Python dependencies (`requests`) |
