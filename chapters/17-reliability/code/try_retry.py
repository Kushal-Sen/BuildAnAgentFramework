"""Provided: Retry around a model that fails twice on purpose. usage: python3 try_retry.py"""
import time

from whitebox import Message, Model, ModelError, Retry, load_model


class FailsTwice(Model):
    """Wraps a real model. The first two calls fail, to simulate a busy server."""

    def __init__(self, model):
        self.model = model
        self.failures = 2

    def chat(self, messages, tools=None, **options):
        if self.failures > 0:
            self.failures -= 1
            print("FailsTwice: simulated failure")
            raise ModelError("The server is busy.", retryable=True)
        return self.model.chat(messages, tools, **options)


def wait(seconds):
    print(f"Retry: waiting {seconds} seconds")
    time.sleep(seconds)


model = Retry(FailsTwice(load_model()), sleep=wait)
reply = model.chat([Message("user", "Say hello in three words.")], temperature=0)
print("Answer:", reply.content)
