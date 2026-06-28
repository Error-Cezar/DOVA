import platform
import subprocess

from langchain.tools import tool

@tool()
def resume_playback():
    """Play/Resume media playback. Use when needing to start or resume a media."""
    try:
        system = platform.system()
        if system == "Linux":
            subprocess.run(["playerctl", "play"], check=True)
            return "Media playback playing."
        else:
            return f"Unsupported OS: {system}"

    except Exception as e:
        return f"Error playing media playback: {str(e)}"

@tool()
def pause_playback():
    """Pause/Stop media playback. Use when needing to pause or stop media."""
    try:
        system = platform.system()
        if system == "Linux":
            subprocess.run(["playerctl", "pause"], check=True)
            return "Media playback paused."
        else:
            return f"Unsupported OS: {system}"

    except Exception as e:
        return f"Error pausing media playback: {str(e)}"

@tool()
def next_playback():
    """Skip to the next media track. Use when needing to skip to the next media."""
    try:
        system = platform.system()
        if system == "Linux":
            subprocess.run(["playerctl", "next"], check=True)
            return "Skipped to next media track."
        else:
            return f"Unsupported OS: {system}"

    except Exception as e:
        return f"Error skipping to next media track: {str(e)}"

@tool()
def previous_playback():
    """Go back to the previous media track. Use when needing to go back to the previous track."""
    try:
        system = platform.system()
        if system == "Linux":
            subprocess.run(["playerctl", "previous"], check=True)
            return "Went back to previous media track."
        else:
            return f"Unsupported OS: {system}"

    except Exception as e:
        return f"Error going back to previous media track: {str(e)}"

tools = [resume_playback, pause_playback, next_playback, previous_playback]
