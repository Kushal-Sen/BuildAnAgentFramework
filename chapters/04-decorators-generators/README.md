# Chapter 04: Decorators, generators and context managers

**Time:** about 2 hours. **You'll learn:** flexible arguments, decorators, generators and
context managers.

## Where we are

In chapter 03, you organized code with classes and type hints. This chapter covers three Python
features that look unusual at first. Your framework depends on all three:

| Feature | What it does | Where you'll use it |
|---|---|---|
| Decorator | Adds behavior to a function | Turning a function into a tool |
| Generator | Gives back values one at a time | Streaming a model's reply |
| Context manager | Runs setup and cleanup around code | Tracing and timing each step |

## Run it

From `chapters/04-decorators-generators/code`, run:

```bash
python3 power_tools.py
```

```text
(1, 2) {'name': 'Tea'}
5
Calling multiply with (4, 5)
20
multiply - Multiply two numbers.
['greet', 'shout']
Hello, Asha!
Models
reply
['bit', 'by', 'bit']
Start loading
Working
End loading
Start risky work
End risky work
Caught: Something went wrong
```

Open [code/power_tools.py](code/power_tools.py) and follow along.

## Flexible arguments

`*args` collects extra positional values into a tuple, which is like a list you can't change.
`**kwargs` collects extra named values into a dictionary.

```python
def show(*args, **kwargs):
    print(args, kwargs)


show(1, 2, name="Tea")
```

It works the other way too. `**` unpacks a dictionary into named arguments:

```python
arguments = {"a": 2, "b": 3}
print(add(**arguments))
```

This is how an agent runs a tool. The model sends the arguments as a dictionary, and your code
calls `tool(**arguments)`. You'll write that line in chapter 10.

## Decorators

In Python, a function is a value. You can pass one to another function, and return one too.

A **decorator** takes a function and returns a new function with extra behavior:

```python
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
```

`@log_calls` is a shortcut for `multiply = log_calls(multiply)`. When you call `multiply`, you're
really calling `wrapper`, which then calls the original.

`functools.wraps` keeps the original's name and docstring. Without it, `multiply.__name__` would
say `wrapper`.

## A decorator that registers tools

A decorator doesn't have to wrap anything. This one stores the function, then gives it back
unchanged:

```python
TOOLS = {}


def tool(function):
    """Add a function to the list of tools."""
    TOOLS[function.__name__] = function
    return function


@tool
def greet(name):
    return f"Hello, {name}!"
```

Adding `@tool` is all it takes, and `TOOLS["greet"]` can now find the function by name. In
chapter 14, you'll build your framework's tool system this way.

## Generators

A normal function returns once and finishes. A **generator** uses `yield` to give back one value
at a time, and pauses in between:

```python
def stream_words(text):
    """Give back one word at a time."""
    for word in text.split():
        yield word


words = stream_words("Models reply bit by bit")
print(next(words))
print(next(words))
print(list(words))
```

`next` gets the next value, and `list` collects whatever is left. A `for` loop works too.

Models send their replies piece by piece, in just this way. In chapter 15, you'll show each piece
as it arrives.

A generator can only be used once. After it runs out, it stays empty.

## Context managers

A **context manager** runs setup before a block of code and cleanup after it, even if something
goes wrong. You use it with `with`. Python's `open` is a common example:

```python
with open("notes.txt") as file:
    print(file.read())
```

The file closes automatically. You can write your own with `@contextmanager`:

```python
@contextmanager
def step(name):
    """Print a message before and after a block of code."""
    print(f"Start {name}")
    try:
        yield
    finally:
        print(f"End {name}")
```

Code before `yield` is the setup, the `with` block runs at `yield`, and code after it is the
cleanup. **`finally` always runs**, even after an error. That's why the output shows
`End risky work` before `Caught: Something went wrong`.

## Reading errors

These are real results. Two of them show no error message at all:

| What you did | What happens | The fix |
|---|---|---|
| Forgot `return wrapper` | `TypeError: 'NoneType' object is not callable` | Return the wrapper from the decorator |
| Forgot `return` inside the wrapper | No error, but every call gives `None` | Return the function's result |
| Called `next` on a finished generator | `StopIteration` | Use a `for` loop, or create a new generator |
| Reused a finished generator | No error, but `list` gives `[]` | Create a new generator |
| Passed a key the function doesn't have | `TypeError: add() got an unexpected keyword argument 'c'` | Match the dictionary's keys to the parameters |
| Forgot `yield` in a context manager | `TypeError: 'NoneType' object is not an iterator` | Add `yield` |

## Exercises

Open [exercises.py](exercises.py) and complete the five TODOs:

1. `double_result`: write a decorator that wraps a function.
2. `register`: write a decorator that stores a function.
3. `call_tool`: call a function with a dictionary of arguments.
4. `evens`: write a generator.
5. `tracked`: write a context manager with guaranteed cleanup.

Then check your work:

```bash
python3 exercises.py
```

You've finished when you see `5/5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- Writing `@log_calls()` with brackets on a decorator that doesn't take options.
- Forgetting `functools.wraps`, which loses the function's name and docstring.
- Expecting to loop over a generator twice.
- Putting cleanup after `yield` without `try` and `finally`. It won't run after an error.

## Recap

- `*args` and `**kwargs` collect arguments, and `**` unpacks a dictionary.
- A decorator takes a function and returns one with extra behavior.
- A generator uses `yield` to give back values one at a time.
- A context manager guarantees setup and cleanup.

## Where this comes from

Generators arrived in Python 2.2, decorators in 2.4 and the `with` statement in 2.5. To learn
more, see the official guide to
[contextlib](https://docs.python.org/3/library/contextlib.html).

**Next:** chapter 05, where you'll learn virtual environments, packages, pytest and HTTP.
