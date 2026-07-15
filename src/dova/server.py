from dova.classes.agent import Agent
from dova.classes import connection
from dova.modules import printing

import asyncio
import json
import argparse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain.messages import HumanMessage

def run_server(agent: Agent):
    app = FastAPI()

    manager = connection.ConnectionManager()

    answer_event = asyncio.Event()
    answer_data = None

    async def websocket_heartbeat(websocket: WebSocket):
        while True:
            await asyncio.sleep(5)
            await manager.send_update("heartbeat", "", websocket)

    @agent.on("stream")
    async def onstream(content: str):
        await manager.send_update("stream", content, agent.websocket)

    @agent.on("stream_end")
    async def onend():
        await manager.send_update("stream_end", "", agent.websocket)

    @agent.on("interrupt")
    async def oninterrupt(interrupt):
        nonlocal answer_data
        answer_event.clear()
        answer_data = None
        value = None
        await manager.send_update("interrupt", interrupt, agent.websocket)
        try:
            await asyncio.wait_for(answer_event.wait(), timeout=10.0)
            value = answer_data
        except asyncio.TimeoutError:
            value = None
        return value or False

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        connected = False
        heartbeat_task = None
        if not await manager.connect(websocket):
            await websocket.close(code=4001, reason="Connection denied")
            print("connection denied")
            return

        try:
            connected = True
            agent.websocket = websocket
            agent.loop = asyncio.get_running_loop()
            heartbeat_task = asyncio.create_task(websocket_heartbeat(websocket))
            await manager.send_update("connected", "", websocket)

            await manager.send_update("available", "", websocket)

            while True:
                data = await websocket.receive_text()
                try:
                    data = json.loads(data)
                except:
                    continue

                datatype, content = data.get("type"), data.get("content")
                printing.info(f"Got datatype: {datatype}")

                if datatype == "interrupt":
                    nonlocal answer_data
                    answer_data = content
                    answer_event.set()
                    continue

                if datatype == "message":
                    agent.AddMessage(HumanMessage(content))
                    async def run_query():
                        await agent.query()
                        await manager.send_update("available", "", websocket)

                    asyncio.create_task(run_query())
                    continue

                if datatype == "tool":
                    agent.tool_relay_content = content
                    agent.tool_relay.set()
                    continue

                if datatype == "test":
                    print("content test:", content)
                    await manager.send_update("test", content, websocket)
                    continue

                printing.error(f"Invalid datatype: {datatype}")
        except WebSocketDisconnect:
            pass
        finally:
            if heartbeat_task is not None:
                heartbeat_task.cancel()
            if connected:
                manager.disconnect(websocket)

    return app
