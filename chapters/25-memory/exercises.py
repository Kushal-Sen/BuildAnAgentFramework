"""Chapter 25 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Hook, Memory, Message, newest


def unwanted(notes, words):
    """TODO 1: Return the notes that hold none of the words, in the order they came. notes is a list of
    strings, and words is a list of lowercase words, one for each fact you hoped to save. Ignore case.
    """
    return None


def recall_score(model, system, questions):
    """TODO 2: Ask each question in a new session, and return how many answers were right. questions is
    a list of (question, word) pairs. A new session is one model.chat call with just two messages: the
    system prompt, then the question. An answer is right if it contains word, ignoring case.
    """
    return None


def forget(memory, word):
    """TODO 3: Delete every note that contains word, ignoring case, and return how many went. Change
    memory.notes, then write the file the way Memory.add does: to a temporary file first, and then
    os.replace. If nothing matched, leave the file alone.
    """
    return None


class Budgeted(Memory):
    """TODO 4: Section 11 said you'll need a limit one day. Override system so the prompt holds only the
    newest notes that fit in budget tokens, still oldest first. The rest of the text must match what
    Memory.system builds, and with no notes it returns text unchanged. Don't change self.notes or the file.
    Chapter 24's newest(messages, budget) does the counting, if you turn each note into a Message.
    """

    def __init__(self, path, budget):
        super().__init__(path)
        self.budget = budget


class Private(Hook):
    """TODO 5: Block the remember tool when the user's latest words contain one of the blocked words,
    ignoring case. Return "Not saved: that looks private." from before_tool to block it. memory.latest
    holds the latest words. Let every other tool through, by returning None.
    """

    def __init__(self, memory, words):
        self.memory = memory
        self.words = words
