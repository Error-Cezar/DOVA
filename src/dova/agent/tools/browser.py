import webbrowser
from langchain.tools import tool

from typing import Any
agent: Any

@tool()
def open_url(url):
    """Open a URL in the default web browser.

    Args:
        url (str): The URL to open."""
    return agent.await_tool("open_url", url)


def new_tab(url):
    """Open a URL in a new tab of the default web browser.

    Args:
        url (str): The URL to open."""
    return agent.await_tool("open_url", url)

tools = [open_url, new_tab]
