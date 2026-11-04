"""Chapter 06 exercises, solved."""
import json


def user_message(text):
    return {"role": "user", "content": text}


def with_system(instructions, text):
    return [{"role": "system", "content": instructions}, user_message(text)]


def build_body(model, messages):
    return {"model": model, "messages": messages, "stream": False}


def reply_text(data):
    return data["message"]["content"]


def join_stream(lines):
    return "".join(json.loads(line)["message"]["content"] for line in lines)
