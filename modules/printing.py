from rich import print as rprint
from typing import Any

def error(content: Any):
    rprint("[italic red][ERROR]:[/italic red]", content)

def warn(content: Any):
    rprint("[italic yellow][WARN]:[/italic yellow]", content)

def info(content: Any):
    rprint("[italic cyan1][INFO]:[/italic cyan1]", content)
