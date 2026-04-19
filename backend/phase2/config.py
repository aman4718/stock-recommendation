"""
config.py — Phase 2 Configuration
Centralizes Chroma Cloud settings, embedding model, and collection name.
All secrets loaded from backend/.env via python-dotenv.
"""

import os
import sys
from dotenv import load_dotenv

# ── Load .env from backend/ root (works from any working directory) ─
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_BACKEND_DIR, ".env"))

# ── Shared data directory (same as Phase 1) ──────────────────────
DATA_DIR        = os.path.join(_BACKEND_DIR, "data")
DOCUMENTS_FILE  = os.path.join(DATA_DIR, "stock_documents.json")

# ── Chroma Cloud credentials (from .env) ─────────────────────────
CHROMA_API_KEY  = os.getenv("CHROMA_API_KEY",  "")
CHROMA_TENANT   = os.getenv("CHROMA_TENANT",   "")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "")

# ── Collection name inside ChromaDB ──────────────────────────────
COLLECTION_NAME = "stock_vectors"

# ── Embedding model (HuggingFace Sentence Transformers) ──────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # fast, 384-dim, great for retrieval

# ── Embedding batch size (to avoid OOM on large datasets) ────────
EMBED_BATCH_SIZE = 16

# ── Distance function for ChromaDB collection ────────────────────
# "cosine" is best for sentence-transformer embeddings
DISTANCE_FUNCTION = "cosine"

# ── Top-K results to return on similarity search ─────────────────
DEFAULT_TOP_K = 5
