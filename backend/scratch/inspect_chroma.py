import os
from loguru import logger
from phase2.vector_store import get_or_create_collection

def inspect_metadata():
    try:
        collection = get_or_create_collection()
        # Peek at some documents
        results = collection.peek(limit=5)
        
        logger.info("Inspection of first 5 documents in ChromaDB:")
        for i in range(len(results["ids"])):
            logger.info(f"ID: {results['ids'][i]}")
            logger.info(f"Metadata: {results['metadatas'][i]}")
            logger.info("-" * 20)
    except Exception as e:
        logger.error(f"Error inspecting metadata: {e}")

if __name__ == "__main__":
    inspect_metadata()
