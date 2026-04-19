"""
llm.py — Initializes the Groq Chat model using LangChain.
"""

from loguru import logger
from langchain_groq import ChatGroq
from phase3.settings import GROQ_API_KEY, LLM_MODEL

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            raise ValueError("Invalid GROQ_API_KEY. Please set it in backend/.env")
        
        logger.info(f"Initializing ChatGroq with model: {LLM_MODEL}")
        _llm = ChatGroq(
            temperature=0.1,  # Keep it grounded
            model_name=LLM_MODEL,
            groq_api_key=GROQ_API_KEY
        )
    return _llm
