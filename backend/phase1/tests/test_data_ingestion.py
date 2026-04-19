"""
test_data_ingestion.py — Tests for phase1/data_ingestion.py

Strategy:
  - All Yahoo Finance (yfinance) calls are mocked → no network needed
  - File I/O uses pytest's tmp_path fixture → no pollution of real data/
  - Tests cover: price-change helper, safe_get, fetch_single_stock,
    fetch_all_stocks, save/load, and the run_ingestion pipeline
"""

import json
import os
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

import data_ingestion as di


# ─────────────────────────────────────────────────────────────────
# _price_change_pct
# ─────────────────────────────────────────────────────────────────

class TestPriceChangePct:
    def _make_history(self, start: float, end: float) -> pd.DataFrame:
        return pd.DataFrame({"Close": [start, (start + end) / 2, end]})

    def test_returns_none_for_empty_dataframe(self):
        assert di._price_change_pct(pd.DataFrame()) is None

    def test_returns_none_for_single_row(self):
        hist = pd.DataFrame({"Close": [100.0]})
        assert di._price_change_pct(hist) is None

    def test_positive_price_change(self):
        hist = self._make_history(100.0, 110.0)
        result = di._price_change_pct(hist)
        assert result == pytest.approx(10.0, rel=1e-3)

    def test_negative_price_change(self):
        hist = self._make_history(200.0, 180.0)
        result = di._price_change_pct(hist)
        assert result == pytest.approx(-10.0, rel=1e-3)

    def test_zero_start_price_returns_none(self):
        hist = self._make_history(0.0, 50.0)
        assert di._price_change_pct(hist) is None

    def test_result_is_rounded_to_two_decimals(self):
        hist = self._make_history(3.0, 4.0)
        result = di._price_change_pct(hist)
        # 33.333...% should round to 33.33
        assert result == pytest.approx(33.33, rel=1e-2)

    def test_no_change_returns_zero(self):
        hist = self._make_history(150.0, 150.0)
        assert di._price_change_pct(hist) == 0.0


# ─────────────────────────────────────────────────────────────────
# _safe_get
# ─────────────────────────────────────────────────────────────────

class TestSafeGet:
    def test_returns_first_non_none_key(self):
        info = {"a": None, "b": 42, "c": 99}
        assert di._safe_get(info, "a", "b", "c") == 42

    def test_returns_none_when_all_missing(self):
        info = {}
        assert di._safe_get(info, "x", "y") is None

    def test_returns_none_when_all_values_none(self):
        info = {"a": None, "b": None}
        assert di._safe_get(info, "a", "b") is None

    def test_returns_first_key_if_present(self):
        info = {"currentPrice": 175.0, "regularMarketPrice": 170.0}
        assert di._safe_get(info, "currentPrice", "regularMarketPrice") == 175.0

    def test_falls_back_to_second_key(self):
        info = {"currentPrice": None, "regularMarketPrice": 170.0}
        assert di._safe_get(info, "currentPrice", "regularMarketPrice") == 170.0


# ─────────────────────────────────────────────────────────────────
# fetch_single_stock — with mocked yfinance
# ─────────────────────────────────────────────────────────────────

def _make_mock_ticker(info_override=None, history_data=None):
    """Build a mock yf.Ticker that returns controlled data."""
    default_info = {
        "longName":             "Apple Inc.",
        "sector":               "Technology",
        "industry":             "Consumer Electronics",
        "currentPrice":         175.50,
        "regularMarketPrice":   175.50,
        "trailingPE":           28.4,
        "forwardPE":            25.1,
        "marketCap":            2_750_000_000_000,
        "fiftyTwoWeekHigh":     199.62,
        "fiftyTwoWeekLow":      164.08,
        "beta":                 1.1,
        "dividendYield":        0.0052,
        "trailingEps":          6.43,
        "revenueGrowth":        0.089,
        "profitMargins":        0.261,
        "longBusinessSummary":  "Apple designs consumer electronics.",
        "volume":               55_000_000,
    }
    if info_override:
        default_info.update(info_override)

    if history_data is None:
        history_data = pd.DataFrame({"Close": [170.0, 172.0, 175.5]})

    mock_ticker = MagicMock()
    mock_ticker.info = default_info
    mock_ticker.history.return_value = history_data
    return mock_ticker


