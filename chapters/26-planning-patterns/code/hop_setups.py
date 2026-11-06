"""Provided: the setups this chapter compares, and the questions it asks them.

Split is chapter 23's, moved here unchanged. StepByStep and Counted are explained in section 5.
"""
from library import OPTIONS, Remember, all_documents, build_agent, build_index, files_seen, load_runs, searches, tool_text
from questions import HANDBOOK
from whitebox import Message, Plan, clean, excerpts
from whitebox.agent import Result
from whitebox.planning import FIND, ONE_ANSWER

ASK_FACTS = (
    "Question: {question}\n\nBreak this question into the separate facts someone would look up in a staff handbook. "
    "For example, a question about a job may need what group that job is in, and then the rule for that group. "
    "Write one short search query per fact, one per line, at most 3. Write nothing else."
)
NEXT = (
    "Question: {question}\n\nKnown so far:\n{known}\n\nIf you can answer the question for this person from what's "
    "known, reply DONE. If not, reply with one short search query for the next fact you need. Write nothing else."
)

HOPS = [row for row in HANDBOOK if row[1] == "hop"]
TWO_FILES = ["harbour-arrive", "senior-beans", "shift-lead-pay", "lead-notice"]  # Chapter 23: the rest need one.
CONTROLS = [row for row in HANDBOOK if row[1] == "direct"] + [row for row in HANDBOOK if row[1] == "none"]


def add_new(hits, more):
    """Add the hits we don't have yet."""
    have = {hit.text for hit in hits}
    return hits + [hit for hit in more if hit.text not in have]


def answer_from(model, question, hits, queries, notes=""):
    """Answer from the hits, and any notes, and return a Result that also says what was searched."""
    asked = f"Excerpts:\n\n{excerpts(hits)}\n\n"
    if notes:
        asked += f"Notes from the search:\n{notes}\n\n"
    messages = [Message("system", ONE_ANSWER), Message("user", asked + f"Question: {question}")]
    reply = model.chat(messages, **OPTIONS)
    result = Result(reply.content, messages + [reply], 2)
    result.queries, result.seen = queries, excerpts(hits)
    return result


class Split:
    """Chapter 23: ask for the facts first, always search for each one, and answer once."""

    def __init__(self, model, index, k=3):
        self.model, self.index, self.k = model, index, k

    def run(self, question):
        reply = self.model.chat([Message("user", ASK_FACTS.format(question=question))], **OPTIONS)
        queries = [clean(line) for line in reply.content.splitlines() if clean(line)][:3]
        hits = []
        for query in queries:
            hits = add_new(hits, self.index.search(query, self.k))
        return answer_from(self.model, question, hits, queries)


class StepByStep:
    """No plan: search, write down what was found, and let the model choose the next search or stop."""

    def __init__(self, model, index, k=3, limit=3):
        self.model, self.index, self.k, self.limit = model, index, k, limit

    def ask(self, text):
        return self.model.chat([Message("user", text)], **OPTIONS).content.strip()

    def run(self, question):
        hits, known, queries = [], [], []
        query = question
        for _ in range(self.limit):
            found = self.index.search(query, self.k)
            hits = add_new(hits, found)
            queries.append(query)
            known.append(self.ask(FIND.format(excerpts=excerpts(found), step=query)))
            decision = self.ask(NEXT.format(question=question, known="\n".join(known)))
            if decision.upper().startswith("DONE"):
                break
            query = clean(decision.splitlines()[0])
        return answer_from(self.model, question, hits, queries, "\n".join(known))


class Counted:
    """Wraps a model and counts every call, so the cost is measured, not worked out."""

    def __init__(self, model):
        self.model = model
        self.calls = 0

    def chat(self, *args, **kwargs):
        self.calls += 1
        return self.model.chat(*args, **kwargs)

    def stream(self, *args, **kwargs):
        self.calls += 1
        return self.model.stream(*args, **kwargs)


def build_setups(model, index):
    return {
        "Plain agent": build_agent(model, index),
        "Split": Split(model, index),
        "Step by step": StepByStep(model, index),
        "Plan": Plan(model, index, options=OPTIONS),
    }


def handbook_index():
    return Remember(build_index(all_documents(), 60))


def what_it_did(result):
    """What a run searched and saw, whichever setup ran it. An agent keeps these in its messages."""
    seen = getattr(result, "seen", None) or tool_text(result)
    return getattr(result, "queries", None) or searches(result), seen


def saved_tests():
    """Both batches of the hop test: yours if you've made them, and otherwise ours."""
    return load_runs("plan-test.json") + load_runs("plan-test-again.json")
