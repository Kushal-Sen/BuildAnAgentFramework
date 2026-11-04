# Chapter 01: Python basics

**Time:** about 2.5 hours. **You'll learn:** values, variables, decisions, loops and functions.

Already know Python? Run `python3 exercises.py` and complete the TODOs. If you can finish
them quickly, skip to chapter 02.

## Where we are

In chapter 00, you set up Python and Ollama. Now you'll learn the Python you need to build
an agent. Every agent you build later uses the ideas in this chapter.

## Run your first program

A Python program is a text file of instructions. Python runs them from top to bottom.
From `chapters/01-python-basics/code`, run:

```bash
python3 basics.py
```

```text
Coffee 120 True
<class 'str'> <class 'int'> <class 'bool'>
Three Coffee orders cost 360.
Big order
Day 1
Day 2
Day 3
Orders left: 3
Orders left: 2
Orders left: 1
Tea order: 160
```

Open [code/basics.py](code/basics.py) beside this article. We'll go through it section by section.

## Values and variables

A **variable** is a name for a value. `=` stores the value on the right under the name on the left.

```python
product = "Coffee"
price = 120
in_stock = True
```

Each value has a **type**:

| Type | Meaning | Example |
|---|---|---|
| `str` | Text, called a string | `"Coffee"` |
| `int` | A whole number | `120` |
| `float` | A number with a decimal point | `19.5` |
| `bool` | True or false | `True` |

`print()` shows a value, and `type()` tells you its type.

## Working with values

Use `+`, `-`, `*` and `/` for arithmetic. Two more operators are useful: `//` divides and
drops the remainder, and `%` gives the remainder. So `7 % 2` is `1`.

An **f-string** puts values inside text. Put `f` before the quotes and the value in `{}`:

```python
total = price * 3
print(f"Three {product} orders cost {total}.")
```

## Decisions

`if` runs code only when a condition is true:

```python
if total >= 300:
    print("Big order")
elif total >= 100:
    print("Medium order")
else:
    print("Small order")
```

Python checks each condition in order and runs the first one that's true. Comparisons include
`==` (equal), `!=` (not equal), `<`, `<=`, `>` and `>=`.

The four spaces at the start of a line matter. **Indentation** tells Python which lines belong
to the `if`.

## Loops

A `for` loop repeats code for each value. `range(1, 4)` gives 1, 2 and 3, because it stops
before the second number.

```python
for day in range(1, 4):
    print("Day", day)
```

A `while` loop repeats as long as a condition is true:

```python
orders_left = 3
while orders_left > 0:
    print("Orders left:", orders_left)
    orders_left = orders_left - 1
```

If the condition never becomes false, the loop runs forever. Press `Ctrl+C` to stop it. You'll
meet this problem again in chapter 12, where an agent's loop needs a limit.

## Functions

A **function** is a named block of code you can reuse. It takes inputs, called **parameters**,
and `return` sends a result back.

```python
def order_cost(price, quantity):
    """Return the cost of an order."""
    return price * quantity


cost = order_cost(80, 2)
```

The text in triple quotes is a **docstring**, which explains what the function does. Later,
you'll see that an agent's tools are ordinary Python functions like this one.

## Reading errors

Errors are normal, and Python tells you what went wrong. Read the last line first, then the
line it points to. These are real errors:

**Mixing text and numbers:**

```text
    print("Price: " + price)
          ~~~~~~~~~~^~~~~~~
TypeError: can only concatenate str (not "int") to str
```

Fix it with an f-string: `print(f"Price: {price}")`.

**Forgetting to indent:**

```text
    print("Big order")
    ^^^^^
IndentationError: expected an indented block after 'if' statement on line 2
```

**Misspelling a name:**

```text
NameError: name 'prise' is not defined. Did you mean: 'price'?
```

**Using `print` instead of `return`:**

```text
TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
```

A function without `return` gives back `None`, which means "no value". `print` only shows a
value on screen, so the rest of your program can't use it.

## Exercises

Open [exercises.py](exercises.py) and complete the five TODOs:

1. `greet`: return a greeting.
2. `is_even`: check if a number is even. Use `%`.
3. `order_size`: choose a size with `if`.
4. `sum_to`: add numbers with a loop.
5. `discounted_price`: calculate a discount.

Then check your work:

```bash
python3 exercises.py
```

You've finished when you see `5/5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- Using `=` when you mean `==`. One stores a value, and the other compares.
- Forgetting the `:` at the end of `if`, `for`, `while` or `def`.
- Using `print` in a function when you need `return`.
- Expecting `range(1, 4)` to include 4.

## Recap

- Variables are names for values, and each value has a type.
- `if` makes decisions, and indentation shows what belongs to it.
- `for` and `while` repeat code.
- Functions take inputs and `return` a result.
- Read errors from the last line up.

## Where this comes from

Guido van Rossum released Python in 1991, with readable code as a main goal. For more practice,
try the official [Python tutorial](https://docs.python.org/3/tutorial/).

**Next:** chapter 02, where you'll work with collections, files, JSON and errors.
