"""
rag.py — Lightweight RAG using fastembed (ONNX, no torch) + numpy cosine similarity.
Loads pre-scraped chunks from data/; falls back to hardcoded FAQs if missing.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding
from loguru import logger

DATA_DIR        = Path(__file__).parent / "data"
DOCS_FILE       = DATA_DIR / "docs.json"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.npy"

_MODEL_NAME = "BAAI/bge-small-en-v1.5"   # 384-dim, ~67MB ONNX, no torch

_model:      TextEmbedding | None = None
_embeddings: np.ndarray | None    = None
_docs:       list[dict] | None    = None


def _embed(texts: list[str]) -> np.ndarray:
    vecs = np.array(list(_model.embed(texts)), dtype=np.float32)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / np.maximum(norms, 1e-9)


def load() -> None:
    global _model, _embeddings, _docs
    if _model is not None:
        return

    logger.info(f"Loading fastembed model: {_MODEL_NAME} ...")
    _model = TextEmbedding(_MODEL_NAME)
    logger.success("Embedding model ready.")

    if DOCS_FILE.exists() and EMBEDDINGS_FILE.exists():
        with open(DOCS_FILE, encoding="utf-8") as f:
            _docs = json.load(f)
        _embeddings = np.load(str(EMBEDDINGS_FILE))
        logger.success(f"Loaded {len(_docs)} scraped chunks | shape={_embeddings.shape}")
    else:
        logger.warning("No scraped data found — using hardcoded FAQs. Run seed.py to scrape Groww.")
        from knowledge import FAQ_DATA
        _docs = [
            {"text": f"Q: {f['question']}\nA: {f['answer']}", "url": f["source"], "title": f["question"]}
            for f in FAQ_DATA
        ]
        _embeddings = _embed([d["text"] for d in _docs])
        logger.success(f"Fallback embeddings ready | {len(_docs)} FAQs")


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    if _model is None or _embeddings is None or _docs is None:
        raise RuntimeError("RAG not initialised — call rag.load() first.")

    q_vec  = _embed([query])
    scores = (_embeddings @ q_vec.T).flatten()
    top_i  = np.argsort(scores)[::-1][:top_k]

    return [{
        "text":  _docs[int(i)]["text"],
        "url":   _docs[int(i)]["url"],
        "title": _docs[int(i)].get("title", ""),
        "score": float(scores[i]),
    } for i in top_i]
