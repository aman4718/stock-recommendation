"""
test_config.py — Tests for phase1/config.py

Verifies that:
  - STOCK_TICKERS is a non-empty list of valid strings
  - All file paths are properly resolved absolute strings
  - Numeric thresholds are logically consistent
"""

import os
import pytest
import config


# ─────────────────────────────────────────────────────────────────
# STOCK_TICKERS
# ─────────────────────────────────────────────────────────────────

class TestStockTickers:
    def test_tickers_is_list(self):
        assert isinstance(config.STOCK_TICKERS, list)

    def test_tickers_not_empty(self):
        assert len(config.STOCK_TICKERS) > 0, "STOCK_TICKERS must not be empty"

    def test_all_tickers_are_strings(self):
        for ticker in config.STOCK_TICKERS:
            assert isinstance(ticker, str), f"Ticker {ticker!r} is not a string"

    def test_all_tickers_are_uppercase(self):
        for ticker in config.STOCK_TICKERS:
            assert ticker == ticker.upper(), f"Ticker {ticker!r} is not uppercase"

    def test_no_duplicate_tickers(self):
        assert len(config.STOCK_TICKERS) == len(set(config.STOCK_TICKERS)), \
            "Duplicate tickers found in STOCK_TICKERS"

    def test_tickers_no_whitespace(self):
        for ticker in config.STOCK_TICKERS:
            assert ticker.strip() == ticker, f"Ticker {ticker!r} has surrounding whitespace"

    def test_minimum_ticker_count(self):
        # Ensure at least 10 stocks for meaningful RAG results
        assert len(config.STOCK_TICKERS) >= 10, \
            f"Need at least 10 tickers, got {len(config.STOCK_TICKERS)}"


# ─────────────────────────────────────────────────────────────────
# File paths
# ─────────────────────────────────────────────────────────────────

class TestFilePaths:
    def test_base_dir_is_string(self):
        assert isinstance(config.BASE_DIR, str)

    def test_data_dir_is_string(self):
        assert isinstance(config.DATA_DIR, str)

    def test_data_dir_is_absolute(self):
        assert os.path.isabs(config.DATA_DIR), "DATA_DIR must be an absolute path"

    def test_raw_data_file_is_json(self):
        assert config.RAW_DATA_FILE.endswith(".json")

    def test_processed_data_file_is_json(self):
        assert config.PROCESSED_DATA_FILE.endswith(".json")

    def test_documents_file_is_json(self):
        assert config.DOCUMENTS_FILE.endswith(".json")

    def test_all_paths_within_data_dir(self):
        for path in [config.RAW_DATA_FILE, config.PROCESSED_DATA_FILE, config.DOCUMENTS_FILE]:
            assert path.startswith(config.DATA_DIR), \
                f"{path} does not live inside DATA_DIR"

    def test_all_output_files_are_distinct(self):
        paths = [config.RAW_DATA_FILE, config.PROCESSED_DATA_FILE, config.DOCUMENTS_FILE]
        assert len(paths) == len(set(paths)), "Output file paths must be unique"


# ─────────────────────────────────────────────────────────────────
# Numeric thresholds
# ─────────────────────────────────────────────────────────────────

class TestThresholds:
    def test_beta_low_less_than_high(self):
        assert config.BETA_LOW_THRESHOLD < config.BETA_HIGH_THRESHOLD, \
            "BETA_LOW_THRESHOLD must be < BETA_HIGH_THRESHOLD"

    def test_beta_thresholds_positive(self):
        assert config.BETA_LOW_THRESHOLD  > 0
        assert config.BETA_HIGH_THRESHOLD > 0

    def test_pe_undervalued_less_than_fair(self):
        assert config.PE_UNDERVALUED_MAX < config.PE_FAIR_MAX, \
            "PE_UNDERVALUED_MAX must be < PE_FAIR_MAX"

    def test_pe_thresholds_positive(self):
        assert config.PE_UNDERVALUED_MAX > 0
        assert config.PE_FAIR_MAX        > 0

    def test_description_max_chars_positive(self):
        assert config.DESCRIPTION_MAX_CHARS > 0

    def test_history_period_is_string(self):
        assert isinstance(config.HISTORY_PERIOD, str)
        assert len(config.HISTORY_PERIOD) > 0
