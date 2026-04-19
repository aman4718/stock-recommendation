"""
main.py — Phase 3 Entry Point
Tests the end-to-end RAG logic via CLI.

Usage:
    cd backend/phase3
    python main.py
"""

import sys
from loguru import logger
from rag_pipeline import run_query

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    level="INFO",
    colorize=True,
)

def interactive_chat():
    banner = "=" * 60
    logger.info(banner)
    logger.info("  PHASE 3 — RAG Pipeline (Groq + LangChain + Chroma)")
    logger.info(banner)
    logger.info("Type 'quit' or 'exit' to stop.")
    
    while True:
        try:
            query = input("\nYou: ")
            if query.lower() in ['quit', 'exit']:
                break
            
            if not query.strip():
                continue
                
            response = run_query(query)
            
            print(f"\nAI:\n{response['answer']}")
            print(f"\nRecommendations (Tickers from Context): {', '.join(response['recommendations'])}")
            print("-" * 60)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        res = run_query(query)
        print(f"\nAI:\n{res['answer']}\n")
        print(f"Recs: {res['recommendations']}")
    else:
        interactive_chat()
