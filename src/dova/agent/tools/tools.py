from langchain.tools import tool

@tool()
def calculator(expression: str) -> str:
    """Performs arithmetic calculations. Use this for any math problems."""
    return str(eval(expression))

@tool()
def web_search(query: str):
    """Search the internet for information."""
    from modules.searxng import search
    response = search(query)
    return response

@tool()
def get_time() -> str:
    """Returns the current time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tools = [calculator, web_search, get_time]
