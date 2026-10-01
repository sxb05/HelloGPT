import math

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = "TAVILY_API_KEY"


CURRENT_THID = "default"
def set_current_thid(thid: str):
    global CURRENT_THID
    CURRENT_THID = thid