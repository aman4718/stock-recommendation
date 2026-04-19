"""
test_data_processor.py — Tests for phase1/data_processor.py

Covers:
  - classify_risk          (boundary values, None handling)
  - classify_valuation     (boundary values, None handling)
  - format_market_cap      (T / B / M / raw / None)
  - format_pct             (fraction → %, None)
  - format_price_change    (positive / negative / zero / None)
  - build_document_text    (template rendering, field presence)
  - process_stocks         (enrichment, file output)
  - convert_to_documents   (structure, metadata, file output)
  - load_processed_data    (happy path, FileNotFoundError)
  - load_documents         (happy path, FileNotFoundError)
"""

import json
import os
import pytest
from unittest.mock import patch

import data_processor as dp
from config import (
    BETA_HIGH_THRESHOLD,
    BETA_LOW_THRESHOLD,
    PE_FAIR_MAX,
    PE_UNDERVALUED_MAX,
)


# ─────────────────────────────────────────────────────────────────
# classify_risk
# ─────────────────────────────────────────────────────────────────

class TestClassifyRisk:
    def test_none_returns_unknown(self):
        assert dp.classify_risk(None) == "Unknown"

    def test_zero_beta_is_low(self):
        assert dp.classify_risk(0.0) == "Low"

    def test_below_low_threshold_is_low(self):
        assert dp.classify_risk(BETA_LOW_THRESHOLD - 0.01) == "Low"

    def test_at_low_threshold_is_moderate(self):
        # beta == 0.8 → not < 0.8 → Moderate
        assert dp.classify_risk(BETA_LOW_THRESHOLD) == "Moderate"

    def test_between_thresholds_is_moderate(self):
        mid = (BETA_LOW_THRESHOLD + BETA_HIGH_THRESHOLD) / 2
        assert dp.classify_risk(mid) == "Moderate"

    def test_at_high_threshold_is_high(self):
        assert dp.classify_risk(BETA_HIGH_THRESHOLD) == "High"

    def test_above_high_threshold_is_high(self):
        assert dp.classify_risk(BETA_HIGH_THRESHOLD + 1.0) == "High"

    def test_very_high_beta_is_high(self):
        assert dp.classify_risk(5.0) == "High"

    def test_aapl_beta_is_moderate(self):
        # AAPL beta ~1.1 → Moderate
        assert dp.classify_risk(1.1) == "Moderate"


# ─────────────────────────────────────────────────────────────────
# classify_valuation
# ─────────────────────────────────────────────────────────────────

class TestClassifyValuation:
    def test_none_returns_unknown(self):
        assert dp.classify_valuation(None) == "Unknown"

    def test_below_undervalued_threshold(self):
        assert dp.classify_valuation(PE_UNDERVALUED_MAX - 1) == "Undervalued"

    def test_at_undervalued_threshold_is_fairly_valued(self):
        assert dp.classify_valuation(PE_UNDERVALUED_MAX) == "Fairly Valued"

    def test_between_thresholds_is_fairly_valued(self):
        mid = (PE_UNDERVALUED_MAX + PE_FAIR_MAX) / 2
        assert dp.classify_valuation(mid) == "Fairly Valued"

    def test_at_fair_max_is_growth(self):
        assert dp.classify_valuation(PE_FAIR_MAX) == "Growth / Premium"

    def test_above_fair_max_is_growth(self):
        assert dp.classify_valuation(PE_FAIR_MAX + 10) == "Growth / Premium"

    def test_negative_pe_is_undervalued(self):
        # Negative PE (loss-making) is < undervalued threshold
        assert dp.classify_valuation(-5) == "Undervalued"


# ─────────────────────────────────────────────────────────────────
# format_market_cap
# ─────────────────────────────────────────────────────────────────

class TestFormatMarketCap:
    def test_none_returns_na(self):
        assert dp.format_market_cap(None) == "N/A"

    def test_trillion(self):
        result = dp.format_market_cap(2_500_000_000_000)
        assert result == "$2.50T"

    def test_exact_trillion_boundary(self):
        result = dp.format_market_cap(1_000_000_000_000)
        assert "T" in result

    def test_billion(self):
        result = dp.format_market_cap(500_000_000_000)
        assert result == "$500.00B"

    def test_exact_billion(self):
        result = dp.format_market_cap(1_000_000_000)
        assert "B" in result

    def test_million(self):
        result = dp.format_market_cap(250_000_000)
        assert result == "$250.00M"

    def test_small_cap_raw(self):
        result = dp.format_market_cap(500_000)
        assert result == "$500,000"

    def test_starts_with_dollar(self):
        for val in [1_000_000, 1_000_000_000, 1_000_000_000_000]:
            assert dp.format_market_cap(val).startswith("$")


