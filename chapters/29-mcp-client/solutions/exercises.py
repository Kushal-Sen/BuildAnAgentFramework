"""Worked answers to the chapter 29 exercises."""
import json

from whitebox import McpClient, McpError, Tool, cosine


def read_reply(lines, number):
    """TODO 1: The heart of reply_to, with a list in place of the queue. lines holds strings from a server, in
    order. Return a pair: the first message whose "id" is number, as a dictionary, and a list of every line
    before it that wasn't JSON, each stripped of spaces and newlines. Skip messages with any other id. If the
    lines run out with no reply, raise McpError("The server has stopped").
    """
    noise = []
    for line in lines:
        try:
            message = json.loads(line)
        except ValueError:
            noise.append(line.strip())
            continue
        if isinstance(message, dict) and message.get("id") == number:
            return message, noise
    raise McpError("The server has stopped")


def to_tool(item, call):
    """TODO 2: The heart of as_tool. item is one tool from tools/list. Return a Tool an Agent can use: the same
    name, the description (or "" if there's none), and item["inputSchema"] as the parameters, with "required"
    set to [] if the server left it out. Running the Tool with keyword arguments must return
    call(name, arguments), where arguments is a dictionary of those keyword arguments.
    """
    name = item["name"]

    def run(**arguments):
        return call(name, arguments)

    return Tool(name, item.get("description", ""), {"properties": {}, "required": [], **item["inputSchema"]}, run)


def connect_all(commands, timeout=2):
    """TODO 3: One bad server shouldn't stop your agent. commands is a dictionary of label to command. For each,
    make an McpClient, call connect, and call tools. Return (clients, tools, problems): the clients that worked,
    all their Tools in one list, and a string "LABEL: MESSAGE" for each one that raised McpError, even if it was
    McpClient(...) itself, which raises when a program can't start. Call close on each one that started and then
    failed. Don't use "with" here, because the clients that worked must stay open.
    """
    clients, tools, problems = [], [], []
    for label, command in commands.items():
        client = None
        try:
            client = McpClient(command, timeout=timeout)
            client.connect()
            tools += client.tools()
            clients.append(client)
        except McpError as error:
            problems.append(f"{label}: {error}")
            if client:
                client.close()
    return clients, tools, problems


def named_tools(groups):
    """TODO 4: A Toolbox keeps one Tool per name, so two servers with a "search" tool would lose one. groups is a
    dictionary of a server's label to its Tools. Return one list of new Tools called LABEL_NAME, keeping each
    Tool's description, parameters and function. Don't change the Tools you were given.
    """
    return [Tool(f"{label}_{item.name}", item.description, item.parameters, item.function)
            for label, tools in groups.items() for item in tools]


def closest_tools(tools, question, k, embedder):
    """TODO 5: Forty tools cost tokens on every request, so offer only the k whose descriptions are closest to the
    question. Use embedder.embed_documents on the descriptions, embedder.embed_query on the question, and
    cosine(a, b) to score them. Return the k Tools with the highest scores, best first.
    """
    vectors = embedder.embed_documents([item.description for item in tools])
    wanted = embedder.embed_query(question)
    scored = sorted(zip(tools, vectors), key=lambda pair: cosine(pair[1], wanted), reverse=True)
    return [item for item, _ in scored[:k]]
