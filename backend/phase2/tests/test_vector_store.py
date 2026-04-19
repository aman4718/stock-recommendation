"""
test_vector_store.py — Tests for phase2/vector_store.py

Strategy:
- ChromaDB CloudClient is MOCKED — no real network calls
- SentenceTransformer is MOCKED — no model downloads
- Tests cover: client singleton, collection management, upsert,
  metadata sanitisation, similarity search, load_documents_from_file,
  get_collection_stats
"""

import json
import os
import pytest
from unittest.mock import MagicMock, patch, call


# ─────────────────────────────────────────────────────────────────
# Mock builders
# ─────────────────────────────────────────────────────────────────

def _make_mock_collection(doc_count: int = 3):
    """Create a mock ChromaDB collection."""
    col = MagicMock()
    col.count.return_value = doc_count
    col.query.return_value = {
        "ids":       [["AAPL", "MSFT", "JNJ"][:doc_count]],
        "documents": [["doc AAPL", "doc MSFT", "doc JNJ"][:doc_count]],
        "metadatas": [[
            {"ticker": "AAPL", "sector": "Technology", "risk_level": "Moderate"},
            {"ticker": "MSFT", "sector": "Technology", "risk_level": "Low"},
            {"ticker": "JNJ",  "sector": "Healthcare",  "risk_level": "Low"},
        ][:doc_count]],
        "distances": [[0.12, 0.18, 0.25][:doc_count]],
    }
    return col


def _make_mock_client(collection=None):
    """Create a mock ChromaDB CloudClient."""
    if collection is None:
        collection = _make_mock_collection()
    client = MagicMock()
    client.get_or_create_collection.return_value = collection
    client.delete_collection.return_value = None
    return client


# ─────────────────────────────────────────────────────────────────
# get_client (singleton)
# ─────────────────────────────────────────────────────────────────

class TestGetClient:
    def test_returns_client_instance(self):
        import vector_store as vs
        mock_client = _make_mock_client()
        with patch("vector_store._client", None), \
             patch("vector_store.chromadb.CloudClient", return_value=mock_client):
            client = vs.get_client()
            assert client is mock_client

    def test_client_created_with_correct_credentials(self):
        import vector_store as vs
        mock_client = _make_mock_client()
        with patch("vector_store._client", None), \
             patch("vector_store.chromadb.CloudClient", return_value=mock_client) as mock_cls, \
             patch("vector_store.CHROMA_API_KEY",  "test-key"), \
             patch("vector_store.CHROMA_TENANT",   "test-tenant"), \
             patch("vector_store.CHROMA_DATABASE", "test-db"):
            vs.get_client()
            mock_cls.assert_called_once_with(
                tenant="test-tenant",
                database="test-db",
                api_key="test-key",
            )

    def test_client_not_recreated_on_second_call(self):
        import vector_store as vs
        existing_client = _make_mock_client()
        with patch("vector_store._client", existing_client):
            c1 = vs.get_client()
            c2 = vs.get_client()
            assert c1 is c2 is existing_client


# ─────────────────────────────────────────────────────────────────
# get_or_create_collection
# ─────────────────────────────────────────────────────────────────

class TestGetOrCreateCollection:
    @pytest.fixture(autouse=True)
    def patch_client(self):
        import vector_store as vs
        self.mock_col    = _make_mock_collection()
        self.mock_client = _make_mock_client(self.mock_col)
        with patch.object(vs, "_client", self.mock_client):
            yield

    def test_returns_collection(self):
        import vector_store as vs
        col = vs.get_or_create_collection(reset=False)
        assert col is self.mock_col

    def test_get_or_create_called_with_collection_name(self):
        import vector_store as vs
        vs.get_or_create_collection(reset=False)
        self.mock_client.get_or_create_collection.assert_called_once()
        call_args = self.mock_client.get_or_create_collection.call_args
        assert call_args[1]["name"] == "stock_vectors"

    def test_reset_true_deletes_collection_first(self):
        import vector_store as vs
        vs.get_or_create_collection(reset=True)
        self.mock_client.delete_collection.assert_called_once_with("stock_vectors")

    def test_reset_false_does_not_delete(self):
        import vector_store as vs
        vs.get_or_create_collection(reset=False)
        self.mock_client.delete_collection.assert_not_called()

    def test_metadata_includes_distance_function(self):
        import vector_store as vs
        vs.get_or_create_collection(reset=False)
        call_kwargs = self.mock_client.get_or_create_collection.call_args[1]
        assert "hnsw:space" in call_kwargs["metadata"]


# ─────────────────────────────────────────────────────────────────
# _sanitise_metadata
# ─────────────────────────────────────────────────────────────────

