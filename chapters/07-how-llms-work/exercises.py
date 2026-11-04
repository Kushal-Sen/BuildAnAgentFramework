"""Chapter 07 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import math


def estimate_tokens(text):
    """TODO 1: Estimate tokens using the rule of thumb of 4 characters per token.
    Round up, so a 5-character text returns 2. Tip: math.ceil.
    """
    return None


def most_likely(chances):
    """TODO 2: Given a dictionary of token to chance, return the token with the highest chance.
    Tip: max(chances, key=chances.get).
    """
    return None


def apply_temperature(scores, temperature):
    """TODO 3: Turn a list of scores into a list of chances that add up to 1.
    Divide each score by the temperature, take math.exp of it,
    then divide each result by the total.
    """
    return None


def fits_window(prompt_tokens, reply_tokens, window):
    """TODO 4: Return True if the prompt and the reply together fit in the window."""
    return None


def add_turn(history, question, answer):
    """TODO 5: Return a new list: the history, then a "user" message with the question,
    then an "assistant" message with the answer. Don't change the original list.
    """
    return None
