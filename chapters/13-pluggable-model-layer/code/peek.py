"""Provided: one tool request, in our format and in Ollama's."""
from whitebox import Message, OllamaModel, ToolCall

ollama = OllamaModel("qwen2.5:7b")

print("1. Our format")
ours = Message("assistant", tool_calls=[ToolCall("read_file", {"path": "sales/monday.txt"})])
print(ours)

print("2. Translated for Ollama")
theirs = ollama.to_ollama(ours)
print(theirs)

print("3. Translated back")
print(ollama.from_ollama(theirs) == ours)
