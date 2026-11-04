"""Chapter 01 exercises. Replace each TODO, then run: python3 exercises.py"""


def greet(name):
    """Return a greeting. greet("Asha") returns "Hello, Asha!"."""
    return None  # TODO 1


def is_even(number):
    """Return True if the number is even, otherwise False."""
    return None  # TODO 2


def order_size(total):
    """Return "big" for 300 or more, "medium" for 100 or more, otherwise "small"."""
    return None  # TODO 3


def sum_to(number):
    """Use a loop to add every whole number from 1 to number. sum_to(4) returns 10."""
    return None  # TODO 4


def discounted_price(price, percent):
    """Return the price after a discount. discounted_price(200, 25) returns 150.0."""
    return None  # TODO 5


# ---- Self-check: you don't need to change anything below this line. ----

CHECKS = [
    ("TODO 1: greet", greet, [(("Asha",), "Hello, Asha!"), (("Ravi",), "Hello, Ravi!")]),
    ("TODO 2: is_even", is_even, [((4,), True), ((7,), False), ((0,), True)]),
    ("TODO 3: order_size", order_size, [((300,), "big"), ((299,), "medium"), ((100,), "medium"), ((99,), "small")]),
    ("TODO 4: sum_to", sum_to, [((4,), 10), ((1,), 1), ((100,), 5050)]),
    ("TODO 5: discounted_price", discounted_price, [((200, 25), 150.0), ((80, 0), 80.0), ((50, 100), 0.0)]),
]


def run_check(cases, function):
    for arguments, expected in cases:
        result = function(*arguments)
        call = f"{function.__name__}({', '.join(repr(a) for a in arguments)})"
        assert result == expected, f"{call} returned {result!r}, expected {expected!r}"


if __name__ == "__main__":
    passed = 0
    for label, function, cases in CHECKS:
        try:
            run_check(cases, function)
            passed += 1
            print(f"PASS  {label}")
        except Exception as error:
            print(f"FAIL  {label}: {error}")
    print(f"{passed}/{len(CHECKS)} passed")
