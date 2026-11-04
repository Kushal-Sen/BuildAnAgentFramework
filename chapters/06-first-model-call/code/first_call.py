"""Your first calls to an AI model."""
import json

import requests

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"


def chat(messages, **options):
    """Send a conversation to the model, and return its reply as text."""
    body = {"model": MODEL, "messages": messages, "stream": False, "options": options}
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return response.json()["message"]["content"]


def stream_chat(messages):
    """Send a conversation to the model, and yield its reply piece by piece."""
    body = {"model": MODEL, "messages": messages, "stream": True}
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180, stream=True)
    response.raise_for_status()
    for line in response.iter_lines():
        yield json.loads(line)["message"]["content"]


print("1. One question")
question = {"role": "user", "content": "What is Python? Reply in one short sentence."}
print(chat([question]))

print("2. A system message")
pirate = {"role": "system",
          "content": "You always talk like a pirate, and you start every reply with Arr! "
                     "Keep your reply to one short sentence."}
print(chat([pirate, question]))

print("3. A conversation")
messages = [
    {"role": "user", "content": "Suggest a fruit. Reply with one word."},
    {"role": "assistant", "content": "Mango"},
    {"role": "user", "content": "What color is it? Reply in one short sentence."},
]
print(chat(messages))

print("4. Streaming")
pieces = list(stream_chat([{"role": "user", "content": "Say hello to a new learner in one short sentence."}]))
print(pieces[:6])
print("".join(pieces))

print("5. Two puzzles")
name = {"role": "user", "content": "Suggest an unusual name for a cat. Reply with only the name."}
print("Same question, three times:", [chat([name]) for _ in range(3)])
chat([{"role": "user", "content": "My name is Asha."}])
print(chat([{"role": "user", "content": "What is my name? Reply in one short sentence."}]))
