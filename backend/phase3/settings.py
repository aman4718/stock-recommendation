"""
config.py — Phase 3 Configuration
Loads environment variables and sets up paths.
"""

import os
import sys
from dotenv import load_dotenv

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load .env (we prefer the one in backend root)
load_dotenv(os.path.join(_BACKEND_DIR, ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
DEFAULT_TOP_K = 5
