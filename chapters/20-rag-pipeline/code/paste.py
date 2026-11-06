"""Paste every document into the prompt. Same run() shape as an Agent, so run_eval works on it."""
from dataclasses import dataclass, field

from whitebox import Message
from whitebox.agent import Result
from whitebox.rag import RAG_SYSTEM


@dataclass
class Paste:
    model: object
    documents: dict
    options: dict = field(default_factory=dict)

    def run(self, question):
        text = "\n\n".join(f"[{name}]\n{body}" for name, body in self.documents.items())
        messages = [
            Message("system", RAG_SYSTEM),
            Message("user", f"Excerpts:\n\n{text}\n\nQuestion: {question}"),
        ]
        reply = self.model.chat(messages, **self.options)
        return Result(reply.content, messages + [reply], 1)
