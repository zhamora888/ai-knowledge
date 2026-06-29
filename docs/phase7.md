# Phase 7 — Tool Calling

## Goal

Give the model agency over what information it fetches. Instead of the application always deciding what context to inject, the model can now request tools — and your application executes them.

## What Changed

### src/tools.py (new)

Defines four tools and their JSON schemas, plus their Python implementations:

| Tool | What it does |
|---|---|
| `list_documents()` | Lists all `.md` files in `knowledge/` |
| `read_file(filename)` | Reads the full contents of a knowledge file |
| `search_notes(query)` | Searches for relevant sections (keyword retrieval from Phase 4) |
| `write_file(filename, content)` | Writes a new or updated file to `knowledge/` |

Each tool has two parts:
1. A **JSON schema** (`TOOL_DEFINITIONS`) sent to Ollama so the model knows tools exist and how to call them
2. A **Python function** that the application executes when the model requests it

### run_agent() — the agentic loop

Replaces `call_ollama()` for the Architect. The loop runs until the model produces a plain text reply:

```
call Ollama (with tools)
    ↓
model returns tool_calls? 
    yes → execute each tool → append results → loop back
    no  → return the text reply
```

In code:
```python
while True:
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": messages,
        "tools": TOOL_DEFINITIONS,
        "stream": False,
    })
    message = response.json()["message"]

    if not message.get("tool_calls"):
        return message["content"]   # final answer

    messages.append(message)       # append assistant's tool-call turn

    for tc in message["tool_calls"]:
        result = tools.execute(tc["function"]["name"], tc["function"]["arguments"])
        messages.append({"role": "tool", "content": result})
    # loop — call Ollama again with tool results in the messages
```

The terminal shows each tool call as it happens:
```
You: What design patterns are in my notes?
  [tool: list_documents({})]
  [tool: search_notes({'query': 'design patterns'})]

[Architect]
...
```

### System prompt updated

The system prompt now explicitly tells the model about its tools:
```
You have access to a knowledge base via tools. Use search_notes or read_file
to look up relevant information before answering. Use list_documents to
discover what is available.
```

Without this instruction, the model may not know to use the tools proactively.

## How Tool Calling Works in the API

When you send `tools` in the request, the model can respond in two ways:

**Normal reply** — `message.content` has text, `message.tool_calls` is empty/absent:
```json
{ "role": "assistant", "content": "Here is my answer..." }
```

**Tool call** — `message.content` is empty, `message.tool_calls` lists what to run:
```json
{
  "role": "assistant",
  "content": "",
  "tool_calls": [
    { "function": { "name": "search_notes", "arguments": { "query": "SOLID" } } }
  ]
}
```

Your application executes the function, then appends a `tool` role message with the result:
```json
{ "role": "tool", "content": "--- solid_principles.md > S — Single Responsibility..." }
```

Then you call Ollama again. The model sees its own tool call and the result, and continues.

## The Key Insight: Deterministic Orchestration vs Probabilistic Inference

The model decides *what* to request. Your application decides *what is allowed* and *how to execute it*.

- The model is probabilistic — it chooses tools based on its training and the prompt
- Your application is deterministic — `execute()` always runs the same Python code for the same tool name

This separation is the foundation of safe agentic systems. The model can only do what your `execute()` function permits. Adding a new capability means adding a new Python function and a new schema — the model cannot reach outside that boundary.

## Reviewer is unchanged

The Reviewer still uses `call_ollama()` (no tools). The critique pass is a one-shot call — it doesn't need to fetch information, just evaluate what the Architect produced.

## File Reference

| File | Purpose |
|---|---|
| `src/tools.py` | Tool schemas (`TOOL_DEFINITIONS`) and implementations (`execute()`) |
| `src/chat.py` | `run_agent()` agentic loop; `call_ollama()` kept for the reviewer |