# ─────────────────────────────────────────────────────────────────
# format_pct
# ─────────────────────────────────────────────────────────────────

class TestFormatPct:
    def test_none_returns_na(self):
        assert dp.format_pct(None) == "N/A"

    def test_zero(self):
        assert dp.format_pct(0.0) == "0.00%"

    def test_half_percent(self):
        assert dp.format_pct(0.005) == "0.50%"

    def test_five_percent(self):
        assert dp.format_pct(0.05) == "5.00%"

    def test_hundred_percent(self):
        assert dp.format_pct(1.0) == "100.00%"

    def test_custom_decimals(self):
        result = dp.format_pct(0.12345, decimals=3)
        assert result == "12.345%"

    def test_ends_with_percent_sign(self):
        assert dp.format_pct(0.1).endswith("%")


# ─────────────────────────────────────────────────────────────────
# format_price_change
# ─────────────────────────────────────────────────────────────────

class TestFormatPriceChange:
    def test_none_returns_na(self):
        assert dp.format_price_change(None) == "N/A"

    def test_positive_has_plus_sign(self):
        result = dp.format_price_change(5.25)
        assert result.startswith("+")
        assert "5.25" in result

    def test_negative_has_minus_sign(self):
        result = dp.format_price_change(-3.10)
        assert result.startswith("-")
        assert "3.10" in result

    def test_zero_has_no_plus(self):
        result = dp.format_price_change(0.0)
        assert result.startswith("-") or result == "0.00%"

    def test_ends_with_percent(self):
        assert dp.format_price_change(1.5).endswith("%")


# ─────────────────────────────────────────────────────────────────
# build_document_text
# ─────────────────────────────────────────────────────────────────

class TestBuildDocumentText:
    @pytest.fixture
    def processed_aapl(self, sample_raw_stock):
        """A processed AAPL record with all derived fields."""
        return {
            **sample_raw_stock,
            "risk_level":           "Moderate",
            "valuation_category":   "Growth / Premium",
            "market_cap_formatted": "$2.75T",
            "dividend_yield_pct":   "0.52%",
            "revenue_growth_pct":   "8.90%",
            "profit_margin_pct":    "26.10%",
            "price_change_fmt":     "+3.25%",
        }

    def test_returns_string(self, processed_aapl):
        result = dp.build_document_text(processed_aapl)
        assert isinstance(result, str)

    def test_contains_ticker(self, processed_aapl):
        result = dp.build_document_text(processed_aapl)
        assert "AAPL" in result

    def test_contains_company_name(self, processed_aapl):
        result = dp.build_document_text(processed_aapl)
        assert "Apple" in result

    def test_contains_sector(self, processed_aapl):
        result = dp.build_document_text(processed_aapl)
        assert "Technology" in result

    def test_contains_price(self, processed_aapl):
        result = dp.build_document_text(processed_aapl)
        assert "175.5" in result or "175.50" in result

    def test_contains_risk_level(self, processed_aapl):
        result = dp.build_document_text(processed_aapl)
        assert "Moderate" in result

    def test_contains_valuation(self, processed_aapl):
        result = dp.build_document_text(processed_aapl)
        assert "Growth" in result or "Premium" in result

    def test_description_truncated(self, sample_raw_stock):
        long_desc = "A" * 1000
        stock = {
            **sample_raw_stock,
            "description": long_desc,
            "risk_level": "Low",
            "valuation_category": "Fairly Valued",
            "market_cap_formatted": "$1B",
            "dividend_yield_pct": "1.00%",
            "revenue_growth_pct": "5.00%",
            "profit_margin_pct": "10.00%",
            "price_change_fmt": "+1.00%",
        }
        from config import DESCRIPTION_MAX_CHARS
        result = dp.build_document_text(stock)
        # The Business Summary should not exceed DESCRIPTION_MAX_CHARS chars
        summary_line = [l for l in result.splitlines() if l.startswith("Business Summary")]
        assert len(summary_line) == 1
        summary_value = summary_line[0].replace("Business Summary:", "").strip()
        assert len(summary_value) <= DESCRIPTION_MAX_CHARS

    def test_missing_price_shows_na(self, sample_raw_stock):
        stock = {
            **sample_raw_stock,
            "current_price": None,
            "risk_level": "Low",
            "valuation_category": "Undervalued",
            "market_cap_formatted": "$1B",
            "dividend_yield_pct": "0.00%",
            "revenue_growth_pct": "N/A",
            "profit_margin_pct": "N/A",
            "price_change_fmt": "N/A",
        }
        result = dp.build_document_text(stock)
        assert "N/A" in result


