"""Chapter 10 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import json


def request_schema(tool_names):
    """TODO 1: Return a schema for an object with two required fields:
    "tool", a string that can only be one of tool_names, and "arguments", an object.
    Tip: chapter 08's label_schema did the same job with one field.
    """
    return None


def read_request(reply):
    """TODO 2: reply is JSON text, like '{"tool": "read_file", "arguments": {"path": "a.txt"}}'.
    Return the tool name and the arguments as a pair: ("read_file", {"path": "a.txt"}).
    """
    return None


def run_tool(tools, name, arguments):
    """TODO 3: tools is a dict from tool name to function. Look up the function, call it with
    the arguments, and return the result as a string. Tip: function(**arguments).
    """
    return None


def safe_run_tool(tools, name, arguments):
    """TODO 4: Call run_tool and return its result, but never crash. If there's no such tool,
    return "Error: there is no tool called <name>". If the tool raises an exception,
    return "Error: <the exception>".
    """
    return None


def round_trip(question, chat, tools):
    """TODO 5: Do one full round trip, and return the final answer.
    1. Call chat with one user message containing the question. The reply is a tool request.
    2. Read the request, and run the tool safely.
    3. Add the reply to the messages as an assistant message.
    4. Add a user message containing the result.
    5. Call chat again, and return its reply.
    chat takes a list of messages and returns text. The tests use a fake one.
    """
    return None
