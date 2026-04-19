"""
data_processor.py — Phase 1, Steps 2 & 3
  Step 2: Normalize raw data → add derived fields (risk, valuation, formatted caps)
  Step 3: Convert processed records → plain-text RAG documents
"""

import json
import os
from loguru import logger

from phase1.config import (
    BETA_HIGH_THRESHOLD,
    BETA_LOW_THRESHOLD,
    DATA_DIR,
    DESCRIPTION_MAX_CHARS,
    DOCUMENTS_FILE,
    PE_FAIR_MAX,
    PE_UNDERVALUED_MAX,
    PROCESSED_DATA_FILE,
)


# ─────────────────────────────────────────────────────────────────
# Classification helpers
# ─────────────────────────────────────────────────────────────────

def classify_risk(beta) -> str:
    """Map beta to a human-readable risk label."""
    if beta is None:
        return "Unknown"
    if beta < BETA_LOW_THRESHOLD:
        return "Low"
    if beta < BETA_HIGH_THRESHOLD:
        return "Moderate"
    return "High"


def classify_valuation(pe) -> str:
    """Map PE ratio to a valuation label."""
    if pe is None:
        return "Unknown"
    if pe < PE_UNDERVALUED_MAX:
        return "Undervalued"
    if pe < PE_FAIR_MAX:
        return "Fairly Valued"
    return "Growth / Premium"


def format_market_cap(market_cap) -> str:
    """Format raw market cap integer to human-readable string."""
    if market_cap is None:
        return "N/A"
    if market_cap >= 1_000_000_000_000:
        return f"${market_cap / 1_000_000_000_000:.2f}T"
    if market_cap >= 1_000_000_000:
        return f"${market_cap / 1_000_000_000:.2f}B"
    if market_cap >= 1_000_000:
        return f"${market_cap / 1_000_000:.2f}M"
    return f"${market_cap:,}"


def format_pct(value, decimals: int = 2) -> str:
    """Convert a fraction (0.05) to a percentage string ('5.00%')."""
    if value is None:
        return "N/A"
    return f"{value * 100:.{decimals}f}%"


def format_price_change(change) -> str:
    """Return a signed percentage string for 1-month price change."""
    if change is None:
        return "N/A"
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.2f}%"


# ─────────────────────────────────────────────────────────────────
# Step 2 — Normalise
# ─────────────────────────────────────────────────────────────────

def process_stocks(raw_stocks: list[dict]) -> list[dict]:
    """
    Enrich each raw stock record with derived / formatted fields.
    Returns the processed list and saves it to PROCESSED_DATA_FILE.
    """
    processed = []

    for stock in raw_stocks:
        enriched = {
            **stock,
            # --- derived classification fields ---
            "risk_level":           classify_risk(stock.get("beta")),
            "valuation_category":   classify_valuation(stock.get("pe_ratio")),
            # --- human-readable formatted fields ---
            "market_cap_formatted": format_market_cap(stock.get("market_cap")),
            "dividend_yield_pct":   format_pct(stock.get("dividend_yield")),
            "revenue_growth_pct":   format_pct(stock.get("revenue_growth")),
            "profit_margin_pct":    format_pct(stock.get("profit_margins")),
            "price_change_fmt":     format_price_change(stock.get("price_change_1mo")),
        }
        processed.append(enriched)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROCESSED_DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(processed, fh, indent=2, default=str)

    logger.success(f"Processed data → {PROCESSED_DATA_FILE}  ({len(processed)} records)")
    return processed


# ─────────────────────────────────────────────────────────────────
# Step 3 — Convert to RAG documents
# ─────────────────────────────────────────────────────────────────

DOCUMENT_TEMPLATE = """\
Stock: {name} ({ticker})
Sector: {sector}
Industry: {industry}
Current Price: {price}
PE Ratio (Trailing): {pe_ratio}
Forward PE: {forward_pe}
Market Cap: {market_cap}
52-Week Range: {low_52} – {high_52}
Beta: {beta}
Risk Level: {risk_level}
Valuation Category: {valuation}
Dividend Yield: {dividend_yield}
EPS (Trailing): {eps}
Revenue Growth: {revenue_growth}
Profit Margin: {profit_margin}
Price Change (1 Month): {price_change}
Business Summary: {description}
"""


