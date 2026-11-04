"""Chapter 04 exercises, solved. Run: python3 solutions/exercises.py"""
import functools
import inspect
from contextlib import contextmanager


def double_result(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs) * 2

    return wrapper


REGISTRY = {}


def register(function):
    REGISTRY[function.__name__] = function
    return function


def call_tool(function, arguments):
    return function(**arguments)


def evens(limit):
    for number in range(2, limit + 1, 2):
        yield number


@contextmanager
def tracked(log):
    log.append("start")
    try:
        yield
    finally:
        log.append("end")


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
