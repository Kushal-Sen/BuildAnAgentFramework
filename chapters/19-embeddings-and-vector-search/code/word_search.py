"""Search the handbook by counting the words a file shares with the question."""
from whitebox import load_documents
from whitebox.rag import words

COMMON = """a about am an and any anything are as at be can could do does for from get give go have
how i if in is it just long m many me much my not of on or s so t that the their this to up was
we what when where which who why will with would you your""".split()


def word_search(question, documents, k=3):
    """Score each file by how many of the question's words it holds. Return the top k."""
    wanted = [word for word in words(question) if word not in COMMON]
    scored = []
    for name, text in documents.items():
        found = words(text)
        scored.append((len([word for word in wanted if word in found]), name))
    return sorted(scored, key=lambda pair: pair[0], reverse=True)[:k]


if __name__ == "__main__":
    documents = load_documents("workspace/handbook")
    print(f"{len(documents)} files")
    for question in ["How much is the till float?", "Can I get money back for buying work footwear?"]:
        print(question)
        for score, name in word_search(question, documents):
            print(f"  {score}  {name}")
