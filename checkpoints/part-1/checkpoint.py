"""Part 1 checkpoint. Complete each TODO, then run: python3 -m pytest test_checkpoint.py"""
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
    """TODO 1: Return a schema for an object with one required field, "label",
    which must be one of LABELS.
    """
    return None


def ticket_messages(text):
    """TODO 2: Return a system message and a user message. The system message must
    define every label in LABELS, and the user message holds the ticket text.
    """
    return None


def classify(chat, text):
    """TODO 3: Call chat with the messages, format=ticket_schema() and temperature=0.
    Read the reply as JSON, and return its "label" value.
    """
    return None


def classify_all(chat, tickets):
    """TODO 4: Write a generator that yields (ticket, label) for each ticket."""
    return []


def count_labels(results):
    """TODO 5: results is a list of (ticket, label) pairs. Return a dictionary
    of each label and how many times it appears.
    """
    return None


if __name__ == "__main__":
    results = list(classify_all(chat, TICKETS))
    for ticket, label in results:
        print(f"{label:9} {ticket}")
    print(count_labels(results))
