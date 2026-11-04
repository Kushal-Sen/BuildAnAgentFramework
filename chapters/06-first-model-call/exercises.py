"""Chapter 06 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import json


def user_message(text):
    """TODO 1: Return a message dictionary with the role "user" and the text as its content."""
    return None


def with_system(instructions, text):
    """TODO 2: Return a list of two messages: a "system" message, then a "user" message."""
    return None


def build_body(model, messages):
    """TODO 3: Return a dictionary with the keys model, messages and stream.
    Set stream to False.
    """
    return None


def reply_text(data):
    """TODO 4: Given the model's JSON response as a dictionary, return the reply text.
    The text is at data["message"]["content"].
    """
    return None


def join_stream(lines):
    """TODO 5: Each line is JSON text from a streamed reply. Read each line with json.loads,
    and join every piece of reply text into one string.
    """
    return None
