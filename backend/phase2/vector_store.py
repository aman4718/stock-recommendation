"""
vector_store.py — Phase 2, Step 2 & 3
Manages the ChromaDB Cloud collection:
  - Connect to Chroma Cloud
  - Create / get collection
  - Upsert documents + embeddings
  - Similarity search (used by Phase 3)
"""

import json
import os
from typing import Any, Optional
from loguru import logger

import chromadb
from chromadb.config import Settings

from phase2.config import (
    CHROMA_API_KEY,
    CHROMA_DATABASE,
    CHROMA_TENANT,
    COLLECTION_NAME,
    DEFAULT_TOP_K,
    DISTANCE_FUNCTION,
    DOCUMENTS_FILE,
)
from phase2.embedder import embed_query, embed_texts


# ─────────────────────────────────────────────────────────────────
# Client
# ─────────────────────────────────────────────────────────────────

_client: Optional[Any] = None


def get_client():
    """
    Return a ChromaDB Cloud client, creating it on first call.
    Credentials are read from .env via config.py.
    """
    global _client
    if _client is None:
        logger.info(
            f"Connecting to Chroma Cloud  "
            f"tenant={CHROMA_TENANT}  database={CHROMA_DATABASE} ..."
        )
        _client = chromadb.CloudClient(
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE,
            api_key=CHROMA_API_KEY,
        )
        logger.success("Chroma Cloud client connected.")
    return _client


# ─────────────────────────────────────────────────────────────────
# Collection
# ─────────────────────────────────────────────────────────────────

def get_or_create_collection(reset: bool = False):
    """
    Get the stock_vectors collection, optionally wiping it first.

    Args:
        reset: If True, deletes the collection before recreating it.
               Use this for daily ETL rebuilds (Phase 5 scheduler).

    Returns:
        chromadb.Collection instance
    """
    client = get_client()

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            logger.info(f"Collection '{COLLECTION_NAME}' deleted for rebuild.")
        except Exception:
            pass  # collection didn't exist yet — that's fine

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": DISTANCE_FUNCTION},
    )
    logger.info(
        f"Collection '{COLLECTION_NAME}' ready  "
        f"|  existing docs: {collection.count()}"
    )
    return collection


# ─────────────────────────────────────────────────────────────────
# Upsert
# ─────────────────────────────────────────────────────────────────

def upsert_documents(documents: list[dict], reset: bool = True) -> int:
    """
    Embed and upsert all documents into ChromaDB Cloud.

    Args:
        documents: List of {id, text, metadata} dicts from Phase 1.
        reset:     Whether to wipe the collection first (default: True).

    Returns:
        Number of documents successfully upserted.
    """
    if not documents:
        logger.warning("No documents to upsert.")
        return 0

    collection = get_or_create_collection(reset=reset)

    ids       = [doc["id"]       for doc in documents]
    texts     = [doc["text"]     for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]

    # ── Sanitise metadata: ChromaDB only accepts str / int / float / bool ──
    metadatas = [_sanitise_metadata(m) for m in metadatas]

    # ── Embed all texts ────────────────────────────────────────────
    embeddings = embed_texts(texts)

    # ── Upsert to Chroma Cloud ────────────────────────────────────
    logger.info(f"Upserting {len(ids)} documents to Chroma Cloud ...")
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    count = collection.count()
    logger.success(f"Upsert complete. Collection now has {count} documents.")
    return len(ids)


def _sanitise_metadata(meta: dict) -> dict:
    """
    ChromaDB metadata values must be str, int, float, or bool.
    Convert None → "" and anything else → str.
    """
    clean = {}
    for k, v in meta.items():
        if v is None:
            clean[k] = ""
        elif isinstance(v, (str, int, float, bool)):
            clean[k] = v
        else:
            clean[k] = str(v)
    return clean


# ─────────────────────────────────────────────────────────────────
# Search (used by Phase 3 RAG pipeline)
# ─────────────────────────────────────────────────────────────────

def similarity_search(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """
    Embed a query and retrieve the top-K most similar stock documents.

    Args:
        query:  Natural-language user query.
        top_k:  Number of results to return.

    Returns:
        List of result dicts:
        {
          "id":       ticker symbol,
          "text":     document text,
          "metadata": stock metadata,
          "distance": cosine distance (lower = more similar)
        }
    """
    collection = get_or_create_collection(reset=False)

    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "id":       results["ids"][0][i],
            "text":     results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": round(results["distances"][0][i], 6),
        })

    logger.info(f"Query: '{query}'  |  Retrieved {len(hits)} results")
    return hits


# ─────────────────────────────────────────────────────────────────
# Load documents from Phase 1 output
# ─────────────────────────────────────────────────────────────────

def load_documents_from_file(path: str = DOCUMENTS_FILE) -> list[dict]:
    """Load RAG documents produced by Phase 1."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Documents file not found: {path}\n"
            "Run Phase 1 first:  cd backend/phase1 && python main.py"
        )
    with open(path, "r", encoding="utf-8") as fh:
        docs = json.load(fh)
    logger.info(f"Loaded {len(docs)} documents from {path}")
    return docs


# ─────────────────────────────────────────────────────────────────
# Collection stats helper
# ─────────────────────────────────────────────────────────────────

def get_collection_stats() -> dict:
    """Return basic stats about the current collection."""
    collection = get_or_create_collection(reset=False)
    count = collection.count()
    return {
        "collection_name": COLLECTION_NAME,
        "document_count":  count,
        "embedding_model": "all-MiniLM-L6-v2",
        "database":        CHROMA_DATABASE,
        "tenant":          CHROMA_TENANT,
    }
