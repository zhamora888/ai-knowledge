import json
import requests
from pathlib import Path

from search import search_notes, build_context

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"
MEMORY_FILE = Path("memory/conversation.json")

SYSTEM_PROMPT = "You are a helpful assistant. Answer clearly and concisely."


def load_messages() -> list:
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
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

    print(f"=== Local AI Chat ({MODEL}) ===")
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

        reply = call_ollama(messages)
        print(f"\nAssistant: {reply}\n")

        messages.append({"role": "assistant", "content": reply})
        save_messages(messages)


if __name__ == "__main__":
    main()
