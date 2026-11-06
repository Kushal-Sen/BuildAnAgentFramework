"""One question through a Reranker, counting the model calls."""
from library import all_documents, build_index, rank_of_text
from whitebox import Reranker, load_model

QUESTIONS = [("What does E44 mean?", "E44"), ("What is FN-6 used for?", "FN-6")]


class Counted:
    """Passes every chat on to the real model, and counts them."""

    def __init__(self, model):
        self.model = model
        self.calls = 0

    def chat(self, messages, **options):
        self.calls += 1
        return self.model.chat(messages, **options)


index = build_index(all_documents(), 60, titles=True)
model = Counted(load_model())
reranker = Reranker(index, model)

for question, code in QUESTIONS:
    model.calls = 0
    print(question)
    print("  Vector rank:", rank_of_text(index, question, code))
    hits = reranker.search(question, 15)
    print("  Reranked rank:", next((place for place, hit in enumerate(hits, 1) if code in hit.text), None))
    print("  Model calls:", model.calls)
