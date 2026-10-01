import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_tavily import TavilySearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
