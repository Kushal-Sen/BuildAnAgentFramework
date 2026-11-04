"""Part 1 checkpoint, solved."""
import json

import requests

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"
LABELS = ["bug", "billing", "feature", "delivery", "other"]
TICKETS = [
    "The app crashes when I open my cart.",
    "Why was I charged twice?",
    "Can you add a dark mode?",
    "My parcel never arrived.",
    "I love this app!",
]


def chat(messages, format=None, **options):
    """Send a conversation to the model, and return its reply as text."""
    body = {"model": MODEL, "messages": messages, "stream": False, "options": options}
    if format:
        body["format"] = format
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return response.json()["message"]["content"]


def ticket_schema():
    return {
        "type": "object",
        "properties": {"label": {"type": "string", "enum": LABELS}},
        "required": ["label"],
    }


def ticket_messages(text):
    rules = ("Classify the customer's message. bug: something is broken. "
             "billing: payments and refunds. feature: a request for something new. "
             "delivery: parcels and shipping. other: anything else, including praise and thanks.")
    return [{"role": "system", "content": rules}, {"role": "user", "content": text}]


def classify(chat, text):
    reply = chat(ticket_messages(text), format=ticket_schema(), temperature=0)
    return json.loads(reply)["label"]


def classify_all(chat, tickets):
    for ticket in tickets:
        yield ticket, classify(chat, ticket)


def count_labels(results):
    counts = {}
    for _, label in results:
        counts[label] = counts.get(label, 0) + 1
    return counts


if __name__ == "__main__":
    results = list(classify_all(chat, TICKETS))
    for ticket, label in results:
        print(f"{label:9} {ticket}")
    print(count_labels(results))
