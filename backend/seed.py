"""
seed.py — One-shot script: scrape Groww → chunk → embed → save to data/.
Run this once locally, then commit data/ to git for Render deployment.

Usage:
    python seed.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from loguru import logger
from sentence_transformers import SentenceTransformer

load_dotenv()

from scraper import scrape_all

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DOCS_FILE       = DATA_DIR / "docs.json"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.npy"

CHUNK_SIZE    = 600   # chars per chunk
CHUNK_OVERLAP = 120


def _chunk(doc: dict) -> list[dict]:
    text = doc["content"]
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_SIZE
        piece = text[start:end].strip()
        if len(piece) > 80:
            chunks.append({
                "text":  piece,
                "url":   doc["url"],
                "title": doc["title"],
            })
        start = end - CHUNK_OVERLAP
    return chunks


def run():
    logger.info("=== Seed: scrape → chunk → embed → save ===")

    docs = scrape_all()
    if not docs:
        logger.error("Nothing scraped — check URLs/network and retry.")
        return

    chunks: list[dict] = []
    for doc in docs:
        chunks.extend(_chunk(doc))
    logger.info(f"Total chunks: {len(chunks)}")

    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
        batch_size=32,
    )

    with open(DOCS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    np.save(str(EMBEDDINGS_FILE), embeddings)

    logger.success(f"Saved {len(chunks)} chunks → {DOCS_FILE}")
    logger.success(f"Embeddings {embeddings.shape} → {EMBEDDINGS_FILE}")


if __name__ == "__main__":
    run()
