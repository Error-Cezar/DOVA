import webbrowser
from langchain.tools import tool

@tool()
def open_url(url):
    """Open a URL in the default web browser.

    Args:
        url (str): The URL to open."""
    try:
        webbrowser.open(url)
        return f"Opening in web browser."
    except Exception as e:
        return f"Error opening URL: {str(e)}"


def new_tab(url):
    """Open a URL in a new tab of the default web browser.

    Args:
        url (str): The URL to open."""
    try:
        webbrowser.open_new_tab(url)
        return f"Opening url in a new browser tab."
    except Exception as e:
        return f"Error opening URL in new tab: {str(e)}"

tools = [open_url, new_tab]
