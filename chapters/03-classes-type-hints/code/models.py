"""Classes, dataclasses and type hints."""
from dataclasses import dataclass, field


# A class
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


# A dataclass
@dataclass
class Message:
    role: str
    content: str


message = Message("user", "Hello")
print(message)
print(message == Message("user", "Hello"))


# A dataclass with a default and methods
@dataclass
class Conversation:
    messages: list[Message] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.messages.append(Message(role, content))

    def last(self) -> Message | None:
        return self.messages[-1] if self.messages else None


conversation = Conversation()
print(conversation.last())
conversation.add("user", "Hi")
conversation.add("assistant", "Hello!")
print(len(conversation.messages), conversation.last().content)


# Type hints
def shorten(text: str, limit: int = 10) -> str:
    """Return text cut down to the limit."""
    return text[:limit]


print(shorten("Whitebox Academy"))
print(shorten.__annotations__)


# Inheritance
class Tool:
    """The shape that every tool shares."""

    name = "tool"

    def run(self, text: str) -> str:
        raise NotImplementedError


class UpperTool(Tool):
    name = "upper"

    def run(self, text: str) -> str:
        return text.upper()


class ReverseTool(Tool):
    name = "reverse"

    def run(self, text: str) -> str:
        return text[::-1]


for tool in [UpperTool(), ReverseTool()]:
    print(tool.name, tool.run("agent"))
