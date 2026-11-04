"""Chapter 08 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import json


def build_prompt(task, context, output_format):
    """TODO 1: Return one string with three lines:
    Task: <task>
    Context: <context>
    Format: <output_format>
    """
    return None


def with_examples(instructions, examples):
    """TODO 2: examples is a list of (message, label) pairs. Return the instructions,
    followed by one line for each example, like this:
    Message: I need a refund. Label: billing
    """
    return None


def final_answer(reply):
    """TODO 3: Return the last line of the reply, with spaces removed from both ends."""
    return None


def parse_json(reply):
    """TODO 4: Return the JSON in the reply as Python data. The reply may be wrapped in
    a code fence, which starts with ```json and ends with ```. Remove those first.
    """
    return None


def label_schema(labels):
    """TODO 5: Return a schema for an object with one required string field, "label",
    which can only be one of the labels. Tip: {"type": "string", "enum": labels}.
    """
    return None
