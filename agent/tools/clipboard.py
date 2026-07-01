from langchain.tools import tool

from typing import Any
agent: Any

@tool()
def copy_to_clipboard(text: str):
    """Copy text to the clipboard.

    Args:
        text (str): The text to copy to the clipboard.
    """
    return agent.await_tool("copy_to_clipboard", text)

@tool()
def paste_from_clipboard() -> str:
    """Paste text from the clipboard."""
    return agent.await_tool("paste_from_clipboard")

tools = [copy_to_clipboard, paste_from_clipboard]
