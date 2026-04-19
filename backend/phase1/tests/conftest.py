"""
conftest.py — Shared pytest fixtures for Phase 1 tests.
Adds the phase1/ directory to sys.path so all modules are importable.
"""

import sys
import os
import json
import pytest

# ── Make phase1/ importable ─────────────────────────────────────
PHASE1_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PHASE1_DIR not in sys.path:
    sys.path.insert(0, PHASE1_DIR)


# ─────────────────────────────────────────────────────────────────
# Shared sample data fixtures
# ─────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_raw_stock():
    """A minimal raw stock dict as returned by data_ingestion."""
    return {
        "ticker":              "AAPL",
        "name":                "Apple Inc.",
        "sector":              "Technology",
        "industry":            "Consumer Electronics",
        "current_price":       175.50,
        "pe_ratio":            28.4,
        "forward_pe":          25.1,
        "market_cap":          2_750_000_000_000,
        "fifty_two_week_high": 199.62,
        "fifty_two_week_low":  164.08,
        "beta":                1.1,
        "dividend_yield":      0.0052,
        "eps":                 6.43,
        "revenue_growth":      0.089,
        "profit_margins":      0.261,
        "description":         "Apple Inc. designs and sells consumer electronics.",
        "price_change_1mo":    3.25,
        "volume":              55_000_000,
        "fetched_at":          "2024-01-15T10:00:00",
    }


@pytest.fixture
def sample_raw_stock_low_risk():
    """A low-risk, undervalued stock."""
    return {
        "ticker":              "JNJ",
        "name":                "Johnson & Johnson",
        "sector":              "Healthcare",
        "industry":            "Drug Manufacturers",
        "current_price":       155.00,
        "pe_ratio":            12.5,
        "forward_pe":          11.0,
        "market_cap":          373_000_000_000,
        "fifty_two_week_high": 170.00,
        "fifty_two_week_low":  143.00,
        "beta":                0.55,
        "dividend_yield":      0.03,
        "eps":                 12.4,
        "revenue_growth":      0.04,
        "profit_margins":      0.18,
        "description":         "Johnson & Johnson is a healthcare conglomerate.",
        "price_change_1mo":    -1.5,
        "volume":              8_000_000,
        "fetched_at":          "2024-01-15T10:00:00",
    }


@pytest.fixture
def sample_raw_stock_high_risk():
    """A high-risk, growth/premium stock."""
    return {
        "ticker":              "TSLA",
        "name":                "Tesla, Inc.",
        "sector":              "Consumer Cyclical",
        "industry":            "Auto Manufacturers",
        "current_price":       210.00,
        "pe_ratio":            65.0,
        "forward_pe":          50.0,
        "market_cap":          669_000_000_000,
        "fifty_two_week_high": 299.29,
        "fifty_two_week_low":  138.80,
        "beta":                2.31,
        "dividend_yield":      None,
        "eps":                 3.22,
        "revenue_growth":      0.19,
        "profit_margins":      0.055,
        "description":         "Tesla designs and manufactures electric vehicles.",
        "price_change_1mo":    -12.5,
        "volume":              120_000_000,
        "fetched_at":          "2024-01-15T10:00:00",
    }


@pytest.fixture
def three_raw_stocks(sample_raw_stock, sample_raw_stock_low_risk, sample_raw_stock_high_risk):
    """A list of three diverse raw stocks."""
    return [sample_raw_stock, sample_raw_stock_low_risk, sample_raw_stock_high_risk]


@pytest.fixture
def raw_stocks_file(tmp_path, three_raw_stocks):
    """Write three_raw_stocks to a temp JSON file and return its path."""
    path = tmp_path / "raw_stocks.json"
    path.write_text(json.dumps(three_raw_stocks), encoding="utf-8")
    return str(path)
