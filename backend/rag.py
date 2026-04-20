"""
rag.py — Loads scraped Groww FAQ embeddings from data/ and retrieves via cosine similarity.
Falls back to hardcoded knowledge.py if data/ files are absent.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from loguru import logger
from sentence_transformers import SentenceTransformer

DATA_DIR        = Path(__file__).parent / "data"
DOCS_FILE       = DATA_DIR / "docs.json"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.npy"

_model:      SentenceTransformer | None = None
_embeddings: np.ndarray | None         = None
_docs:       list[dict] | None         = None


def load() -> None:
    global _model, _embeddings, _docs
    if _model is not None:
        return

    logger.info("Loading sentence-transformer model ...")
    _model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    logger.success(f"Model ready | dim={_model.get_sentence_embedding_dimension()}")

    if DOCS_FILE.exists() and EMBEDDINGS_FILE.exists():
        with open(DOCS_FILE, encoding="utf-8") as f:
            _docs = json.load(f)
        _embeddings = np.load(str(EMBEDDINGS_FILE))
        logger.success(f"Loaded {len(_docs)} scraped chunks | shape={_embeddings.shape}")
    else:
        # Fallback: embed the hardcoded FAQ list
        logger.warning("Scraped data not found — using hardcoded FAQs. Run seed.py to scrape Groww.")
        from knowledge import FAQ_DATA
        _docs = [
            {"text": f"Q: {f['question']}\nA: {f['answer']}", "url": f["source"], "title": f["question"]}
            for f in FAQ_DATA
        ]
        texts = [d["text"] for d in _docs]
        _embeddings = _model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        logger.success(f"Fallback embeddings ready | {len(_docs)} FAQs")


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    if _model is None or _embeddings is None or _docs is None:
        raise RuntimeError("RAG not initialised — call rag.load() first.")

    q_vec  = _model.encode([query], normalize_embeddings=True, convert_to_numpy=True)
    scores = (_embeddings @ q_vec.T).flatten()
    top_i  = np.argsort(scores)[::-1][:top_k]

    results = []
    for i in top_i:
        d = _docs[int(i)]
        results.append({
            "text":  d["text"],
            "url":   d["url"],
            "title": d.get("title", ""),
            "score": float(scores[i]),
        })

    logger.debug(f"retrieve '{query[:50]}' | scores={[round(r['score'],3) for r in results]}")
    return results
