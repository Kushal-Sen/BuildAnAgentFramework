"""Models. The rest of the framework only knows about the Model class."""
import json
import os

import requests

from .messages import Message, ToolCall

DEFAULT_MODEL = "ollama/qwen2.5:7b"


class Model:
    """The shape that every model shares."""

    def chat(self, messages, tools=None, **options):
        raise NotImplementedError

    def stream(self, messages, tools=None, **options):
        """Yield the reply's text in pieces, then the finished Message."""
        reply = self.chat(messages, tools, **options)
        if reply.content:
            yield reply.content
        yield reply


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

    def tool_to_ollama(self, tool):
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }

    def from_ollama(self, data):
        calls = [
            ToolCall(call["function"]["name"], call["function"]["arguments"])
            for call in data.get("tool_calls") or []
        ]
        return Message("assistant", data.get("content", ""), calls)

    def request_body(self, messages, tools, options, stream):
        return {
            "model": self.name,
            "messages": [self.to_ollama(message) for message in messages],
            "tools": [self.tool_to_ollama(tool) for tool in tools or []],
            "stream": stream,
            "options": options,
        }

    def chat(self, messages, tools=None, **options):
        body = self.request_body(messages, tools, options, stream=False)
        response = requests.post(f"{self.url}/api/chat", json=body, timeout=180)
        response.raise_for_status()
        return self.from_ollama(response.json()["message"])

    def stream(self, messages, tools=None, **options):
        body = self.request_body(messages, tools, options, stream=True)
        response = requests.post(f"{self.url}/api/chat", json=body, timeout=180, stream=True)
        response.raise_for_status()
        text, calls = "", []
        for line in response.iter_lines():
            part = json.loads(line)["message"]
            if part.get("content"):
                text += part["content"]
                yield part["content"]
            calls += part.get("tool_calls") or []
        yield self.from_ollama({"content": text, "tool_calls": calls})


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
