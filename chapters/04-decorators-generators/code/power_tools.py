"""Decorators, generators and context managers."""
import functools
from contextlib import contextmanager


# Flexible arguments
def show(*args, **kwargs):
    print(args, kwargs)


show(1, 2, name="Tea")


def add(a, b):
    return a + b


arguments = {"a": 2, "b": 3}
print(add(**arguments))


# A decorator
def log_calls(function):
    """Print each call, then run the function."""

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        print(f"Calling {function.__name__} with {args}")
        return function(*args, **kwargs)

    return wrapper


@log_calls
def multiply(a, b):
    """Multiply two numbers."""
    return a * b


print(multiply(4, 5))
print(multiply.__name__, "-", multiply.__doc__)

# A decorator that registers tools
TOOLS = {}


def tool(function):
    """Add a function to the list of tools."""
    TOOLS[function.__name__] = function
    return function


@tool
def greet(name):
    return f"Hello, {name}!"


@tool
def shout(text):
    return text.upper()


print(sorted(TOOLS))
print(TOOLS["greet"]("Asha"))


# Generators
def stream_words(text):
    """Give back one word at a time."""
    for word in text.split():
        yield word


words = stream_words("Models reply bit by bit")
print(next(words))
print(next(words))
print(list(words))


# Context managers
@contextmanager
def step(name):
    """Print a message before and after a block of code."""
    print(f"Start {name}")
    try:
        yield
    finally:
        print(f"End {name}")


with step("loading"):
    print("Working")

try:
    with step("risky work"):
        raise ValueError("Something went wrong")
except ValueError as error:
    print("Caught:", error)