# ─────────────────────────────────────────────────────────────────
# process_stocks
# ─────────────────────────────────────────────────────────────────

class TestProcessStocks:
    def test_returns_list_same_length(self, three_raw_stocks, tmp_path, monkeypatch):
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "proc.json"))
        monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))
        result = dp.process_stocks(three_raw_stocks)
        assert len(result) == len(three_raw_stocks)

    def test_adds_risk_level(self, three_raw_stocks, tmp_path, monkeypatch):
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "proc.json"))
        monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))
        result = dp.process_stocks(three_raw_stocks)
        for stock in result:
            assert "risk_level" in stock

    def test_aapl_risk_is_moderate(self, sample_raw_stock, tmp_path, monkeypatch):
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "proc.json"))
        monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))
        result = dp.process_stocks([sample_raw_stock])
        assert result[0]["risk_level"] == "Moderate"   # beta=1.1

    def test_jnj_risk_is_low(self, sample_raw_stock_low_risk, tmp_path, monkeypatch):
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "proc.json"))
        monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))
        result = dp.process_stocks([sample_raw_stock_low_risk])
        assert result[0]["risk_level"] == "Low"        # beta=0.55

    def test_tsla_risk_is_high(self, sample_raw_stock_high_risk, tmp_path, monkeypatch):
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "proc.json"))
        monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))
        result = dp.process_stocks([sample_raw_stock_high_risk])
        assert result[0]["risk_level"] == "High"       # beta=2.31

    def test_adds_valuation_category(self, three_raw_stocks, tmp_path, monkeypatch):
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "proc.json"))
        monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))
        result = dp.process_stocks(three_raw_stocks)
        for stock in result:
            assert "valuation_category" in stock

    def test_adds_market_cap_formatted(self, three_raw_stocks, tmp_path, monkeypatch):
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "proc.json"))
        monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))
        result = dp.process_stocks(three_raw_stocks)
        for stock in result:
            assert "market_cap_formatted" in stock

    def test_saves_file(self, three_raw_stocks, tmp_path, monkeypatch):
        target = str(tmp_path / "proc.json")
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", target)
        monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))
        dp.process_stocks(three_raw_stocks)
        assert os.path.isfile(target)

    def test_original_fields_preserved(self, sample_raw_stock, tmp_path, monkeypatch):
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "proc.json"))
        monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))
        result = dp.process_stocks([sample_raw_stock])
        assert result[0]["ticker"] == "AAPL"
        assert result[0]["current_price"] == 175.50


# ─────────────────────────────────────────────────────────────────
# convert_to_documents
# ─────────────────────────────────────────────────────────────────

def _make_processed(raw_stocks, tmp_path, monkeypatch):
    """Helper: run process_stocks with temp paths and return result."""
    monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "proc.json"))
    monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))
    return dp.process_stocks(raw_stocks)


