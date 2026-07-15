from dova.parser import parse
from dova import server
from dova.modules import printing
from dova.classes import connection
from dova.classes.agent import Agent

from langchain_ollama import ChatOllama
from langchain.agents.middleware import InterruptOnConfig
from langchain.messages import HumanMessage

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

import json, argparse, asyncio

interrupt_data: dict[str, bool | InterruptOnConfig] = {
    "execute": {"allowed_decisions": ["approve", "reject"]},
    "ls": {"allowed_decisions": ["approve", "reject"]},
}

agent: Agent;

def main():
    parser = argparse.ArgumentParser()
    parse(parser)
    args = parser.parse_args()

    llm = ChatOllama(model=args.model, num_ctx=32000, temperature=.7)  # Request a larger context window
    agent = Agent(model=llm, interrupt_data=interrupt_data)

    app = server.run_server(agent)

    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
