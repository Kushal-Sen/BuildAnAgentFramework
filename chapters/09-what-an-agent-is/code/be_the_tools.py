"""You play the part of the tools. The model asks, and you fetch."""
import requests

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"
QUESTION = "What was the total coffee revenue across all the days in the sales folder?"
SYSTEM = """You can't see any files. A person is helping you, and they can.
Each message you send must ask for exactly one thing, such as the files in a folder, or
what one file says. Then stop, and wait for their reply. Never guess what a file says.
When you have everything you need, state the final answer."""


def chat(messages, **options):
    """Send a conversation to the model, and return its reply as text."""
    body = {"model": MODEL, "messages": messages, "stream": False, "options": options}
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return response.json()["message"]["content"]


messages = [
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": QUESTION},
]
print("Question:", QUESTION)
answer = ""
while answer != "done":
    reply = chat(messages, temperature=0)
    print("Model:", reply)
    messages.append({"role": "assistant", "content": reply})
    answer = input("You: ")
    messages.append({"role": "user", "content": answer})
