import server
from langchain_ollama import ChatOllama
from langchain.agents.middleware import InterruptOnConfig
from langchain.messages import HumanMessage
import classes.agent as agent_class

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

import json, argparse, asyncio

import modules.printing as printing
import classes.connection as connection
from parser import parse

interrupt_data: dict[str, bool | InterruptOnConfig] = {
    "execute": {"allowed_decisions": ["approve", "reject"]},
    "ls": {"allowed_decisions": ["approve", "reject"]},
}

agent: agent_class.Agent;

# -------------------------
# -------------------------
# -------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parse(parser)
    args = parser.parse_args()

    llm = ChatOllama(model=args.model, num_ctx=32000, temperature=.7)  # Request a larger context window
    agent = agent_class.Agent(model=llm, interrupt_data=interrupt_data)

    app = server.run_server(agent)

    uvicorn.run(app, host=args.host, port=args.port)