class TestConvertToDocuments:
    def test_returns_list_same_length(self, three_raw_stocks, tmp_path, monkeypatch):
        processed = _make_processed(three_raw_stocks, tmp_path, monkeypatch)
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", str(tmp_path / "docs.json"))
        result = dp.convert_to_documents(processed)
        assert len(result) == 3

    def test_each_doc_has_id(self, three_raw_stocks, tmp_path, monkeypatch):
        processed = _make_processed(three_raw_stocks, tmp_path, monkeypatch)
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", str(tmp_path / "docs.json"))
        docs = dp.convert_to_documents(processed)
        for doc in docs:
            assert "id" in doc

    def test_each_doc_has_text(self, three_raw_stocks, tmp_path, monkeypatch):
        processed = _make_processed(three_raw_stocks, tmp_path, monkeypatch)
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", str(tmp_path / "docs.json"))
        docs = dp.convert_to_documents(processed)
        for doc in docs:
            assert "text" in doc
            assert len(doc["text"]) > 50

    def test_each_doc_has_metadata(self, three_raw_stocks, tmp_path, monkeypatch):
        processed = _make_processed(three_raw_stocks, tmp_path, monkeypatch)
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", str(tmp_path / "docs.json"))
        docs = dp.convert_to_documents(processed)
        for doc in docs:
            assert "metadata" in doc
            assert isinstance(doc["metadata"], dict)

    def test_metadata_has_required_keys(self, sample_raw_stock, tmp_path, monkeypatch):
        processed = _make_processed([sample_raw_stock], tmp_path, monkeypatch)
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", str(tmp_path / "docs.json"))
        docs = dp.convert_to_documents(processed)
        meta = docs[0]["metadata"]
        for key in ["ticker", "name", "sector", "price", "pe_ratio", "risk_level", "valuation"]:
            assert key in meta, f"Missing metadata key: {key}"

    def test_id_matches_ticker(self, sample_raw_stock, tmp_path, monkeypatch):
        processed = _make_processed([sample_raw_stock], tmp_path, monkeypatch)
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", str(tmp_path / "docs.json"))
        docs = dp.convert_to_documents(processed)
        assert docs[0]["id"] == "AAPL"

    def test_saves_documents_file(self, three_raw_stocks, tmp_path, monkeypatch):
        processed = _make_processed(three_raw_stocks, tmp_path, monkeypatch)
        target = str(tmp_path / "docs.json")
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", target)
        dp.convert_to_documents(processed)
        assert os.path.isfile(target)

    def test_saved_file_is_valid_json(self, three_raw_stocks, tmp_path, monkeypatch):
        processed = _make_processed(three_raw_stocks, tmp_path, monkeypatch)
        target = str(tmp_path / "docs.json")
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", target)
        dp.convert_to_documents(processed)
        with open(target, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_text_contains_ticker_symbol(self, sample_raw_stock, tmp_path, monkeypatch):
        processed = _make_processed([sample_raw_stock], tmp_path, monkeypatch)
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", str(tmp_path / "docs.json"))
        docs = dp.convert_to_documents(processed)
        assert "AAPL" in docs[0]["text"]


# ─────────────────────────────────────────────────────────────────
# load_processed_data / load_documents
# ─────────────────────────────────────────────────────────────────

class TestLoadHelpers:
    def test_load_processed_data_returns_list(self, three_raw_stocks, tmp_path, monkeypatch):
        target = str(tmp_path / "proc.json")
        tmp_path.joinpath("proc.json").write_text(
            json.dumps(three_raw_stocks), encoding="utf-8"
        )
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", target)
        result = dp.load_processed_data()
        assert isinstance(result, list)
        assert len(result) == 3

    def test_load_processed_data_raises_if_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "missing.json"))
        with pytest.raises(FileNotFoundError):
            dp.load_processed_data()

    def test_load_documents_returns_list(self, tmp_path, monkeypatch):
        docs = [{"id": "AAPL", "text": "Stock: Apple", "metadata": {}}]
        tmp_path.joinpath("docs.json").write_text(
            json.dumps(docs), encoding="utf-8"
        )
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", str(tmp_path / "docs.json"))
        result = dp.load_documents()
        assert isinstance(result, list)
        assert result[0]["id"] == "AAPL"

    def test_load_documents_raises_if_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", str(tmp_path / "missing.json"))
        with pytest.raises(FileNotFoundError):
            dp.load_documents()


# ─────────────────────────────────────────────────────────────────
# End-to-End: process_stocks → convert_to_documents pipeline
# ─────────────────────────────────────────────────────────────────

class TestProcessorPipeline:
    def test_full_pipeline_produces_valid_documents(self, three_raw_stocks, tmp_path, monkeypatch):
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "proc.json"))
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", str(tmp_path / "docs.json"))
        monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))

        processed = dp.process_stocks(three_raw_stocks)
        docs = dp.convert_to_documents(processed)

        assert len(docs) == 3
        for doc in docs:
            assert doc["id"]
            assert len(doc["text"]) > 100
            assert doc["metadata"]["ticker"] in ["AAPL", "JNJ", "TSLA"]

    def test_pipeline_risk_diversity(self, three_raw_stocks, tmp_path, monkeypatch):
        """The three fixture stocks should span all three risk levels."""
        monkeypatch.setattr(dp, "PROCESSED_DATA_FILE", str(tmp_path / "proc.json"))
        monkeypatch.setattr(dp, "DOCUMENTS_FILE", str(tmp_path / "docs.json"))
        monkeypatch.setattr(dp, "DATA_DIR", str(tmp_path))

        processed = dp.process_stocks(three_raw_stocks)
        risk_levels = {s["risk_level"] for s in processed}
        assert "Low"      in risk_levels
        assert "Moderate" in risk_levels
        assert "High"     in risk_levels
