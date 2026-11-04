"""Chapter 11 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""


def multiply_schema():
    """TODO 1: Return the tool definition for a tool called multiply, in the same shape as
    the definitions in code/tools.py. Give it a description, and one required parameter,
    "numbers", which is an array of numbers.
    """
    return None


def requested_calls(reply):
    """TODO 2: Return the list of tool calls in the model's reply. If the reply has no
    "tool_calls" key, return an empty list.
    """
    return None


def run_tool(call, tools):
    """TODO 3: Run one tool call and return its result as a string. tools is a dict from
    tool name to function. If the name isn't in tools, return "Error: there is no tool
    called <name>". If the tool raises an exception, return "Error: <the exception>".
    """
    return None


def tool_message(call, result):
    """TODO 4: Return the message that gives a tool's result back to the model. It has
    three keys: "role", "tool_name" and "content".
    """
    return None


def round_trip(question, chat, tools):
    """TODO 5: Do one round trip, and return the model's final text.
    1. Build messages with one user message, and call chat(messages).
    2. Add the reply to messages. If it has no tool calls, return its "content".
    3. Run each tool call, and add a tool message for each one.
    4. Call chat(messages) again, and return the "content" of that reply.
    Use your functions from TODOs 2, 3 and 4.
    """
    return None
