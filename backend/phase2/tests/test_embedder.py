"""
test_embedder.py — Tests for phase2/embedder.py

Strategy:
- All SentenceTransformer calls are MOCKED — no model download needed
- Tests cover: singleton loading, embed_texts (batching, empty, output shape),
  embed_query, and get_embedding_dimension
"""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch, PropertyMock


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

DIM = 384   # expected output dimension for all-MiniLM-L6-v2


def _make_mock_model(dim: int = DIM):
    """Build a mock SentenceTransformer that returns random unit vectors."""
    mock = MagicMock()
    mock.get_sentence_embedding_dimension.return_value = dim

    def fake_encode(texts, **kwargs):
        n = len(texts)
        vecs = np.random.randn(n, dim).astype(np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        return vecs / norms   # unit-normalised

    mock.encode.side_effect = fake_encode
    return mock


# ─────────────────────────────────────────────────────────────────
# get_model (singleton)
# ─────────────────────────────────────────────────────────────────

class TestGetModel:
    def test_model_loaded_on_first_call(self):
        import embedder
        with patch("embedder._model", None), \
             patch("embedder.SentenceTransformer", return_value=_make_mock_model()) as mock_cls:
            model = embedder.get_model()
            assert model is not None
            mock_cls.assert_called_once_with("all-MiniLM-L6-v2")

    def test_model_not_reloaded_on_second_call(self):
        import embedder
        mock_model = _make_mock_model()
        with patch("embedder._model", mock_model):
            m1 = embedder.get_model()
            m2 = embedder.get_model()
            assert m1 is m2  # same object

    def test_returns_sentence_transformer_instance(self):
        import embedder
        mock_model = _make_mock_model()
        with patch("embedder._model", mock_model):
            result = embedder.get_model()
            assert result is mock_model


# ─────────────────────────────────────────────────────────────────
# embed_texts
# ─────────────────────────────────────────────────────────────────

class TestEmbedTexts:
    @pytest.fixture(autouse=True)
    def patch_model(self):
        """Patch the global _model for every test in this class."""
        import embedder
        mock_model = _make_mock_model()
        with patch.object(embedder, "_model", mock_model):
            self.mock_model = mock_model
            yield

    def test_empty_input_returns_empty_list(self):
        import embedder
        result = embedder.embed_texts([])
        assert result == []

    def test_returns_list(self):
        import embedder
        result = embedder.embed_texts(["hello world"])
        assert isinstance(result, list)

    def test_output_count_matches_input(self):
        import embedder
        texts = ["stock A", "stock B", "stock C"]
        result = embedder.embed_texts(texts)
        assert len(result) == 3

    def test_each_embedding_is_list_of_floats(self):
        import embedder
        result = embedder.embed_texts(["test text"])
        assert isinstance(result[0], list)
        assert all(isinstance(v, float) for v in result[0])

    def test_embedding_dimension_is_correct(self):
        import embedder
        result = embedder.embed_texts(["hello"])
        assert len(result[0]) == DIM

    def test_different_texts_produce_different_embeddings(self):
        import embedder
        # Random vectors from our mock — very unlikely to be equal
        results = embedder.embed_texts(["apple stocks", "healthcare dividends"])
        assert results[0] != results[1]

    def test_encode_called_with_correct_args(self):
        import embedder
        texts = ["text1", "text2"]
        embedder.embed_texts(texts, batch_size=8)
        call_kwargs = self.mock_model.encode.call_args[1]
        assert call_kwargs["batch_size"] == 8
        assert call_kwargs["normalize_embeddings"] is True

    def test_single_text_works(self):
        import embedder
        result = embedder.embed_texts(["one text"])
        assert len(result) == 1
        assert len(result[0]) == DIM

    def test_large_batch_returns_all_embeddings(self):
        import embedder
        texts = [f"stock text {i}" for i in range(50)]
        result = embedder.embed_texts(texts)
        assert len(result) == 50


# ─────────────────────────────────────────────────────────────────
# embed_query
# ─────────────────────────────────────────────────────────────────

class TestEmbedQuery:
    @pytest.fixture(autouse=True)
    def patch_model(self):
        import embedder
        with patch.object(embedder, "_model", _make_mock_model()):
            yield

    def test_returns_list(self):
        import embedder
        result = embedder.embed_query("Best IT stocks")
        assert isinstance(result, list)

    def test_returns_single_vector(self):
        import embedder
        result = embedder.embed_query("low risk stocks")
        assert len(result) == DIM

    def test_each_element_is_float(self):
        import embedder
        result = embedder.embed_query("growth stocks")
        assert all(isinstance(v, float) for v in result)

    def test_empty_string_works(self):
        import embedder
        result = embedder.embed_query("")
        assert isinstance(result, list)
        assert len(result) == DIM

    def test_query_is_unit_normalised(self):
        """Since normalize_embeddings=True, vector norm should be ~1.0."""
        import embedder
        result = embedder.embed_query("dividend stocks")
        norm = sum(v**2 for v in result) ** 0.5
        assert abs(norm - 1.0) < 0.01


# ─────────────────────────────────────────────────────────────────
# get_embedding_dimension
# ─────────────────────────────────────────────────────────────────

class TestGetEmbeddingDimension:
    def test_returns_correct_dimension(self):
        import embedder
        with patch.object(embedder, "_model", _make_mock_model(dim=DIM)):
            assert embedder.get_embedding_dimension() == DIM

    def test_returns_int(self):
        import embedder
        with patch.object(embedder, "_model", _make_mock_model()):
            result = embedder.get_embedding_dimension()
            assert isinstance(result, int)
