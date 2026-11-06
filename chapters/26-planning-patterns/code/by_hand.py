"""Do the two searches by hand, reading the first result before writing the second. No chat model here."""
from hop_setups import handbook_index

index = handbook_index()


def show(query):
    print(f"Search: {query}")
    for hit in index.search(query, 3):
        print(f"  [{hit.source}]", " ".join(hit.text.split())[:150])


show("What band is a shift lead?")
# Read that. Now you know a word the question never said.
show("How much notice does Band C give?")
