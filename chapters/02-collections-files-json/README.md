# Chapter 02: Collections, files, JSON and errors

**Time:** about 2 hours. **You'll learn:** lists, dictionaries, files, JSON and handling errors.

## Where we are

In chapter 01, you learned values, decisions, loops and functions. Real programs work with
groups of data, and they save and load that data. This chapter covers both.

It matters for agents too. An agent's whole conversation is a list of dictionaries, and models
ask for tools using JSON.

## Run it

From `chapters/02-collections-files-json/code`, run:

```bash
python3 data_basics.py
```

```text
Coffee 3
Coffee 0
user: Hello
assistant: Hi! How can I help?
[240, 160, 190] 295
Order more coffee
480
{"name": "add", "arguments": {"a": 2, "b": 3}}
Error: missing.json doesn't exist
```

Open [code/data_basics.py](code/data_basics.py) and follow along.

## Lists

A **list** holds values in order. Positions start at 0, so `products[0]` is the first item.

```python
products = ["Coffee", "Tea"]
products.append("Juice")
print(products[0], len(products))
```

`append` adds an item to the end, and `len` counts the items.

## Dictionaries

A **dictionary** stores values under names, called **keys**.

```python
order = {"product": "Coffee", "quantity": 2}
order["price"] = 120
print(order["product"], order.get("discount", 0))
```

`order["product"]` needs the key to exist. `order.get("discount", 0)` is safer: it gives back
`0` if the key is missing.

## A list of dictionaries

This shape appears everywhere, and it's exactly how you'll store an agent's conversation:

```python
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"},
]
for message in messages:
    print(f"{message['role']}: {message['content']}")
```

## List comprehensions

A **list comprehension** builds a new list in one line:

```python
prices = [120, 80, 95]
print([price * 2 for price in prices], sum(prices))
```

You can also filter: `[price for price in prices if price > 90]` gives `[120, 95]`.

## Files

`Path` from the `pathlib` module works with files. It comes with Python, but you need to
`import` it.

```python
notes = HERE / "notes.txt"
notes.write_text("Order more coffee\n")
print(notes.read_text().strip())
```

`write_text` replaces whatever is in the file. `strip` removes spaces and line breaks from
both ends of the text.

## JSON

**JSON** is a text format for data. It looks like Python lists and dictionaries, and most
programs and web services can read it.

| Function | What it does |
|---|---|
| `json.loads(text)` | Turns JSON text into Python data |
| `json.dumps(data)` | Turns Python data into JSON text |

```python
orders = json.loads((HERE / "orders.json").read_text())
print(sum(item["price"] * item["quantity"] for item in orders))
print(json.dumps({"name": "add", "arguments": {"a": 2, "b": 3}}))
```

JSON has a few differences from Python: strings must use double quotes, and it uses `true`,
`false` and `null` where Python uses `True`, `False` and `None`.

## Handling errors

Some errors are expected, like a missing file. `try` and `except` let your program deal with
them and keep running.

```python
def read_json(path):
    """Return the data in a JSON file, or an error message."""
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        return f"Error: {path} doesn't exist"
```

Agents use this same pattern. When a tool fails, the error is returned as text, so the model
can read it and try something else.

Only catch errors you expect. A plain `except:` hides real bugs.

## Reading errors

These are real error messages:

| What happened | What Python says |
|---|---|
| The key isn't in the dictionary | `KeyError: 'price'` |
| The position is past the end of the list | `IndexError: list index out of range` |
| The JSON isn't valid | `JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)` |
| The file doesn't exist | `FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'` |

## Exercises

Open [exercises.py](exercises.py) and complete the five TODOs:

1. `total_quantity`: add up values from a list of dictionaries.
2. `get_price`: look up a value safely.
3. `in_stock`: filter a list with a list comprehension.
4. `save_and_load`: write JSON to a file and read it back.
5. `tool_name`: read JSON safely, and handle invalid JSON with `json.JSONDecodeError`.

Then check your work:

```bash
python3 exercises.py
```

You've finished when you see `5/5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- Starting from 1 instead of 0. The last item in a list of 3 is at position 2.
- Using `[]` for a key that might be missing. Use `.get()` instead.
- Mixing up `loads` and `dumps`. Text goes in to `loads`, and text comes out of `dumps`.
- Writing JSON with single quotes.

## Recap

- Lists hold values in order, and dictionaries store values under keys.
- A list of dictionaries is how an agent stores its conversation.
- `Path` reads and writes files.
- JSON turns data into text and back.
- `try` and `except` handle errors you expect.

## Where this comes from

Douglas Crockford popularized JSON in the early 2000s. To learn more, see the official guide
to [Python data structures](https://docs.python.org/3/tutorial/datastructures.html).

**Next:** chapter 03, where you'll learn classes, dataclasses and type hints.
