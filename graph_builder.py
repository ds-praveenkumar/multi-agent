
from prompt import *
from langgraph.prebuilt import create_react_agent
from gemini import GeminiLangchain

llm = GeminiLangchain()

from typing import Literal

from langchain_core.tools import tool

@tool
def search(query: str):
    """Call to surf the web."""
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

graph = create_react_agent(llm.llm, tools=[search])
inputs = {"messages": [("user", "what is the weather in sf")]}
print_stream(graph.stream(inputs, ))