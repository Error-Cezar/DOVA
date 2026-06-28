import pyperclip
from langchain.tools import tool

@tool()
def copy_to_clipboard(text: str):
    """Copy text to the clipboard.

    Args:
        text (str): The text to copy to the clipboard.
    """
    pyperclip.copy(text)
    return "Text copied to clipboard."

@tool()
def paste_from_clipboard() -> str:
    """Paste text from the clipboard."""
    return pyperclip.paste()

tools = [copy_to_clipboard, paste_from_clipboard]
