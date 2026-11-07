"""The same tool sent to the model twice: as a local Tool, and as the Tool McpClient made. How many tokens does each cost?"""
import json
import sys

from library import all_documents, build_index
from whitebox import McpClient, Message, load_model, search_tool

model = load_model()
messages = [Message("user", "How much is the till float?")]
local = search_tool(build_index(all_documents(), 60))
with McpClient([sys.executable, "handbook_server.py"], timeout=120) as server:
    remote = server.tools()[0]
    for label, item in (("local", local), ("over MCP", remote)):
        read = model.chat(messages, [item], num_predict=1).tokens_in
        print(f"{label:<9} read {read} tokens. Parameters: {json.dumps(item.parameters)}")
