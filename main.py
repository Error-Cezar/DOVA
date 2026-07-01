from langchain_ollama import ChatOllama
from langchain.agents.middleware import InterruptOnConfig
from langchain.messages import HumanMessage
import classes.agent as agent_class

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

import json, argparse, asyncio

import modules.printing as printing
import classes.connection as connection
from parser import parse

parser = argparse.ArgumentParser()
parse(parser)
args = parser.parse_args()

model = "gemma4:e4b"  # Specify the model you want to use
llm = ChatOllama(model=model, num_ctx=32000, temperature=.7)  # Request a larger context window

interrupt_data: dict[str, bool | InterruptOnConfig] = {
    "execute": {"allowed_decisions": ["approve", "reject"]},
    "ls": {"allowed_decisions": ["approve", "reject"]},
}

agent = agent_class.Agent(
    model=llm,
    interrupt_data=interrupt_data
)

# -------------------------
# -------------------------
# -------------------------

app = FastAPI()

manager = connection.ConnectionManager()

answer_event = asyncio.Event()
answer_data = None


async def websocket_heartbeat(websocket: WebSocket):
    while True:
        await asyncio.sleep(5)
        await manager.send_update({"type": "heartbeat"}, websocket)

@agent.on("stream")
async def onstream(content: str):
    await manager.send_update({"type": "stream", "content": content}, agent.websocket)

@agent.on("stream_end")
async def onend():
    await manager.send_update({"type": "stream_end", "content": ""}, agent.websocket)

@agent.on("interrupt")
async def oninterrupt(interrupt):
    answer_event.clear()
    answer_data = None
    value = None
    await manager.send_update({"type": "interrupt", "content": interrupt}, agent.websocket)
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
        await manager.send_update({"type": "connected", "content": "Hello World!"}, websocket)

        await manager.send_update({"type": "available"}, websocket)

        while True:
            data = await websocket.receive_text()
            try:
                data = json.loads(data)
            except:
                continue

            datatype, content = data.get("type"), data.get("content")
            printing.info(f"Got datatype: {datatype}")

            if datatype == "interrupt":
                global answer_data
                answer_data = content
                continue

            if datatype == "message":
                agent.AddMessage(HumanMessage(content))
                async def run_query():
                    await agent.query()
                    await manager.send_update({"type": "available"}, websocket)

                asyncio.create_task(run_query())
                continue

            if datatype == "tool":
                agent.tool_relay_content = content
                agent.tool_relay.set()
                continue

            if datatype == "test":
                print("content test:", content)
                await manager.send_update({"type": "test", "content": content}, websocket)
                continue

            printing.error(f"Invalid datatype: {datatype}")
    except WebSocketDisconnect:
        pass
    finally:
        if heartbeat_task is not None:
            heartbeat_task.cancel()
        if connected:
            manager.disconnect(websocket)
            if agent.websocket == websocket:
                agent.websocket = None
