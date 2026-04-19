import sys
import os
import json

# Ensure we can import from backend root
sys.path.append(os.getcwd())

from phase1.data_processor import process_stocks, convert_to_documents, load_processed_data, load_documents
from phase1.data_ingestion import load_raw_data
from phase2.vector_store import upsert_documents
from loguru import logger

def sync():
    try:
        logger.info("Starting metadata sync pipeline...")
        
        # 1. Load raw data and re-process to ensure all fields are in processed_stocks.json
        logger.info("Step 1: Re-processing raw data...")
        raw_stocks = load_raw_data()
        processed_stocks = process_stocks(raw_stocks)
        
        # 2. Convert to documents (this picks up the NEW metadata fields I just added)
        logger.info("Step 2: Converting processed stocks to RAG documents with enriched metadata...")
        documents = convert_to_documents(processed_stocks)
        
        # 3. Upsert to ChromaDB
        logger.info("Step 3: Upserting enriched documents to Chroma Cloud...")
        count = upsert_documents(documents, reset=True)
        
        logger.success(f"Successfully synced {count} documents with enriched metadata.")
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sync()
