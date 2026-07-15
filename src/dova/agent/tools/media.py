from langchain.tools import tool

from typing import Any
agent: Any

@tool()
def resume_playback():
    """Play/Resume media playback. Use when needing to start or resume a media."""
    return agent.await_tool("resume_playback")

@tool()
def pause_playback():
    """Pause/Stop media playback. Use when needing to pause or stop media."""
    return agent.await_tool("pause_playback")

@tool()
def next_playback():
    """Skip to the next media track. Use when needing to skip to the next media."""
    return agent.await_tool("next_playback")

@tool()
def previous_playback():
    """Go back to the previous media track. Use when needing to go back to the previous track."""
    return agent.await_tool("previous_playback")

tools = [resume_playback, pause_playback, next_playback, previous_playback]
