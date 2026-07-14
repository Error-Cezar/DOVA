from langchain.tools import tool

from typing import Any
agent: Any

@tool()
def execute(command: str):
    """Execute a shell command on the system.

    Args:
        command (str): The shell command to execute.
    """
    return agent.await_tool("execute", command)

@tool()
def get_system_type() -> str:
    """Get the current operating system."""
    return agent.await_tool("get_system_type")

tools = [execute, get_system_type]
