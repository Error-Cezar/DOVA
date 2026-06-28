from langchain.messages import AIMessage, AIMessageChunk, AnyMessage, ToolMessage

def render_message_chunk(token: AIMessageChunk) -> None:
    if token.text:
        print(token.text, end="")
    if token.tool_call_chunks:
        pass
        # print(token.tool_call_chunks)
    # N.B. all content is available through token.content_blocks

def render_completed_message(message: AnyMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        print(f"Tool calls: {message.tool_calls}")
    if isinstance(message, ToolMessage):
        print(f"Tool response: {message.content_blocks}")

def render_completed_message(message: AnyMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        print(f"Tool calls: {message.tool_calls}")
    if isinstance(message, ToolMessage):
        print(f"Tool response: {message.content_blocks}")
