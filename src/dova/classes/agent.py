from concurrent.futures import TimeoutError as FutureTimeoutError

from dova.modules import renderer

from dova.agent import tooling
from dova.agent import prompt

import threading
import time
import sys, asyncio, json

from typing import Any
from fastapi import WebSocket

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig

from langchain.messages import AnyMessage, AIMessageChunk, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel

from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.utils.uuid import uuid7
from langgraph.types import Command

def_prompt = prompt.prompt

class EventNotFoundError(Exception):
    """Custom exception raised when an event is not registered."""
    pass

class Agent:
    def __init__(self, model: BaseChatModel, interrupt_data: dict[str, bool | InterruptOnConfig]):
        self.listening: bool = True
        self.websocket: WebSocket
        self.loop: asyncio.AbstractEventLoop | None = None

        self.tool_relay = threading.Event()
        self.tool_relay_content = None

        self.connections = {
            "stream": [],
            "interrupt": [],
            "stream_end": [],
        }

        self.messages: list[AnyMessage] = []

        self.tools = tooling.Tools()
        self.tools.agent = self
        self.tools.load_all_tools()

        self.agent = create_agent(
            model=model,
            tools=self.tools.tools,
            system_prompt=def_prompt,
            checkpointer=MemorySaver(),
            middleware=[
                HumanInTheLoopMiddleware(interrupt_on=interrupt_data),
            ],
        )

        self.config: RunnableConfig = {"configurable": {"thread_id": str(uuid7())}}

    def await_tool(self, tool_name: str, *argv):
        print("running await tool")
        self.tool_relay_content = None
        self.tool_relay.clear()

        if self.loop is None:
            return None

        future = asyncio.run_coroutine_threadsafe(self.websocket.send_text(json.dumps({
            "type": "tool",
            "content": {
                "tool": tool_name,
                "arguments": argv
            }
        })), self.loop)

        value = None
        try:
            future.result(timeout=0.5)
            if self.tool_relay.wait(timeout=10.0):
                value = self.tool_relay_content
            else:
                value = None
        except FutureTimeoutError:
            value = None
        except Exception:
            value = None
        return value

    def _trigger_sync(self, event_name, *args, **kwargs):
        if self.loop is None:
            return False

        future = asyncio.run_coroutine_threadsafe(
            self._trigger(event_name, *args, **kwargs),
            self.loop,
        )
        return future.result()

    async def _trigger(self, event_name, *args, **kwargs):
        if event_name in self.connections:
            for listener in self.connections[event_name]:
                result = await listener(*args, **kwargs)
                if result != None: return result
            return False
        else:
            raise EventNotFoundError(f"Cannot trigger unknown event: '{event_name}'")


    def on(self, event_name):
        """Decorator to register a listener for a specific event."""
        def decorator(func):
            if event_name not in self.connections:
                raise EventNotFoundError(f"Event {event_name} does not exist")
            self.connections[event_name].append(func)

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def AddMessage(self, Content: AnyMessage):
        self.messages.append(Content)

    def _query_blocking(self, Decision: Any = None):
        interrupts, decisions = [], {}

        final_message = ""
        full_message = ""

        In = Decision or {"messages": self.messages}
        stream = self.agent.stream(
            In,
            config=self.config,
            stream_mode=["messages", "updates"],
            version="v2",
        )
        for chunk in stream:
            if chunk["type"] == "messages":
                token, _ = chunk["data"]
                if isinstance(token, AIMessageChunk):
                    full_message = token if full_message is None else full_message + token.text
                    if token.chunk_position == "last":
                        final_message = full_message
                    if token.text == "":
                        continue
                    renderer.render_message_chunk(token)
                    self._trigger_sync("stream", token.text)

            elif chunk["type"] == "updates":
                for source, update in chunk["data"].items():
                    if source in ("model", "tools"):
                        renderer.render_completed_message(update["messages"][-1])
                    if source == "__interrupt__":
                        interrupts.extend(update)

        self._trigger_sync("stream_end")
        print("\n")
        self.AddMessage(AIMessage(final_message))

        if len(interrupts) > 0:
            for interrupt in interrupts:
                result = self._trigger_sync("interrupt", interrupt)
                if result == False:
                    result = [{"type": "reject", "message": "Action has timed-out."}]
                decisions[interrupt.id] = {
                    "decisions": result
                }
            print(decisions)
            self._query_blocking(Command(resume=decisions))

    async def query(self, Decision: Any = None):
        await asyncio.to_thread(self._query_blocking, Decision)
