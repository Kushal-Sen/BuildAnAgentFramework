"""Chapter 04 exercises. Complete each TODO, then run: python3 exercises.py"""
import functools
import inspect
from contextlib import contextmanager


def double_result(function):
    """TODO 1: Return a wrapper that calls the function and doubles its result.
    Use functools.wraps, so the function keeps its name.
    """
    return function


REGISTRY = {}


def register(function):
    """TODO 2: Store the function in REGISTRY under its name, then return it."""
    return function


def call_tool(function, arguments):
    """TODO 3: Call the function using the arguments dictionary, and return the result."""
    return None


def evens(limit):
    """TODO 4: Write a generator that yields each even number from 2 up to limit."""
    return []


@contextmanager
def tracked(log):
    """TODO 5: Add "start" to the log, run the block, then always add "end",
    even if the block raises an error.
    """
    yield


# ---- Self-check: you don't need to change anything below this line. ----


def check_double_result():
    @double_result
    def five():
        return 5

    @double_result
    def add(a, b):
        return a + b

    assert five() == 10, f"five() returned {five()}, expected 10"
    assert add(2, b=3) == 10, "the wrapper should pass on all arguments"
    assert five.__name__ == "five", "use functools.wraps to keep the name"


def check_register():
    @register
    def sample():
        return "ok"

    assert "sample" in REGISTRY, "the function isn't in REGISTRY"
    assert sample() == "ok", "register should return the function"


def check_call_tool():
    def subtract(a, b):
        return a - b

    result = call_tool(subtract, {"a": 5, "b": 2})
    assert result == 3, f"returned {result}, expected 3"


def check_evens():
    assert inspect.isgenerator(evens(4)), "use yield to make a generator"
    assert list(evens(7)) == [2, 4, 6], f"returned {list(evens(7))}, expected [2, 4, 6]"


def check_tracked():
    log = []
    with tracked(log):
        log.append("work")
    assert log == ["start", "work", "end"], f"log is {log}"
    log = []
    try:
        with tracked(log):
            raise ValueError
    except ValueError:
        pass
    assert log == ["start", "end"], f"after an error, log is {log}. Use try and finally."


if __name__ == "__main__":
    checks = [("TODO 1: double_result", check_double_result), ("TODO 2: register", check_register),
              ("TODO 3: call_tool", check_call_tool), ("TODO 4: evens", check_evens),
              ("TODO 5: tracked", check_tracked)]
    passed = 0
    for label, check in checks:
        try:
            check()
            passed += 1
            print(f"PASS  {label}")
        except Exception as error:
            print(f"FAIL  {label}: {error}")
    print(f"{passed}/{len(checks)} passed")
