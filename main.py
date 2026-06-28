from langchain.messages import HumanMessage
import classes.agent as agent_class
from langchain_ollama import ChatOllama
from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig

import modules.printing as printing
import modules.voice as voice

import argparse
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
    skills=["./agent/skills/"],
    interrupt_data=interrupt_data
)

first_query = args.input
text_input = args.chat

while True:
    query = first_query or ""
    first_query = ""
    printing.info(f"Listening status is {agent.listening}")
    if not query:
        if text_input:
            query = input("Enter your query: ")
        else:
            detect = voice.run_detection()
            if detect["wake"]:
                printing.info("Wake word detected!")
                query = detect["detected"]
                agent.listening = True
            elif detect["normal"]:
                printing.info("Normal word detected!")
                query = agent.listening and detect["detected"] or ""
    if not query:
        continue
    agent.AddMessage(HumanMessage(query))
    agent.query()
