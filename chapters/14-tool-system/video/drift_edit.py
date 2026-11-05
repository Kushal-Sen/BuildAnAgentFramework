# In chapter 13's sales_tools.py, rename one parameter in the function:
def read_file(filename: str) -> str:
    """Read a text file inside the workspace."""
    return (WORKSPACE / filename).read_text()


# Leave the schema further down the same file as it was:
schema(
    "read_file",
    "Read a text file.",
    {"path": {"type": "string", "description": "File path, such as sales/monday.txt"}},
    ["path"],
),
