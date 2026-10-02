import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_tavily import TavilySearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq



from agent import get_agent

agent = get_agent("gemini-3.1-flash-lite")

config = {
    "configurable":{
        "thread_id": "test_thread",

    }
}

for message_chunk, metadata in agent.stream(
    {"messages": [HumanMessage(content="generate a blog about Ml")]},
    config=config,
    stream_mode="messages"
):
    if message_chunk.content:
        # Handle cases where content is returned as a structured list/dict from Gemini
        if isinstance(message_chunk.content, list):
            for part in message_chunk.content:
                if isinstance(part, dict) and "text" in part:
                    print(part["text"], end="", flush=True)
                elif isinstance(part, str):
                    print(part, end="", flush=True)
        # Handle cases where content is a clean, standard string
        elif isinstance(message_chunk.content, str):
            print(message_chunk.content, end="", flush=True)
