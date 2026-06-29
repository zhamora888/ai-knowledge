import json
import requests
from pathlib import Path

from search import search_notes, build_context

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"
MEMORY_FILE = Path("memory/conversation.json")

SYSTEM_PROMPT = """You are a Software Architecture Assistant. Your role is to help with \
software design decisions, architecture reviews, and engineering best practices.

When knowledge base notes are provided in the prompt, use them as your primary reference. \
Be specific — cite the relevant principles or patterns from those notes. If the notes do not \
cover the topic, draw on general software engineering knowledge and say so.

Structure your answers clearly. When reviewing designs, identify tradeoffs. \
When proposing solutions, explain the reasoning behind them. Be concise."""

REVIEWER_PROMPT = """You are a Senior Software Engineer conducting a design review. \
You will be given a design question and an architecture proposal.

Your job is to critically evaluate the proposal. Look for:
- Violations of SOLID principles or established patterns
- Missing edge cases or failure modes
- Scalability or maintainability concerns
- Simpler alternatives that achieve the same goal

Be direct and specific. If the proposal is sound, say so briefly and note only genuine concerns. \
Do not repeat the proposal back — just critique it."""


def load_messages() -> list:
    if MEMORY_FILE.exists():
        messages = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        # Always apply the current system prompt so role changes take effect immediately.
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = SYSTEM_PROMPT
        return messages
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def save_messages(messages: list) -> None:
    MEMORY_FILE.write_text(
        json.dumps(messages, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def call_ollama(messages: list) -> str:
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": messages,
        "stream": False,
    })
    response.raise_for_status()
    return response.json()["message"]["content"]


def run_reviewer(user_input: str, architect_reply: str) -> str:
    # Independent call — fresh messages list with the reviewer role.
    # The reviewer sees only the question and the proposal, not the full conversation.
    messages = [
        {"role": "system", "content": REVIEWER_PROMPT},
        {"role": "user", "content": (
            f"Design question: {user_input}\n\n"
            f"Proposed solution:\n{architect_reply}"
        )},
    ]
    return call_ollama(messages)


def build_prompt(user_input: str) -> str:
    matches = search_notes(user_input)
    if not matches:
        return user_input

    labels = ", ".join(f"{m['filename']} > {m['heading']}" for m in matches)
    print(f"  [retrieved: {labels}]")

    context = build_context(matches)
    return (
        f"[Relevant notes from knowledge base]\n\n"
        f"{context}\n\n"
        f"[Question]\n{user_input}"
    )


def main():
    messages = load_messages()
    is_new = len(messages) == 1

    print(f"=== Software Architecture Assistant ({MODEL}) ===")
    if is_new:
        print("New conversation started.")
    else:
        print(f"Resumed conversation ({len(messages) - 1} messages loaded).")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        prompt = build_prompt(user_input)
        messages.append({"role": "user", "content": prompt})

        architect_reply = call_ollama(messages)
        print(f"\n[Architect]\n{architect_reply}\n")

        critique = run_reviewer(user_input, architect_reply)
        print(f"[Reviewer]\n{critique}\n")

        # Save both passes as a single assistant turn so future context includes both.
        combined = f"**Architect:**\n{architect_reply}\n\n**Reviewer:**\n{critique}"
        messages.append({"role": "assistant", "content": combined})
        save_messages(messages)


if __name__ == "__main__":
    main()
