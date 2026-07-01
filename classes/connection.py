import json
from fastapi import WebSocket

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

    async def send_update(self, content, websocket: WebSocket):
        await websocket.send_text(json.dumps(content))

    async def broadcast(self, message: str):
        for connection in self.connections:
            await connection.send_text(message)
