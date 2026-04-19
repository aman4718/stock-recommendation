"""
data_ingestion.py — Phase 1, Step 1
Fetches raw stock data from Yahoo Finance and persists it to JSON.
"""

import json
import os
from datetime import datetime

import yfinance as yf
from loguru import logger

from phase1.config import (
    DATA_DIR,
    HISTORY_PERIOD,
    RAW_DATA_FILE,
    STOCK_TICKERS,
)


# ─────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────

def _price_change_pct(history) -> float | None:
    """Return percentage price change over the history window."""
    if history.empty or len(history) < 2:
        return None
    start = history["Close"].iloc[0]
    end   = history["Close"].iloc[-1]
    if start == 0:
        return None
    return round(((end - start) / start) * 100, 2)


def _safe_get(info: dict, *keys):
    """Return the first non-None value from the info dict for given keys."""
    for key in keys:
        val = info.get(key)
        if val is not None:
            return val
    return None


# ─────────────────────────────────────────────────────────────────
# Core fetch
# ─────────────────────────────────────────────────────────────────

def fetch_single_stock(ticker: str) -> dict | None:
    """
    Fetch all relevant fields for one ticker.
    Returns None on failure.
    """
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        # Some tickers return minimal info dicts — skip those
        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            logger.warning(f"[{ticker}] Empty / invalid info dict — skipping.")
            return None

        history      = stock.history(period=HISTORY_PERIOD)
        price_change = _price_change_pct(history)

        data = {
            "ticker":               ticker,
            "name":                 info.get("longName") or ticker,
            "sector":               info.get("sector", "N/A"),
            "industry":             info.get("industry", "N/A"),
            "current_price":        _safe_get(info, "currentPrice", "regularMarketPrice"),
            "pe_ratio":             info.get("trailingPE"),
            "forward_pe":           info.get("forwardPE"),
            "market_cap":           info.get("marketCap"),
            "fifty_two_week_high":  info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low":   info.get("fiftyTwoWeekLow"),
            "beta":                 info.get("beta"),
            "dividend_yield":       info.get("dividendYield"),
            "eps":                  info.get("trailingEps"),
            "revenue_growth":       info.get("revenueGrowth"),
            "profit_margins":       info.get("profitMargins"),
            "description":          info.get("longBusinessSummary", ""),
            "price_change_1mo":     price_change,
            "volume":               _safe_get(info, "volume", "averageVolume"),
            "fetched_at":           datetime.now().isoformat(),
        }

        logger.info(
            f"✓ [{ticker}]  Price=${data['current_price']}  "
            f"Sector={data['sector']}  PE={data['pe_ratio']}  "
            f"1M-Change={price_change}%"
        )
        return data

    except Exception as exc:
        logger.error(f"✗ [{ticker}] Failed: {exc}")
        return None


def fetch_all_stocks(tickers: list[str] | None = None) -> list[dict]:
    """
    Fetch data for every ticker in the list.
    Falls back to the default STOCK_TICKERS list if none provided.
    """
    tickers = tickers or STOCK_TICKERS
    logger.info(f"Starting fetch for {len(tickers)} tickers …")

    results = []
    for ticker in tickers:
        record = fetch_single_stock(ticker)
        if record:
            results.append(record)

    logger.info(f"Fetched {len(results)}/{len(tickers)} stocks successfully.")

    return results


# ─────────────────────────────────────────────────────────────────
# Persistence
# ─────────────────────────────────────────────────────────────────

def save_raw_data(stocks: list[dict]) -> None:
    """Save raw stock records to data/raw_stocks.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(RAW_DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(stocks, fh, indent=2, default=str)
    logger.success(f"Raw data → {RAW_DATA_FILE}  ({len(stocks)} records)")


def load_raw_data() -> list[dict]:
    """Load previously saved raw stock data."""
    if not os.path.exists(RAW_DATA_FILE):
        raise FileNotFoundError(f"Raw data file not found: {RAW_DATA_FILE}")
    with open(RAW_DATA_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ─────────────────────────────────────────────────────────────────
# Public entry-point
# ─────────────────────────────────────────────────────────────────

def run_ingestion(tickers: list[str] | None = None) -> list[dict]:
    """
    Full ingestion pipeline:
      1. Fetch stock data from Yahoo Finance
      2. Persist to raw JSON
      3. Return the list of records
    """
    stocks = fetch_all_stocks(tickers)
    save_raw_data(stocks)
    return stocks
