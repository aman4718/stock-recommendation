"""
retriever.py — Wrapper around Phase 2's ChromaDB similarity search.
"""

from phase3 import settings
from typing import List, Dict
from loguru import logger
from phase2.vector_store import similarity_search
from phase3.settings import DEFAULT_TOP_K

def retrieve_context(query: str, top_k: int = DEFAULT_TOP_K) -> List[Dict]:
    """Retrieve relevant stock documents from ChromaDB."""
    logger.info(f"Retrieving top {top_k} documents for query: '{query}'")
    results = similarity_search(query, top_k=top_k)
    return results

def format_context_for_prompt(results: List[Dict]) -> str:
    """Format similarity search results into a clean string for the LLM."""
    if not results:
        return "No relevant context found."
    
    parts = []
    for i, res in enumerate(results, 1):
        # res has "id", "text", "metadata", "distance"
        parts.append(f"--- Document {i} (Ticker: {res['id']}, Distance: {res['distance']}) ---")
        parts.append(res['text'])
        parts.append("")
    
    return "\n".join(parts)
