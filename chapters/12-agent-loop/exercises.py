"""Chapter 12 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""


def add(a, b):
    return a + b


TOOLS = {"add": add}


def run_tool(call):
    """Provided: run one tool call, as in chapter 11. Errors come back as text."""
    name = call["function"]["name"]
    if name not in TOOLS:
        return f"Error: there is no tool called {name}"
    try:
        return str(TOOLS[name](**call["function"]["arguments"]))
    except Exception as error:
        return f"Error: {error}"


def is_final(reply):
    """TODO 1: Return True if the reply is a final answer, which means it has no tool calls.
    The "tool_calls" key may be missing, or it may hold an empty list.
    """
    return None


def add_results(messages, calls):
    """TODO 2: For each call, run it with run_tool, and add this message to messages:
    {"role": "tool", "tool_name": <the tool's name>, "content": <the result>}
    """
    return None


def run_agent(question, chat, max_steps=3):
    """TODO 3: Start messages with one user message holding the question. Then, in a loop,
    call chat(messages) and add its reply to messages. If the reply is final, return its
    "content". If not, add the tool results and go round again. Use your functions above.

    TODO 4: Stop after max_steps, and return "Stopped: no answer after <max_steps> steps."
    """
    return None


def tools_used(messages):
    """TODO 5: Return the name of every tool the model asked for, in order. Tool requests
    are in the "tool_calls" of the assistant messages. Other messages don't have that key.
    """
    return None
