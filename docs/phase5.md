# Phase 5 — Software Architecture Assistant

## Goal

Give the assistant a specific identity and area of expertise. Replace the generic system prompt with one that defines a role, sets expectations for how answers are structured, and tells the model how to use the knowledge base.

## What Changed

### The System Prompt

Before:
```
You are a helpful assistant. Answer clearly and concisely.
```

After:
```
You are a Software Architecture Assistant. Your role is to help with
software design decisions, architecture reviews, and engineering best practices.

When knowledge base notes are provided in the prompt, use them as your primary
reference. Be specific — cite the relevant principles or patterns from those notes.
If the notes do not cover the topic, draw on general software engineering knowledge
and say so.

Structure your answers clearly. When reviewing designs, identify tradeoffs.
When proposing solutions, explain the reasoning behind them. Be concise.
```

This prompt does several things:
- **Declares a role** — anchors the model's behaviour to a specific domain
- **Directs note usage** — tells the model to treat injected notes as primary sources
- **Sets answer structure** — tradeoffs, reasoning, conciseness
- **Sets an honesty expectation** — acknowledge when notes don't cover a topic

### load_messages() — live system prompt

The system prompt is now always overwritten when loading a saved conversation:

```python
if messages and messages[0]["role"] == "system":
    messages[0]["content"] = SYSTEM_PROMPT
```

This means you can update the system prompt and it takes effect on the next run without losing conversation history. The role is defined by the code, not by whatever was saved to disk.

## Why the System Prompt Is Powerful

The system prompt is processed before any user message. It shapes everything that follows — the model's tone, its focus, how it formats answers, what it pays attention to in the context.

A vague prompt ("be helpful") gives the model maximum latitude, which leads to inconsistent, unfocused answers. A specific prompt ("you are a Software Architecture Assistant — cite from the notes, identify tradeoffs") gives the model a clear lens to apply to every question.

This is prompt engineering in its simplest and most impactful form. You are not changing the model — you are changing the instructions it operates under.

## What to Try

Ask design questions that draw on your knowledge base:
- `"How would you structure a payment service?"` → should reason about architecture
- `"What pattern should I use to handle multiple payment providers?"` → should cite Strategy pattern from notes
- `"Review this design: a single class that handles auth, logging, and billing."` → should cite SRP and flag the violation

Notice how the answers are more structured and grounded than before.

## File Reference

| File | Purpose |
|---|---|
| `src/chat.py` | Updated `SYSTEM_PROMPT` and `load_messages()` |
