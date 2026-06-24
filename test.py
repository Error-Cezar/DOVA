# pip install -qU deepagents langchain-ollama
from deepagents import create_deep_agent
from langchain_ollama import ChatOllama

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

llm = ChatOllama(
    model="qwen3.5:4b",
    num_ctx=10000  # Request a larger context window
)

agent = create_deep_agent(
    model=llm,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# Run the agent
res = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)

print(res)
