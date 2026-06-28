from pydantic import BaseModel, Field
from typing import Literal, Any

from langchain.tools import tool
import pyautogui

agent: Any

@tool("calculator", description="Performs arithmetic calculations. Use this for any math problems.")
def toolscalc(expression: str) -> str:
    """Evaluate mathematical expressions."""
    return str(eval(expression))

@tool("web_search", description="Searches the internet for information.")
def websearch(query: str):
    """Search the web for information."""
    from modules.searxng import search
    response = search(query)
    return response

@tool()
def keyboard_interact(query:str):
    """
    Simulates keyboard input based on the provided query. Use this to type/write inputs directly into the environment.

    Args:
        query: The string to be typed.
        interval: Time interval (in seconds) between each keystroke [defaults to 0.25].
    """
    pyautogui.write(query)
    return f"Query typed successfully."

@tool()
def get_time() -> str:
    """Returns the current time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool()
def stop_interaction() -> str:
    """
    Ending tool. Stops the agent from listening and ends the interaction. Use this when the user indicates they are done or wants to stop the conversation.
    """
    agent.listening = False
    return "Interaction has ended."

tools = [toolscalc, websearch, keyboard_interact, get_time, stop_interaction]
