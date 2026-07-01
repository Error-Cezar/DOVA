from langchain.tools import tool

from typing import Any
agent: Any

@tool()
def stop_interaction() -> str:
    """
    Ending tool. Stops the agent from listening and ends the interaction. Use this when the user indicates they are done or wants to stop the conversation.
    """
    return agent.await_tool("stop_interaction")


tools = [stop_interaction]