class TestFetchSingleStock:
    @patch("data_ingestion.yf.Ticker")
    def test_returns_dict_on_success(self, mock_yf):
        mock_yf.return_value = _make_mock_ticker()
        result = di.fetch_single_stock("AAPL")
        assert isinstance(result, dict)

    @patch("data_ingestion.yf.Ticker")
    def test_has_required_keys(self, mock_yf):
        mock_yf.return_value = _make_mock_ticker()
        result = di.fetch_single_stock("AAPL")
        required_keys = [
            "ticker", "name", "sector", "industry",
            "current_price", "pe_ratio", "market_cap",
            "beta", "price_change_1mo", "fetched_at",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    @patch("data_ingestion.yf.Ticker")
    def test_ticker_symbol_is_preserved(self, mock_yf):
        mock_yf.return_value = _make_mock_ticker()
        result = di.fetch_single_stock("AAPL")
        assert result["ticker"] == "AAPL"

    @patch("data_ingestion.yf.Ticker")
    def test_price_set_correctly(self, mock_yf):
        mock_yf.return_value = _make_mock_ticker()
        result = di.fetch_single_stock("AAPL")
        assert result["current_price"] == 175.50

    @patch("data_ingestion.yf.Ticker")
    def test_price_change_calculated(self, mock_yf):
        history = pd.DataFrame({"Close": [100.0, 105.0, 110.0]})
        mock_yf.return_value = _make_mock_ticker(history_data=history)
        result = di.fetch_single_stock("AAPL")
        assert result["price_change_1mo"] == pytest.approx(10.0, rel=1e-2)

    @patch("data_ingestion.yf.Ticker")
    def test_returns_none_when_info_empty(self, mock_yf):
        mock = MagicMock()
        mock.info = {}
        mock_yf.return_value = mock
        result = di.fetch_single_stock("FAKE")
        assert result is None

    @patch("data_ingestion.yf.Ticker")
    def test_returns_none_on_exception(self, mock_yf):
        mock_yf.side_effect = Exception("Network error")
        result = di.fetch_single_stock("ERR")
        assert result is None

    @patch("data_ingestion.yf.Ticker")
    def test_falls_back_to_regular_market_price(self, mock_yf):
        mock_yf.return_value = _make_mock_ticker(
            info_override={"currentPrice": None, "regularMarketPrice": 180.0}
        )
        result = di.fetch_single_stock("AAPL")
        assert result["current_price"] == 180.0

    @patch("data_ingestion.yf.Ticker")
    def test_description_captured(self, mock_yf):
        mock_yf.return_value = _make_mock_ticker()
        result = di.fetch_single_stock("AAPL")
        assert "Apple" in result["description"]

    @patch("data_ingestion.yf.Ticker")
    def test_fetched_at_is_iso_string(self, mock_yf):
        mock_yf.return_value = _make_mock_ticker()
        result = di.fetch_single_stock("AAPL")
        from datetime import datetime
        # Should not raise
        datetime.fromisoformat(result["fetched_at"])


# ─────────────────────────────────────────────────────────────────
# fetch_all_stocks
# ─────────────────────────────────────────────────────────────────

class TestFetchAllStocks:
    @patch("data_ingestion.fetch_single_stock")
    def test_returns_list(self, mock_fetch):
        mock_fetch.return_value = {"ticker": "AAPL", "current_price": 175.0}
        result = di.fetch_all_stocks(["AAPL"])
        assert isinstance(result, list)

    @patch("data_ingestion.fetch_single_stock")
    def test_filters_out_none_results(self, mock_fetch):
        # AAPL succeeds, FAKE fails
        mock_fetch.side_effect = lambda t: {"ticker": t} if t == "AAPL" else None
        result = di.fetch_all_stocks(["AAPL", "FAKE"])
        assert len(result) == 1
        assert result[0]["ticker"] == "AAPL"

    @patch("data_ingestion.fetch_single_stock")
    def test_uses_default_tickers_when_none_passed(self, mock_fetch):
        mock_fetch.return_value = {"ticker": "X", "current_price": 1.0}
        from config import STOCK_TICKERS
        di.fetch_all_stocks(None)
        assert mock_fetch.call_count == len(STOCK_TICKERS)

    @patch("data_ingestion.fetch_single_stock")
    def test_all_failures_returns_empty_list(self, mock_fetch):
        mock_fetch.return_value = None
        result = di.fetch_all_stocks(["A", "B", "C"])
        assert result == []


# ─────────────────────────────────────────────────────────────────
# save_raw_data / load_raw_data
# ─────────────────────────────────────────────────────────────────

class TestSaveLoadRawData:
    def test_save_creates_file(self, tmp_path, three_raw_stocks, monkeypatch):
        target = str(tmp_path / "raw_stocks.json")
        monkeypatch.setattr(di, "RAW_DATA_FILE", target)
        monkeypatch.setattr(di, "DATA_DIR", str(tmp_path))
        di.save_raw_data(three_raw_stocks)
        assert os.path.isfile(target)

    def test_save_writes_correct_count(self, tmp_path, three_raw_stocks, monkeypatch):
        target = str(tmp_path / "raw_stocks.json")
        monkeypatch.setattr(di, "RAW_DATA_FILE", target)
        monkeypatch.setattr(di, "DATA_DIR", str(tmp_path))
        di.save_raw_data(three_raw_stocks)
        with open(target, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 3

    def test_save_preserves_ticker(self, tmp_path, sample_raw_stock, monkeypatch):
        target = str(tmp_path / "raw_stocks.json")
        monkeypatch.setattr(di, "RAW_DATA_FILE", target)
        monkeypatch.setattr(di, "DATA_DIR", str(tmp_path))
        di.save_raw_data([sample_raw_stock])
        with open(target, encoding="utf-8") as f:
            data = json.load(f)
        assert data[0]["ticker"] == "AAPL"

    def test_load_returns_list(self, tmp_path, three_raw_stocks, monkeypatch):
        target = str(tmp_path / "raw_stocks.json")
        tmp_path.joinpath("raw_stocks.json").write_text(
            json.dumps(three_raw_stocks), encoding="utf-8"
        )
        monkeypatch.setattr(di, "RAW_DATA_FILE", target)
        result = di.load_raw_data()
        assert isinstance(result, list)
        assert len(result) == 3

    def test_load_raises_if_file_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(di, "RAW_DATA_FILE", str(tmp_path / "nonexistent.json"))
        with pytest.raises(FileNotFoundError):
            di.load_raw_data()


# ─────────────────────────────────────────────────────────────────
# run_ingestion — integration (mocked network + temp files)
# ─────────────────────────────────────────────────────────────────

class TestRunIngestion:
    @patch("data_ingestion.fetch_single_stock")
    def test_run_ingestion_returns_list(self, mock_fetch, tmp_path, monkeypatch):
        monkeypatch.setattr(di, "RAW_DATA_FILE", str(tmp_path / "raw_stocks.json"))
        monkeypatch.setattr(di, "DATA_DIR", str(tmp_path))
        mock_fetch.return_value = {"ticker": "AAPL", "current_price": 175.0}
        result = di.run_ingestion(["AAPL"])
        assert isinstance(result, list)
        assert len(result) == 1

    @patch("data_ingestion.fetch_single_stock")
    def test_run_ingestion_saves_file(self, mock_fetch, tmp_path, monkeypatch):
        target = str(tmp_path / "raw_stocks.json")
        monkeypatch.setattr(di, "RAW_DATA_FILE", target)
        monkeypatch.setattr(di, "DATA_DIR", str(tmp_path))
        mock_fetch.return_value = {"ticker": "MSFT", "current_price": 300.0}
        di.run_ingestion(["MSFT"])
        assert os.path.isfile(target)
