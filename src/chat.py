import json
import sys
import requests
from pathlib import Path

import tools
from tools import TOOL_DEFINITIONS

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"
MEMORY_FILE = Path("memory/conversation.json")

SYSTEM_PROMPT = """You are a Software Architecture Assistant. Your role is to help with \
software design decisions, architecture reviews, and engineering best practices.

You have access to a knowledge base via tools:
- Use search_notes or read_file to look up relevant information before answering.
- Use list_documents to discover what is available.
- Use write_file ONLY when the user explicitly asks you to save, add, or update a note. \
  Never write to the knowledge base on your own initiative. \
  When writing, produce well-structured Markdown with a clear title and ## sections.

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
    """Simple one-shot call — used for the reviewer (no tools)."""
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": messages,
        "stream": False,
    })
    response.raise_for_status()
    return response.json()["message"]["content"]


def run_agent(messages: list) -> str:
    """Agentic loop: call Ollama, execute any tool calls, repeat until a text reply arrives."""
    while True:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "messages": messages,
            "tools": TOOL_DEFINITIONS,
            "stream": False,
        })
        response.raise_for_status()
        message = response.json()["message"]

        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            # No tool calls — the model produced its final answer.
            return message["content"]

        # Append the assistant's tool-call turn to the messages list.
        messages.append(message)

        # Execute each requested tool and feed results back.
        for tc in tool_calls:
            fn = tc["function"]
            name = fn["name"]
            args = fn.get("arguments") or {}
            if isinstance(args, str):
                args = json.loads(args)

            print(f"  [tool: {name}({args})]")
            result = tools.execute(name, args)

            messages.append({"role": "tool", "content": result})


def run_reviewer(user_input: str, architect_reply: str) -> str:
    messages = [
        {"role": "system", "content": REVIEWER_PROMPT},
        {"role": "user", "content": (
            f"Design question: {user_input}\n\n"
            f"Proposed solution:\n{architect_reply}"
        )},
    ]
    return call_ollama(messages)


def main():
    if "--reset" in sys.argv and MEMORY_FILE.exists():
        MEMORY_FILE.unlink()
        print("Memory cleared.\n")

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

        messages.append({"role": "user", "content": user_input})

        architect_reply = run_agent(messages)
        print(f"\n[Architect]\n{architect_reply}\n")

        critique = run_reviewer(user_input, architect_reply)
        print(f"[Reviewer]\n{critique}\n")

        combined = f"**Architect:**\n{architect_reply}\n\n**Reviewer:**\n{critique}"
        messages.append({"role": "assistant", "content": combined})
        save_messages(messages)


if __name__ == "__main__":
    main()
