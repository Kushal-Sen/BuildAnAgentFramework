"""What can a model do on its own? Three experiments."""
from pathlib import Path

import requests

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"
HERE = Path(__file__).parent


def chat(messages, **options):
    """Send a conversation to the model, and return its reply as text."""
    body = {"model": MODEL, "messages": messages, "stream": False, "options": options}
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return response.json()["message"]["content"]


def user(text):
    return {"role": "user", "content": text}


def system(text):
    return {"role": "system", "content": text}


QUESTION = "What was the total coffee revenue across all the days in the sales folder?"

print("1. Just ask")
print(" ", chat([user(QUESTION + " Reply in one sentence.")], temperature=0))

YOU_CAN = ("You can read and write files on this computer. "
           "Do what the user asks, then report the result in one sentence.")
print("2. Tell it that it can read files")
for seed in range(5):
    print(" ", chat([system(YOU_CAN), user(QUESTION)], seed=seed))

print("3. Ask it to create a file")
request = "Create a file called note.txt that contains the word hello."
print(" ", chat([system(YOU_CAN), user(request)], temperature=0))
print("  Does note.txt exist?", (HERE / "note.txt").exists())
