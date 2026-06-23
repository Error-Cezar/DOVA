from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver

# qwen3:0.6b
# llama3.2:3b
# qwen2.5:0.5b
# ==========================
# AGENT CREATION
# ==========================
model = "qwen3.5:4b"
prompt = "You are a helpful assistant. use the available skills tools to answer the user queries."
checkpointer = MemorySaver()
llm = ChatOllama(model=model)
agent = create_agent(
    model=llm,
    skills=["skills/"],
    system_prompt=prompt,
    checkpointer=checkpointer,
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
def query_agent():
    stream = agent.stream_events({"messages": messages}, version="v3")
    for message in stream.messages:
        print(f"[{message.node}] ", end="")
        for delta in message.text:
            print(delta, end="", flush=True)

        full_message = message.output
        usage = full_message.usage_metadata
        if usage:
            print(usage)

# Use agent
query="What are Common Architectural Scenarios in python?"
AddMessage(HumanMessage(content=query))
query_agent()