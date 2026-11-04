"""Chapter 03 exercises, solved. Run: python3 solutions/exercises.py"""
from dataclasses import dataclass, field


class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def label(self):
        return f"{self.name}: {self.price}"


@dataclass
class ToolCall:
    name: str
    arguments: dict = field(default_factory=dict)


@dataclass
class Chat:
    messages: list[str] = field(default_factory=list)

    def add(self, text: str) -> None:
        self.messages.append(text)

    def last(self) -> str | None:
        return self.messages[-1] if self.messages else None


class Tool:
    name = "tool"

    def run(self, a, b):
        raise NotImplementedError


class AddTool(Tool):
    name = "add"

    def run(self, a, b):
        return a + b


def area(width: float, height: float) -> float:
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
