"""Part 4 checkpoint. Complete each TODO, then run: python3 -m pytest test_checkpoint.py"""
from pathlib import Path

from whitebox import (
    Agent, Case, HybridIndex, Index, KeywordIndex, LoopGuard, OllamaEmbedder, Rag, RescueToolCalls, Retry, Toolbox,
    contains, excludes, finished, load_documents, load_model, make_chunks, run_eval, search_tool,
)

GUIDE = Path(__file__).parent / "workspace" / "guide"
SYSTEM = (
    "You answer questions about the Larkfield Library guide. Use search_handbook to find facts, and never "
    "answer from memory. If an answer depends on a second fact, search for that too. "
    "If searching doesn't find the answer, say exactly: I don't know."
)


def build_chunks():
    """TODO 1: Load the documents in GUIDE, and return chunks of about 60 words that carry
    their document's title.
    """
    return []


def build_index(chunks, embedder):
    """TODO 2: Return a HybridIndex that joins an Index using embedder with a KeywordIndex,
    with chunks added to it.
    """
    return None


def build_pipeline(model, index):
    """TODO 3: Return a Rag pipeline that uses model and index, finds 3 hits, and has the
    option temperature 0.7.
    """
    return None


def build_agent(model, index):
    """TODO 4: Return an Agent whose only tool searches index for 3 hits. Wrap model in
    RescueToolCalls, then wrap that in Retry. Use SYSTEM, the hook LoopGuard(), and the option
    temperature 0.7.
    """
    return None


def make_cases():
    """TODO 5: Return three Cases, each with a check on the answer and finished():
    "colour page" asks how much one colour page costs, and the answer has 40p.
    "student fee" asks "I'm a student. How much is my late fee each day?". The answer has 5p, and
    doesn't have 10p or 20p, because an answer listing every band isn't an answer. Use excludes.
    "cafe" asks whether the library has a cafe, and the answer has "don't know".
    """
    return []


if __name__ == "__main__":
    model = load_model()
    index = build_index(build_chunks(), OllamaEmbedder())
    for label, runner in (("pipeline", build_pipeline(model, index)), ("agent", build_agent(model, index))):
        print(run_eval(runner, make_cases(), runs=5, label=label).table())
