"""Three ways to get a second fact. hop_fixes.py tries them, and eval_agent.py measures Split."""
from whitebox import AGENT_SYSTEM, Message, excerpts
from whitebox.agent import Result
from whitebox.rag import RAG_SYSTEM

CHECK_SYSTEM = AGENT_SYSTEM + (
    " Before you answer, ask: does the rule I found depend on something I haven't looked up yet, such as "
    "which band a role is in? If it does, search for that first. Never guess it, and never list every option."
)

ASK_MISSING = (
    "Question: {question}\n\nExcerpts:\n\n{excerpts}\n\nTo answer the question for this person, is one fact missing "
    "from the excerpts? For example, the excerpts may give a rule for each band, but not say which band the person "
    "is in. If a fact is missing, reply with a short search query for it. If nothing is missing, reply with exactly: NONE"
)

ASK_FACTS = (
    "Question: {question}\n\nBreak this question into the separate facts someone would look up in a staff handbook. "
    "For example, a question about a job may need what group that job is in, and then the rule for that group. "
    "Write one short search query per fact, one per line, at most 3. Write nothing else."
)

ONE_ANSWER = RAG_SYSTEM + " Give one answer for this person: don't list every option."


def answer_from(model, question, hits, asked, queries, options):
    """Answer from the hits, and return a Result that also says what was searched."""
    messages = [Message("system", ONE_ANSWER), Message("user", f"Excerpts:\n\n{excerpts(hits)}\n\nQuestion: {question}")]
    reply = model.chat(messages, **options)
    result = Result(reply.content, asked + messages + [reply], 2)
    result.queries = queries
    result.seen = excerpts(hits)
    return result


def add_new(hits, more):
    """Add the hits we don't have yet."""
    have = {hit.text for hit in hits}
    return hits + [hit for hit in more if hit.text not in have]


class AskMissing:
    """Search, ask the model what's missing, search for that, and answer from both."""

    def __init__(self, model, index, k=3, options=None):
        self.model, self.index, self.k, self.options = model, index, k, options or {}

    def run(self, question):
        hits = self.index.search(question, self.k)
        asked = [Message("user", ASK_MISSING.format(question=question, excerpts=excerpts(hits)))]
        reply = self.model.chat(asked, **self.options)
        query = reply.content.strip().strip('"')
        if "NONE" not in query.upper():
            hits = add_new(hits, self.index.search(query, self.k))
        return answer_from(self.model, question, hits, asked + [reply], [query], self.options)


class Split:
    """Ask for the facts first, always search for each one, and answer once."""

    def __init__(self, model, index, k=3, options=None):
        self.model, self.index, self.k, self.options = model, index, k, options or {}

    def run(self, question):
        asked = [Message("user", ASK_FACTS.format(question=question))]
        reply = self.model.chat(asked, **self.options)
        queries = [line.strip(' -*"0123456789.') for line in reply.content.splitlines() if line.strip()][:3]
        hits = []
        for query in queries:
            hits = add_new(hits, self.index.search(query, self.k))
        return answer_from(self.model, question, hits, asked + [reply], queries, self.options)