class TestSanitiseMetadata:
    def _sanitise(self, meta):
        import vector_store as vs
        return vs._sanitise_metadata(meta)

    def test_none_becomes_empty_string(self):
        result = self._sanitise({"price": None})
        assert result["price"] == ""

    def test_string_preserved(self):
        result = self._sanitise({"sector": "Technology"})
        assert result["sector"] == "Technology"

    def test_int_preserved(self):
        result = self._sanitise({"count": 42})
        assert result["count"] == 42

    def test_float_preserved(self):
        result = self._sanitise({"ratio": 3.14})
        assert result["ratio"] == 3.14

    def test_bool_preserved(self):
        result = self._sanitise({"active": True})
        assert result["active"] is True

    def test_list_converted_to_str(self):
        result = self._sanitise({"tags": ["a", "b"]})
        assert isinstance(result["tags"], str)

    def test_dict_converted_to_str(self):
        result = self._sanitise({"nested": {"a": 1}})
        assert isinstance(result["nested"], str)

    def test_all_none_values_become_empty_strings(self):
        meta = {"a": None, "b": None, "c": "ok"}
        result = self._sanitise(meta)
        assert result["a"] == ""
        assert result["b"] == ""
        assert result["c"] == "ok"

    def test_empty_dict_returns_empty_dict(self):
        assert self._sanitise({}) == {}


# ─────────────────────────────────────────────────────────────────
# upsert_documents
# ─────────────────────────────────────────────────────────────────

class TestUpsertDocuments:
    @pytest.fixture(autouse=True)
    def patch_deps(self):
        import vector_store as vs
        self.mock_col    = _make_mock_collection(doc_count=3)
        self.mock_client = _make_mock_client(self.mock_col)

        fake_embeddings = [[0.1] * 384] * 3

        with patch.object(vs, "_client", self.mock_client), \
             patch("vector_store.embed_texts", return_value=fake_embeddings) as mock_embed:
            self.mock_embed = mock_embed
            yield

    def test_returns_count_of_documents(self, three_documents):
        import vector_store as vs
        count = vs.upsert_documents(three_documents, reset=False)
        assert count == 3

    def test_upsert_called_on_collection(self, three_documents):
        import vector_store as vs
        vs.upsert_documents(three_documents, reset=False)
        self.mock_col.upsert.assert_called_once()

    def test_upsert_called_with_correct_ids(self, three_documents):
        import vector_store as vs
        vs.upsert_documents(three_documents, reset=False)
        call_kwargs = self.mock_col.upsert.call_args[1]
        assert set(call_kwargs["ids"]) == {"AAPL", "TSLA", "JNJ"}

    def test_upsert_called_with_documents(self, three_documents):
        import vector_store as vs
        vs.upsert_documents(three_documents, reset=False)
        call_kwargs = self.mock_col.upsert.call_args[1]
        assert "documents" in call_kwargs
        assert len(call_kwargs["documents"]) == 3

    def test_embed_texts_called_with_document_texts(self, three_documents):
        import vector_store as vs
        vs.upsert_documents(three_documents, reset=False)
        texts_passed = self.mock_embed.call_args[0][0]
        assert len(texts_passed) == 3

    def test_empty_documents_returns_zero(self):
        import vector_store as vs
        count = vs.upsert_documents([], reset=False)
        assert count == 0

    def test_empty_documents_does_not_call_upsert(self):
        import vector_store as vs
        vs.upsert_documents([], reset=False)
        self.mock_col.upsert.assert_not_called()

    def test_reset_true_deletes_collection(self, three_documents):
        import vector_store as vs
        vs.upsert_documents(three_documents, reset=True)
        self.mock_client.delete_collection.assert_called_once()

    def test_none_metadata_sanitised_before_upsert(
        self, sample_document_with_none_metadata
    ):
        import vector_store as vs
        vs.upsert_documents([sample_document_with_none_metadata], reset=False)
        call_kwargs = self.mock_col.upsert.call_args[1]
        metadata_list = call_kwargs["metadatas"]
        for meta in metadata_list:
            for v in meta.values():
                assert v is not None, "None metadata values must be sanitised"


# ─────────────────────────────────────────────────────────────────
# similarity_search
# ─────────────────────────────────────────────────────────────────

