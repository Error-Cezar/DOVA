import json
from fastapi import WebSocket
from langgraph.types import Interrupt
from typing import Any

class ConnectionManager:
    def __init__(self):
        self.Limit = 1
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        self.connections.clear()
        await websocket.accept()
        self.connections.append(websocket)
        return True

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def send_update(self, type: str, content: Any, websocket: WebSocket):
        if isinstance(content, Interrupt):
            content = content.value
        to_send = json.dumps({"type": type, "content": content})
        await websocket.send_text(to_send)

    async def broadcast(self, message: str):
        for connection in self.connections:
            await connection.send_text(message)
