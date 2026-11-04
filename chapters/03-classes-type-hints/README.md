# Chapter 03: Classes, dataclasses and type hints

**Time:** about 2 hours. **You'll learn:** classes, dataclasses, type hints and inheritance.

## Where we are

In chapter 02, you stored data in lists and dictionaries. Those work well, but a dictionary
can't stop you misspelling a key, and it can't carry its own behavior. Classes solve both.

You'll use these ideas throughout the framework: `Message` and `Conversation` hold an agent's
history, type hints describe its tools, and a shared base class lets you swap one model for another.

## Run it

From `chapters/03-classes-type-hints/code`, run:

```bash
python3 models.py
```

```text
Coffee 240
Message(role='user', content='Hello')
True
None
2 Hello!
Whitebox A
{'text': <class 'str'>, 'limit': <class 'int'>, 'return': <class 'str'>}
upper AGENT
reverse tnega
```

Open [code/models.py](code/models.py) and follow along.

## Classes

A **class** is a blueprint. It groups data with the functions that use that data. Each thing
you create from a class is called an **object**.

```python
class Order:
    """An order for one product."""

    def __init__(self, product, price, quantity):
        self.product = product
        self.price = price
        self.quantity = quantity

    def total(self):
        return self.price * self.quantity


order = Order("Coffee", 120, 2)
print(order.product, order.total())
```

- `__init__` runs when you create an object, and sets up its data.
- `self` means "this object". Python passes it in for you.
- `self.price` is an **attribute**, a value stored on the object.
- `total` is a **method**, a function that belongs to the class.

## Dataclasses

Many classes mostly hold data. A **dataclass** writes `__init__` for you. It also gives you
readable printing and lets you compare objects with `==`.

```python
@dataclass
class Message:
    role: str
    content: str
```

`@dataclass` is a **decorator**, which adds behavior to the class. You'll learn how decorators
work in chapter 04.

## Defaults and methods

A dataclass can have methods too. A list field needs `field(default_factory=list)`, so each
object gets its own new list:

```python
@dataclass
class Conversation:
    messages: list[Message] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.messages.append(Message(role, content))

    def last(self) -> Message | None:
        return self.messages[-1] if self.messages else None
```

`self.messages[-1]` is the last item in the list. The one-line `if` gives back the last message
if there is one, and `None` if the list is empty.

## Type hints

**Type hints** describe what a function takes and returns:

```python
def shorten(text: str, limit: int = 10) -> str:
    """Return text cut down to the limit."""
    return text[:limit]
```

| Hint | Meaning |
|---|---|
| `text: str` | `text` should be a string |
| `limit: int = 10` | `limit` should be a whole number, and defaults to 10 |
| `-> str` | The function returns a string |
| `-> None` | The function returns nothing |
| `Message \| None` | Either a `Message` or `None` |
| `list[Message]` | A list of `Message` objects |

**Python doesn't enforce type hints.** Nothing stops you calling `shorten(123)` with a number.
You only get an error if the code inside can't handle it, and here it can't:
`TypeError: 'int' object is not subscriptable`. Hints help people and tools read your code.

Your program can read them, though. `shorten.__annotations__` shows them as data:

```text
{'text': <class 'str'>, 'limit': <class 'int'>, 'return': <class 'str'>}
```

In chapter 14, you'll use this to describe tools to a model automatically.

## Inheritance

**Inheritance** lets a class build on another one. A base class defines the shape, and each
**subclass** fills in the details:

```python
class Tool:
    """The shape that every tool shares."""

    name = "tool"

    def run(self, text: str) -> str:
        raise NotImplementedError


class UpperTool(Tool):
    name = "upper"

    def run(self, text: str) -> str:
        return text.upper()
```

`raise NotImplementedError` stops the program with an error, which tells you a subclass must
provide that method.

Code that uses a `Tool` doesn't care which one it gets:

```python
for tool in [UpperTool(), ReverseTool()]:
    print(tool.name, tool.run("agent"))
```

In chapter 13, this same idea makes your model replaceable.

## Reading errors

These are real error messages:

| What you did | What Python says | The fix |
|---|---|---|
| Forgot `self` in a method | `TypeError: Order.total() takes 0 positional arguments but 1 was given` | Add `self` as the first parameter |
| Left out a value | `TypeError: Order.__init__() missing 1 required positional argument: 'price'` | Pass the value in |
| Wrote `price = price` instead of `self.price = price` | `AttributeError: 'Order' object has no attribute 'price'` | Store it on `self` |
| Used `[]` as a dataclass default | `ValueError: mutable default <class 'list'> for field messages is not allowed: use default_factory` | Use `field(default_factory=list)` |

## Exercises

Open [exercises.py](exercises.py) and complete the TODOs:

1. `Item`: write a class with `__init__` and a method.
2. `ToolCall`: write a dataclass with a default.
3. `Chat`: complete two methods.
4. `AddTool`: write a subclass.
5. `area`: add type hints.

Then check your work:

```bash
python3 exercises.py
```

You've finished when you see `5/5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- Forgetting `self` in a method, or forgetting `self.` when you store a value.
- Writing `Order` when you mean `Order()`. The brackets create the object.
- Using `[]` as a default instead of `field(default_factory=list)`.
- Expecting type hints to stop wrong values. They don't.

## Recap

- A class groups data with the functions that use it.
- A dataclass writes the setup code for you.
- Type hints describe your code, and your program can read them.
- Inheritance lets different classes share one shape.

## Where this comes from

Dataclasses arrived in Python 3.7, and type hints in Python 3.5. To learn more, see the official
guide to [classes](https://docs.python.org/3/tutorial/classes.html).

**Next:** chapter 04, where you'll learn decorators, generators and context managers.
