import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"

SYSTEM_PROMPT = "You are a helpful assistant. Answer clearly and concisely."


def call_ollama(messages: list) -> str:
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": messages,
        "stream": False,
    })
    response.raise_for_status()
    return response.json()["message"]["content"]


def main():
    print(f"=== Local AI Chat ({MODEL}) ===")
    print("Type 'quit' to exit.\n")

    # The conversation history lives here in the app, not in the model.
    # The model is stateless — we send the full history on every call.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        reply = call_ollama(messages)
        print(f"\nAssistant: {reply}\n")

        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
