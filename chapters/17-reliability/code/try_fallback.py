"""Provided: two real failures, then a Fallback past them. usage: python3 try_fallback.py"""
from whitebox import Fallback, Message, ModelError, OllamaModel, load_model

HELLO = [Message("user", "Say hello in three words.")]

unreachable = OllamaModel("qwen2.5:7b", url="http://127.0.0.1:9")
not_installed = OllamaModel("no-such-model")

for model in [unreachable, not_installed]:
    try:
        model.chat(HELLO)
    except ModelError as error:
        print(f"retryable={error.retryable}: {str(error)[:62]}")

model = Fallback([unreachable, not_installed, load_model()])
print("Answer:", model.chat(HELLO, temperature=0).content)
