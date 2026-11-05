# In this chapter's sales_tools.py, make the same change:
@tool
def read_file(filename: Annotated[str, "File path, such as sales/monday.txt"]) -> str:
    """Read a text file."""
    return (WORKSPACE / filename).read_text()