class TestSimilaritySearch:
    @pytest.fixture(autouse=True)
    def patch_deps(self):
        import vector_store as vs
        self.mock_col    = _make_mock_collection(doc_count=3)
        self.mock_client = _make_mock_client(self.mock_col)

        with patch.object(vs, "_client", self.mock_client), \
             patch("vector_store.embed_query", return_value=[0.1] * 384):
            yield

    def test_returns_list(self):
        import vector_store as vs
        results = vs.similarity_search("best stocks", top_k=3)
        assert isinstance(results, list)

    def test_result_count_matches_top_k(self):
        import vector_store as vs
        results = vs.similarity_search("low risk stocks", top_k=3)
        assert len(results) == 3

    def test_each_result_has_required_keys(self):
        import vector_store as vs
        results = vs.similarity_search("tech stocks", top_k=2)
        for r in results:
            assert "id"       in r
            assert "text"     in r
            assert "metadata" in r
            assert "distance" in r

    def test_distance_is_float(self):
        import vector_store as vs
        results = vs.similarity_search("growth stocks", top_k=2)
        for r in results:
            assert isinstance(r["distance"], float)

    def test_embed_query_called(self):
        import vector_store as vs
        with patch("vector_store.embed_query", return_value=[0.1]*384) as mock_eq:
            vs.similarity_search("query text")
            mock_eq.assert_called_once_with("query text")

    def test_query_passed_to_collection(self):
        import vector_store as vs
        vs.similarity_search("dividend stocks", top_k=2)
        self.mock_col.query.assert_called_once()
        call_kwargs = self.mock_col.query.call_args[1]
        assert "query_embeddings" in call_kwargs

    def test_top_k_capped_at_collection_count(self):
        import vector_store as vs
        # Collection has 3 docs, we ask for 10 — should clamp to 3
        vs.similarity_search("stocks", top_k=10)
        call_kwargs = self.mock_col.query.call_args[1]
        assert call_kwargs["n_results"] <= 3

    def test_results_ordered_by_distance(self):
        import vector_store as vs
        results = vs.similarity_search("best technology stocks", top_k=3)
        distances = [r["distance"] for r in results]
        assert distances == sorted(distances)


# ─────────────────────────────────────────────────────────────────
# load_documents_from_file
# ─────────────────────────────────────────────────────────────────

class TestLoadDocumentsFromFile:
    def test_loads_list_from_json(self, documents_json_file):
        import vector_store as vs
        docs = vs.load_documents_from_file(documents_json_file)
        assert isinstance(docs, list)
        assert len(docs) == 3

    def test_preserves_ids(self, documents_json_file):
        import vector_store as vs
        docs = vs.load_documents_from_file(documents_json_file)
        ids = [d["id"] for d in docs]
        assert "AAPL" in ids
        assert "TSLA" in ids

    def test_raises_if_file_missing(self, tmp_path):
        import vector_store as vs
        with pytest.raises(FileNotFoundError):
            vs.load_documents_from_file(str(tmp_path / "nonexistent.json"))


# ─────────────────────────────────────────────────────────────────
# get_collection_stats
# ─────────────────────────────────────────────────────────────────

class TestGetCollectionStats:
    def test_returns_dict(self):
        import vector_store as vs
        mock_col    = _make_mock_collection(doc_count=10)
        mock_client = _make_mock_client(mock_col)
        with patch.object(vs, "_client", mock_client):
            stats = vs.get_collection_stats()
        assert isinstance(stats, dict)

    def test_has_required_keys(self):
        import vector_store as vs
        mock_col    = _make_mock_collection(doc_count=5)
        mock_client = _make_mock_client(mock_col)
        with patch.object(vs, "_client", mock_client):
            stats = vs.get_collection_stats()
        for key in ["collection_name", "document_count", "embedding_model"]:
            assert key in stats

    def test_document_count_matches_collection(self):
        import vector_store as vs
        mock_col    = _make_mock_collection(doc_count=27)
        mock_client = _make_mock_client(mock_col)
        with patch.object(vs, "_client", mock_client):
            stats = vs.get_collection_stats()
        assert stats["document_count"] == 27


# ─────────────────────────────────────────────────────────────────
# Integration: upsert → search pipeline (all mocked)
# ─────────────────────────────────────────────────────────────────

class TestUpsertSearchPipeline:
    def test_documents_are_searchable_after_upsert(self, three_documents):
        """
        Upsert 3 docs, then run a search. Both should succeed and
        return the expected structure.
        """
        import vector_store as vs

        mock_col    = _make_mock_collection(doc_count=3)
        mock_client = _make_mock_client(mock_col)
        fake_embed  = [[0.1] * 384] * 3

        with patch.object(vs, "_client", mock_client), \
             patch("vector_store.embed_texts",  return_value=fake_embed), \
             patch("vector_store.embed_query",  return_value=[0.1] * 384):

            count   = vs.upsert_documents(three_documents, reset=False)
            results = vs.similarity_search("best long-term stocks", top_k=3)

        assert count == 3
        assert len(results) == 3
        for r in results:
            assert "id" in r and "text" in r and "distance" in r
