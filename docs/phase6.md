# Phase 6 — Reviewer Pass

## Goal

Introduce a second perspective on every answer. After the Architect proposes a solution, a Reviewer independently critiques it — looking for SOLID violations, missing edge cases, scalability concerns, and simpler alternatives. Same model, completely different behaviour, just by changing the prompt.

## What Changed

### REVIEWER_PROMPT

A second system prompt defines the Reviewer's role:

```
You are a Senior Software Engineer conducting a design review.
You will be given a design question and an architecture proposal.

Your job is to critically evaluate the proposal. Look for:
- Violations of SOLID principles or established patterns
- Missing edge cases or failure modes
- Scalability or maintainability concerns
- Simpler alternatives that achieve the same goal

Be direct and specific. If the proposal is sound, say so briefly and
note only genuine concerns. Do not repeat the proposal back — just critique it.
```

### run_reviewer()

A new function makes an independent Ollama call with the reviewer role:

```python
def run_reviewer(user_input: str, architect_reply: str) -> str:
    messages = [
        {"role": "system", "content": REVIEWER_PROMPT},
        {"role": "user", "content": (
            f"Design question: {user_input}\n\n"
            f"Proposed solution:\n{architect_reply}"
        )},
    ]
    return call_ollama(messages)
```

Key point: the reviewer's `messages` list is freshly constructed. It does not include the conversation history. The reviewer only sees the current question and the architect's answer — it has no awareness of previous turns.

### The main loop

Each turn now makes two Ollama calls:

```
User question
    ↓
build_prompt()          → retrieves relevant note sections
    ↓
call_ollama(messages)   → Architect answers (with full conversation history + notes)
    ↓
run_reviewer()          → Reviewer critiques (fresh context: question + proposal only)
    ↓
combined saved to memory as single assistant turn
```

Both passes are displayed separately in the terminal:
```
[Architect]
...proposal...

[Reviewer]
...critique...
```

And saved as one combined assistant message so the next turn has both perspectives in context:
```
**Architect:**
...proposal...

**Reviewer:**
...critique...
```

## The Core Insight: Same Model, Different Agent

The Architect and the Reviewer are not different models. They are not different programs. They are the same `call_ollama()` function called with different `messages` lists.

What makes them behave differently is entirely the system prompt and the input they receive. This is deterministic orchestration — your Python code decides who speaks, in what order, and what each "agent" is shown. The model just executes its role as instructed.

This is the foundation of multi-agent systems: multiple prompts, coordinated by application logic, each producing output that feeds the next step.

## Limitations

- Two calls per turn means twice the latency. With a local model this is acceptable.
- The Reviewer only sees the current question and proposal — it has no memory of past turns. This is intentional: the review should be independent and unbiased by conversation history.
- With a 1B model, the Reviewer may not always catch subtle issues. The pattern is sound — the model's capacity is the constraint.

## File Reference

| File | Purpose |
|---|---|
| `src/chat.py` | Added `REVIEWER_PROMPT` and `run_reviewer()`, updated main loop |
