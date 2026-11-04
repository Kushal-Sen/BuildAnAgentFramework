"""A workflow: your code decides every step, and the model does one of them."""
from pathlib import Path

import requests

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"
FOLDER = Path(__file__).parent / "workspace" / "sales"
QUESTION = "What was the total coffee revenue across all the days in the sales folder?"


def chat(messages, **options):
    """Send a conversation to the model, and return its reply as text."""
    body = {"model": MODEL, "messages": messages, "stream": False, "options": options}
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return response.json()["message"]["content"]


# Step 1: your code reads every file.
files = ""
for path in sorted(FOLDER.iterdir()):
    files += f"{path.name}:\n{path.read_text()}\n"

# Step 2: your code builds the prompt.
prompt = f"{QUESTION}\n\nHere are the files:\n\n{files}"
print(prompt)

# Step 3: the model answers, in one call.
replies = [chat([{"role": "user", "content": prompt}], seed=seed) for seed in range(5)]
print("A reply:", replies[0])
print(f"Correct: {sum('380' in reply for reply in replies)}/5")
