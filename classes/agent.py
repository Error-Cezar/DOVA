from langchain.tools import tool
from deepagents import create_deep_agent
from typing import Any
import sys
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from langchain.messages import AnyMessage, AIMessageChunk, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig
from deepagents.backends.local_shell import LocalShellBackend
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.utils.uuid import uuid7

import modules.renderer as renderer
import modules.safety as safeguard
import classes.speaker as speaker

import agent.tooling as tooling

from datetime import datetime

current_year = datetime.now().year
current_month = datetime.now().month
current_day = datetime.now().day
current_operating_system = sys.platform

current_formatted_date = f"{current_year}-{current_month:02d}-{current_day:02d}"

def_prompt = f"""
## System Context
- Current date: {current_formatted_date} [YEAR-MONTH-DAY]
- Operating system: {current_operating_system}
- You are: DOVA, a helpful voice assistant

## Response Guidelines
1. Be concise – Keep answers to 1–3 sentences for straightforward questions.
2. Use natural language – Speak conversationally, as you would to a friend.
3. Seek clarification – If a question is ambiguous, ask before responding.
4. Handle complexity – For involved topics, provide a brief answer and offer deeper explanation if needed.
5. Prioritize accuracy – Give truthful, honest responses. If you're uncertain, acknowledge it rather than guessing.

## Formatting Restrictions
1. Do not use markdown formatting (bold, italics, headers, lists, code blocks, etc.)
2. Do not use emojis or special symbols
3. Do not use line breaks or visual separators
4. Write in plain text only – as if speaking aloud

## Audio Optimization
1. Write for listening, not reading – Use short, natural sentences that flow when spoken
2. Avoid dense lists – Break complex ideas into simple, separate statements
3. Limit information density – Present one or two key points per response, offer to expand if asked
4. Use conversational pacing – Include natural pauses and transitions (like saying "So..." or "Here's the thing...")
5. Keep sentences short – Aim for 15-20 words per sentence to maintain clarity when heard

## Tool Specifications
1. When asked to type/write something, you are most likely asked to type it into the user's environment. If unsure, ask for clarification.
2. When using a tool, provide a brief explanation of what you are doing to allow audible feedback.

## User Engagement
1. End interactions by asking if the user needs anything else
2. Use natural follow-up phrases like "Is there anything else I can help with?"
3. Make the offer feel genuine, not robotic
4. When ending an interaction, express willingness to assist in the future and use the appropriate ending tool.
"""

speak = speaker.Speaker()

class Agent:
    def __init__(self, model: BaseChatModel, skills: list[str], interrupt_data: dict[str, bool | InterruptOnConfig]):
        self.listening: bool = True

        self.messages: list[AnyMessage] = []

        self.tools = tooling.Tools()
        self.tools.agent = self
        self.tools.load_all_tools()

        self.agent = create_deep_agent(
            model=model,
            skills=skills,
            tools=self.tools.tools,
            backend=LocalShellBackend(virtual_mode=True),
            system_prompt=def_prompt,
            checkpointer=MemorySaver(),
            middleware=[
                HumanInTheLoopMiddleware(interrupt_on=interrupt_data),
            ],
        )

        self.config: RunnableConfig = {"configurable": {"thread_id": str(uuid7())}}

    def AddMessage(self, Content: AnyMessage):
        self.messages.append(Content)

    def query(self, Decision: Any=None):
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
                    renderer.render_message_chunk(token)
                    speak.add_word(token.text)

            elif chunk["type"] == "updates":
                for source, update in chunk["data"].items():
                    if source in ("model", "tools"):
                        renderer.render_completed_message(update["messages"][-1])
                    if source == "__interrupt__":
                        interrupts.extend(update)

        print("\n")
        speak.tts_finish()
        self.AddMessage(AIMessage(final_message))

        if len(interrupts) > 0:
            for interrupt in interrupts:
                decisions[interrupt.id] = {
                    "decisions": safeguard.get_interrupt_decisions(interrupt)
                }
            print(decisions)
            self.query(Command(resume=decisions))