def _fmt(value, prefix: str = "", suffix: str = "", fallback: str = "N/A") -> str:
    """Small helper to safely format a value."""
    if value is None or value == "" or value == "N/A":
        return fallback
    return f"{prefix}{value}{suffix}"


def build_document_text(stock: dict) -> str:
    """Render the template for a single processed stock dict."""
    price = stock.get("current_price")

    return DOCUMENT_TEMPLATE.format(
        name          = stock.get("name", stock.get("ticker", "N/A")),
        ticker        = stock.get("ticker", "N/A"),
        sector        = stock.get("sector", "N/A"),
        industry      = stock.get("industry", "N/A"),
        price         = _fmt(price, prefix="$"),
        pe_ratio      = _fmt(stock.get("pe_ratio")),
        forward_pe    = _fmt(stock.get("forward_pe")),
        market_cap    = stock.get("market_cap_formatted", "N/A"),
        high_52       = _fmt(stock.get("fifty_two_week_high"), prefix="$"),
        low_52        = _fmt(stock.get("fifty_two_week_low"),  prefix="$"),
        beta          = _fmt(stock.get("beta")),
        risk_level    = stock.get("risk_level", "Unknown"),
        valuation     = stock.get("valuation_category", "Unknown"),
        dividend_yield= stock.get("dividend_yield_pct", "N/A"),
        eps           = _fmt(stock.get("eps"), prefix="$"),
        revenue_growth= stock.get("revenue_growth_pct", "N/A"),
        profit_margin = stock.get("profit_margin_pct", "N/A"),
        price_change  = stock.get("price_change_fmt", "N/A"),
        description   = (stock.get("description") or "")[:DESCRIPTION_MAX_CHARS],
    ).strip()


def convert_to_documents(processed_stocks: list[dict]) -> list[dict]:
    """
    Convert each processed stock into a RAG-ready document dict:
      {
        "id":       ticker symbol,
        "text":     plain-text document (fed to the embedder),
        "metadata": key fields for filtering / display
      }
    Saves to DOCUMENTS_FILE and returns the list.
    """
    documents = []

    for stock in processed_stocks:
        ticker = stock.get("ticker", "UNKNOWN")
        doc = {
            "id":   ticker,
            "text": build_document_text(stock),
            "metadata": {
                "ticker":           ticker,
                "name":             stock.get("name", ticker),
                "sector":           stock.get("sector", "N/A"),
                "industry":         stock.get("industry", "N/A"),
                "price":            stock.get("current_price"),
                "pe_ratio":         stock.get("pe_ratio"),
                "market_cap":       stock.get("market_cap_formatted", "N/A"),
                "risk_level":       stock.get("risk_level", "Unknown"),
                "valuation":        stock.get("valuation_category", "Unknown"),
                "price_change_1mo": stock.get("price_change_1mo"),
                "dividend_yield":   stock.get("dividend_yield_pct", "N/A"),
                "description":      (stock.get("description") or "")[:500],
                "fifty_two_week_high": stock.get("fifty_two_week_high"),
                "fifty_two_week_low":  stock.get("fifty_two_week_low"),
                "eps":                 stock.get("eps"),
                "revenue_growth":      stock.get("revenue_growth_pct", "N/A"),
                "profit_margin":       stock.get("profit_margin_pct", "N/A"),
                "fetched_at":       stock.get("fetched_at", ""),
            },
        }
        documents.append(doc)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DOCUMENTS_FILE, "w", encoding="utf-8") as fh:
        json.dump(documents, fh, indent=2, default=str)

    logger.success(f"Documents → {DOCUMENTS_FILE}  ({len(documents)} documents)")
    return documents


# ─────────────────────────────────────────────────────────────────
# Load helpers (used by Phase 2+)
# ─────────────────────────────────────────────────────────────────

def load_processed_data() -> list[dict]:
    if not os.path.exists(PROCESSED_DATA_FILE):
        raise FileNotFoundError(f"Processed data not found: {PROCESSED_DATA_FILE}")
    with open(PROCESSED_DATA_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_documents() -> list[dict]:
    if not os.path.exists(DOCUMENTS_FILE):
        raise FileNotFoundError(f"Documents file not found: {DOCUMENTS_FILE}")
    with open(DOCUMENTS_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)
