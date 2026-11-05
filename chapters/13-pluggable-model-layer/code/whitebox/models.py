"""Models. The rest of the framework only knows about the Model class."""
import os

import requests

from .messages import Message, ToolCall

DEFAULT_MODEL = "ollama/qwen2.5:7b"


class Model:
    """The shape that every model shares."""

    def chat(self, messages, tools=None, **options):
        raise NotImplementedError


class OllamaModel(Model):
    """A model served by Ollama. Translates to and from Ollama's format."""

    def __init__(self, name, url="http://127.0.0.1:11434"):
        self.name = name
        self.url = url

    def to_ollama(self, message):
        data = {"role": message.role, "content": message.content}
        if message.tool_calls:
            data["tool_calls"] = [
                {"function": {"name": call.name, "arguments": call.arguments}}
                for call in message.tool_calls
            ]
        if message.tool_name:
            data["tool_name"] = message.tool_name
        return data

    def from_ollama(self, data):
        calls = [
            ToolCall(call["function"]["name"], call["function"]["arguments"])
            for call in data.get("tool_calls") or []
        ]
        return Message("assistant", data.get("content", ""), calls)

    def chat(self, messages, tools=None, **options):
        body = {
            "model": self.name,
            "messages": [self.to_ollama(message) for message in messages],
            "tools": tools or [],
            "stream": False,
            "options": options,
        }
        response = requests.post(f"{self.url}/api/chat", json=body, timeout=180)
        response.raise_for_status()
        return self.from_ollama(response.json()["message"])


class FakeModel(Model):
    """Gives back replies you wrote in advance, and remembers what it was sent."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.seen = []

    def chat(self, messages, tools=None, **options):
        self.seen.append(list(messages))
        return self.replies.pop(0)


PROVIDERS = {"ollama": OllamaModel}


def load_model(spec=None):
    """Build a model from a "provider/name" string, or from the MODEL setting."""
    spec = spec or os.environ.get("MODEL", DEFAULT_MODEL)
    provider, _, name = spec.partition("/")
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider {provider!r}. Choose from {sorted(PROVIDERS)}.")
    return PROVIDERS[provider](name)
