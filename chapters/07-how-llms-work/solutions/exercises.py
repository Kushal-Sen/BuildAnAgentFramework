"""Chapter 07 exercises, solved."""
import math


def estimate_tokens(text):
    return math.ceil(len(text) / 4)


def most_likely(chances):
    return max(chances, key=chances.get)


def apply_temperature(scores, temperature):
    weights = [math.exp(score / temperature) for score in scores]
    total = sum(weights)
    return [weight / total for weight in weights]


def fits_window(prompt_tokens, reply_tokens, window):
    return prompt_tokens + reply_tokens <= window


def add_turn(history, question, answer):
    return history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]
