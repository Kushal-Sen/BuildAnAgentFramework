"""Chapter 09 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""


def ask_model(messages, chat):
    """TODO 1: Send messages to chat, which returns the reply as text. Add the reply to
    messages as an "assistant" message, then return the reply.
    """
    return None


def give_result(messages, text):
    """TODO 2: Add the text to messages as a "user" message. Return nothing."""


def play_session(question, chat, results):
    """TODO 3: Run a whole session, with a list of results in place of a person.
    Start with one "user" message that holds the question. For each result, ask the model,
    then give it the result. Finally, ask the model once more, and return that last reply.
    """
    return None


def workflow_prompt(question, files):
    """TODO 4: files is a dictionary from file name to text. Return the question, then a
    blank line, then each file in sorted name order, like this:
    a.txt: Coffee: 120
    b.txt: Coffee: 150
    """
    return None


def pick_shape(needs_outside_facts, steps_known):
    """TODO 5: Return the simplest shape that fits the job: "single call", "workflow" or
    "agent". If the job needs no outside facts, it's a single call. If it does, and you
    know the steps in advance, it's a workflow. Otherwise, it's an agent.
    """
    return None
