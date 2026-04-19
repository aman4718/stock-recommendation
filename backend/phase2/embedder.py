"""
embedder.py — Phase 2, Step 1
Loads a HuggingFace sentence-transformer model and converts
text documents (or queries) into dense vector embeddings.
"""

import os
from loguru import logger
from sentence_transformers import SentenceTransformer

from phase2.config import EMBED_BATCH_SIZE, EMBEDDING_MODEL


# ─────────────────────────────────────────────────────────────────
# Model loader (singleton pattern — load once, reuse)
# ─────────────────────────────────────────────────────────────────

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """
    Return the sentence-transformer model, loading it on first call.
    Subsequent calls return the cached instance.
    """
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL} ...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.success(f"Model loaded — embedding dim: {_model.get_sentence_embedding_dimension()}")
    return _model


# ─────────────────────────────────────────────────────────────────
# Embedding functions
# ─────────────────────────────────────────────────────────────────

def embed_texts(texts: list[str], batch_size: int = EMBED_BATCH_SIZE) -> list[list[float]]:
    """
    Embed a list of text strings in batches.

    Args:
        texts:      List of plain-text strings to embed.
        batch_size: Number of texts to process per forward pass.

    Returns:
        List of embedding vectors (one per input text).
        Each vector is a list of floats (dim = 384 for MiniLM).
    """
    if not texts:
        return []

    model = get_model()
    logger.info(f"Embedding {len(texts)} texts in batches of {batch_size} ...")

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,   # unit-norm → cosine similarity = dot product
    )

    result = embeddings.tolist()
    logger.success(f"Embedded {len(result)} texts  |  dim={len(result[0]) if result else 0}")
    return result


def embed_query(query: str) -> list[float]:
    """
    Embed a single query string.
    Used at retrieval time (Phase 3).

    Args:
        query: Natural-language user query.

    Returns:
        Single embedding vector as a list of floats.
    """
    model = get_model()
    vector = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return vector[0].tolist()


def get_embedding_dimension() -> int:
    """Return the embedding dimension of the loaded model."""
    return get_model().get_sentence_embedding_dimension()
