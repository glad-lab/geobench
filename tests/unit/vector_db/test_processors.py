"""Unit tests for vector_db.processors module."""

import pytest
from unittest.mock import Mock, MagicMock

from src.vector_db.processors import (
    DataProcessor,
    BatchProcessor,
    EmbeddingProcessor,
    MetadataProcessor,
    ContentProcessor
)
from src.vector_db.exceptions import ProcessingError


class TestBatchProcessor:
    """Test BatchProcessor class."""

    def test_batch_processing(self):
        """Test batching data."""
        processor = BatchProcessor(batch_size=2)
        data = [{"id": f"item-{i}"} for i in range(5)]

        batches = list(processor.process(data))

        assert len(batches) == 3
        assert len(batches[0]) == 2
        assert len(batches[1]) == 2
        assert len(batches[2]) == 1

    def test_invalid_batch_size(self):
        """Test error for invalid batch size."""
        with pytest.raises(ValueError):
            BatchProcessor(batch_size=0)

        with pytest.raises(ValueError):
            BatchProcessor(batch_size=-1)

    def test_empty_data(self):
        """Test batching empty data."""
        processor = BatchProcessor(batch_size=10)
        batches = list(processor.process([]))

        assert len(batches) == 0


class TestEmbeddingProcessor:
    """Test EmbeddingProcessor class."""

    def test_add_embeddings(self):
        """Test adding embeddings to documents."""
        # Mock embedding provider
        mock_provider = Mock()
        mock_provider.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]

        processor = EmbeddingProcessor(mock_provider, text_field="description")
        data = [
            {"id": "1", "description": "Text 1"},
            {"id": "2", "description": "Text 2"}
        ]

        result = processor.process(data)

        assert len(result) == 2
        assert "embedding" in result[0]
        assert result[0]["embedding"] == [0.1, 0.2]
        assert result[1]["embedding"] == [0.3, 0.4]
        mock_provider.embed_documents.assert_called_once()

    def test_fallback_text_field(self):
        """Test fallback when text field is missing."""
        mock_provider = Mock()
        mock_provider.embed_documents.return_value = [[0.1, 0.2]]

        processor = EmbeddingProcessor(mock_provider, text_field="content")
        data = [{"id": "1", "description": "Fallback text", "name": "Name"}]

        result = processor.process(data)

        # Should use fallback field
        assert len(result) == 1
        mock_provider.embed_documents.assert_called_once_with(["Fallback text"])


class TestMetadataProcessor:
    """Test MetadataProcessor class."""

    def test_extract_metadata(self):
        """Test metadata extraction."""
        processor = MetadataProcessor(["id", "name", "category"])
        data = [
            {"id": "1", "name": "Item 1", "category": "Cat1", "extra": "value"}
        ]

        result = processor.process(data)

        assert "metadata" in result[0]
        assert result[0]["metadata"]["id"] == "1"
        assert result[0]["metadata"]["name"] == "Item 1"
        assert result[0]["metadata"]["category"] == "Cat1"
        assert "extra" not in result[0]["metadata"]


class TestContentProcessor:
    """Test ContentProcessor class."""

    def test_normalize_content(self):
        """Test content normalization."""
        processor = ContentProcessor(content_field="content", fallback_fields=["description", "name"])
        data = [
            {"id": "1", "description": "Desc 1"},
            {"id": "2", "content": "Content 2"},
            {"id": "3", "name": "Name 3"}
        ]

        result = processor.process(data)

        assert result[0]["content"] == "Desc 1"
        assert result[1]["content"] == "Content 2"
        assert result[2]["content"] == "Name 3"

    def test_minimum_length_validation(self):
        """Test minimum length validation."""
        processor = ContentProcessor(min_length=10)
        data = [{"id": "1", "content": "Short"}]

        # Should process but log warning
        result = processor.process(data)
        assert len(result) == 1
