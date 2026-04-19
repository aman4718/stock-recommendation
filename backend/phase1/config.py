"""
config.py — Phase 1 Configuration
Centralizes all settings: tickers, paths, thresholds.
"""

import os

# ── Top stocks across major sectors ─────────────────────────────
STOCK_TICKERS = [
    # Technology
    "AAPL", "MSFT", "GOOGL", "NVDA", "META", "AMD", "TSLA",
    # Finance
    "JPM", "BAC", "GS", "V", "MA",
    # Healthcare
    "JNJ", "PFE", "UNH", "ABBV",
    # Consumer Discretionary
    "AMZN", "WMT", "COST", "MCD",
    # Energy
    "XOM", "CVX",
    # Industrials
    "CAT", "HON", "GE",
    # Telecom
    "T", "VZ",
    # ETFs (for diversification queries)
    "SPY", "QQQ",
]

# ── File paths ────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "data")

RAW_DATA_FILE       = os.path.join(DATA_DIR, "raw_stocks.json")
PROCESSED_DATA_FILE = os.path.join(DATA_DIR, "processed_stocks.json")
DOCUMENTS_FILE      = os.path.join(DATA_DIR, "stock_documents.json")

# ── Risk / Valuation thresholds ───────────────────────────────────
BETA_LOW_THRESHOLD      = 0.8    # beta < 0.8  → Low risk
BETA_HIGH_THRESHOLD     = 1.2    # beta > 1.2  → High risk

PE_UNDERVALUED_MAX      = 15     # PE < 15     → Undervalued
PE_FAIR_MAX             = 25     # 15 ≤ PE ≤ 25 → Fairly Valued
                                  # PE > 25     → Growth / Premium

# ── History window for price-change calculation ────────────────────
HISTORY_PERIOD = "1mo"           # yfinance period string

# ── Document text — max chars from business description ───────────
DESCRIPTION_MAX_CHARS = 600
