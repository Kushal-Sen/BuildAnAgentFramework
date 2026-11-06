"""Compare small lists of numbers with cosine, so you can check each result yourself."""
from whitebox import cosine

pairs = [
    ([1, 0], [1, 0]),
    ([3, 4], [6, 8]),
    ([1, 0], [1, 1]),
    ([1, 0], [0, 1]),
    ([1, 0], [-1, 0]),
]
for a, b in pairs:
    print(f"{a!s:8} {b!s:8} {cosine(a, b):.3f}")
