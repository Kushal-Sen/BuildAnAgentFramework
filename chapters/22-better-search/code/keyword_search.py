"""Three questions through KeywordIndex, ranked by the rare words they share with each chunk."""
from library import all_documents, build_keyword

QUESTIONS = [
    "What does E44 mean?",
    "How long was the Station card reader down just before Christmas 2025?",
    "Can I get money back for buying work footwear?",
]

index = build_keyword(all_documents(), 60)
for question in QUESTIONS:
    print(question)
    for hit in index.search(question, 3):
        print(f"  {hit.score:>5.2f}  {hit.source}")
