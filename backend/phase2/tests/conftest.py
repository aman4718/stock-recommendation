"""
conftest.py — Shared pytest fixtures for Phase 2 tests.
"""

import sys
import os
import json
import pytest

# ── Make phase2/ importable ─────────────────────────────────────
PHASE2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PHASE2_DIR not in sys.path:
    sys.path.insert(0, PHASE2_DIR)


# ─────────────────────────────────────────────────────────────────
# Sample document fixtures
# ─────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_document():
    return {
        "id": "AAPL",
        "text": (
            "Stock: Apple Inc. (AAPL)\n"
            "Sector: Technology\n"
            "Industry: Consumer Electronics\n"
            "Current Price: $175.50\n"
            "PE Ratio (Trailing): 28.4\n"
            "Market Cap: $2.75T\n"
            "Risk Level: Moderate\n"
            "Valuation Category: Growth / Premium\n"
            "Dividend Yield: 0.52%\n"
            "Price Change (1 Month): +3.25%\n"
            "Business Summary: Apple Inc. designs consumer electronics."
        ),
        "metadata": {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "price": 175.50,
            "pe_ratio": 28.4,
            "market_cap": "$2.75T",
            "risk_level": "Moderate",
            "valuation": "Growth / Premium",
            "price_change_1mo": 3.25,
            "dividend_yield": "0.52%",
            "fetched_at": "2024-01-15T10:00:00",
        },
    }


@pytest.fixture
def sample_document_with_none_metadata():
    """Document whose metadata contains None values (must be sanitised)."""
    return {
        "id": "TSLA",
        "text": "Stock: Tesla Inc. (TSLA)\nSector: Consumer Cyclical",
        "metadata": {
            "ticker": "TSLA",
            "name": "Tesla, Inc.",
            "sector": "Consumer Cyclical",
            "price": None,           # None — must be sanitised
            "pe_ratio": None,        # None
            "risk_level": "High",
            "valuation": "Growth / Premium",
            "price_change_1mo": -12.5,
            "dividend_yield": None,  # None
            "fetched_at": "2024-01-15T10:00:00",
        },
    }


@pytest.fixture
def three_documents(sample_document, sample_document_with_none_metadata):
    doc3 = {
        "id": "JNJ",
        "text": "Stock: Johnson & Johnson (JNJ)\nSector: Healthcare",
        "metadata": {
            "ticker": "JNJ",
            "name": "Johnson & Johnson",
            "sector": "Healthcare",
            "price": 155.0,
            "pe_ratio": 12.5,
            "risk_level": "Low",
            "valuation": "Undervalued",
            "price_change_1mo": -1.5,
            "dividend_yield": "3.00%",
            "fetched_at": "2024-01-15T10:00:00",
        },
    }
    return [sample_document, sample_document_with_none_metadata, doc3]


@pytest.fixture
def documents_json_file(tmp_path, three_documents):
    """Write three_documents to a temp JSON file."""
    path = tmp_path / "stock_documents.json"
    path.write_text(json.dumps(three_documents), encoding="utf-8")
    return str(path)
