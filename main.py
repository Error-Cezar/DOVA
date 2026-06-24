from typing import Any
from langgraph.types import Command, Interrupt
from deepagents import create_deep_agent
from deepagents.backends.local_shell import LocalShellBackend

from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig
from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langchain.messages import AIMessage, AIMessageChunk, AnyMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.utils.uuid import uuid7
from pathlib import Path

def _render_message_chunk(token: AIMessageChunk) -> None:
    if token.text:
        print(token.text, end="|")
    if token.tool_call_chunks:
        print(token.tool_call_chunks)
    # N.B. all content is available through token.content_blocks


def _render_completed_message(message: AnyMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        print(f"Tool calls: {message.tool_calls}")
    if isinstance(message, ToolMessage):
        print(f"Tool response: {message.content_blocks}")

def _get_interrupt_decisions(interrupt: Interrupt) -> list[dict]:
    full_res = []
    for request in interrupt.value["action_requests"]:
        print(request["description"])
        print("Confirm ? [y/n]")
        response = input().strip().lower()
        if response == "y":
            full_res.append({"type": "approve"})
        else:
           full_res.append({"type": "reject", "message": "User rejected the action."})
    return full_res

# qwen3:0.6b
# llama3.2:3b
# qwen2.5:0.5b
# ==========================
# AGENT CREATION
# ==========================
EXAMPLE_DIR = Path(__file__).parent
model = "qwen3.5:4b"
prompt = """
You are a helpful assistant.
Use the available skills tools to answer the user queries.
Only answer in a clear language that is clear of any kind of formatting, code blocks, or markdown.
"""

config: RunnableConfig = {"configurable": {"thread_id": str(uuid7())}}
checkpointer = MemorySaver()

llm = ChatOllama(model=model, num_ctx=10000)  # Request a larger context window

interrupt_data: dict[str, bool | InterruptOnConfig] = {
    "execute": {"allowed_decisions": ["approve", "reject"]},
    "ls": {"allowed_decisions": ["approve", "reject"]},
}

agent = create_deep_agent(
    model=llm,
    skills=["./skills/"],
    backend=LocalShellBackend(root_dir=EXAMPLE_DIR, virtual_mode=True),
    system_prompt=prompt,
    checkpointer=checkpointer,
    middleware=[
        HumanInTheLoopMiddleware(interrupt_on=interrupt_data),
    ],
)

# ==========================
# AGENT MESSAGES
# ==========================
messages: list[HumanMessage | AIMessage | SystemMessage] = []

def AddMessage(Content: HumanMessage | AIMessage | SystemMessage):
    messages.append(Content)

# ==========================
# AGENT QUERY
# ==========================
def query_agent(Decision: Any=None):
    interrupts = []
    In = Decision or {"messages": messages}
    stream = agent.stream(
        In,
        config=config,
        stream_mode=["messages", "updates"],
        version="v2",
    )
    for chunk in stream:
        if chunk["type"] == "messages":
            token, metadata = chunk["data"]
            if isinstance(token, AIMessageChunk):
                _render_message_chunk(token)
        elif chunk["type"] == "updates":
            for source, update in chunk["data"].items():
                if source in ("model", "tools"):
                    _render_completed_message(update["messages"][-1])
                if source == "__interrupt__":
                    interrupts.extend(update)

    decisions = {}
    if len(interrupts) > 0:
        for interrupt in interrupts:
            decisions[interrupt.id] = {
                "decisions": _get_interrupt_decisions(interrupt)
            }
        print(decisions)
        query_agent(Command(resume=decisions))


# Use agent
query="run ls on home and return the result"
AddMessage(HumanMessage(content=query))
print("QUERY")
query_agent()
print("END")
