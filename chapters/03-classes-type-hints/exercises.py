"""Chapter 03 exercises. Complete each TODO, then run: python3 exercises.py"""
from dataclasses import dataclass, field


class Item:
    """TODO 1: Add __init__(self, name, price), and a label() method.
    Item("Tea", 80).label() returns "Tea: 80".
    """


@dataclass
class ToolCall:
    """TODO 2: Add two fields: name, a str, and arguments, a dict that starts empty."""


@dataclass
class Chat:
    messages: list[str] = field(default_factory=list)

    def add(self, text: str) -> None:
        """TODO 3: Add the text to messages."""

    def last(self) -> str | None:
        """TODO 3: Return the last message, or None if there aren't any."""


class Tool:
    name = "tool"

    def run(self, a, b):
        raise NotImplementedError


class AddTool(Tool):
    """TODO 4: Set name to "add", and make run return a + b."""


def area(width, height):
    """TODO 5: Add type hints. Both inputs and the result are floats."""
    return width * height


# ---- Self-check: you don't need to change anything below this line. ----


def check_item():
    assert Item("Tea", 80).label() == "Tea: 80", 'label() should return "Tea: 80"'
    assert Item("Coffee", 120).price == 120


def check_tool_call():
    assert ToolCall("add").arguments == {}
    assert ToolCall("add", {"a": 1}).name == "add"
    first = ToolCall("add")
    first.arguments["a"] = 1
    assert ToolCall("add").arguments == {}, "each ToolCall needs its own dict"


def check_chat():
    chat = Chat()
    assert chat.last() is None, "last() should return None for an empty chat"
    chat.add("Hello")
    chat.add("Bye")
    assert len(chat.messages) == 2, "add() should store each message"
    assert chat.last() == "Bye", "last() should return the newest message"


def check_add_tool():
    tool = AddTool()
    assert tool.name == "add", f'name is "{tool.name}", expected "add"'
    assert tool.run(2, 3) == 5, "run(2, 3) should return 5"


def check_area():
    hints = area.__annotations__
    expected = {"width": float, "height": float, "return": float}
    assert hints == expected, f"area has hints {hints}"


if __name__ == "__main__":
    checks = [("TODO 1: Item", check_item), ("TODO 2: ToolCall", check_tool_call),
              ("TODO 3: Chat", check_chat), ("TODO 4: AddTool", check_add_tool),
              ("TODO 5: area", check_area)]
    passed = 0
    for label, check in checks:
        try:
            check()
            passed += 1
            print(f"PASS  {label}")
        except Exception as error:
            print(f"FAIL  {label}: {type(error).__name__}: {error}")
    print(f"{passed}/{len(checks)} passed")
