"""Unit tests for vector_db.populator module."""

import pytest
from unittest.mock import Mock, MagicMock, patch

from src.vector_db.populator import (
    PopulationEvent,
    PopulationResult,
    VectorDBPopulator
)
from src.vector_db.loaders import DataLoader
from src.vector_db.processors import DataProcessor
from src.vector_db.validators import DataValidator, ValidationResult
from src.vector_db.exceptions import PopulationError


class MockLoader(DataLoader):
    """Mock data loader for testing."""

    def __init__(self, data):
        self.data = data

    def validate_source(self):
        return True

    def load(self):
        return self.data


class MockProcessor(DataProcessor):
    """Mock data processor for testing."""

    def process(self, data):
        return [{"processed": True, **item} for item in data]


class MockValidator(DataValidator):
    """Mock data validator for testing."""

    def __init__(self, is_valid=True):
        self.is_valid = is_valid

    def validate(self, data):
        return ValidationResult(
            is_valid=self.is_valid,
            errors=[] if self.is_valid else ["Mock validation error"],
            warnings=[],
            stats={"total": len(data)}
        )


class TestVectorDBPopulator:
    """Test VectorDBPopulator class."""

    def test_builder_pattern(self):
        """Test Builder pattern method chaining."""
        mock_vector_store = Mock()
        loader = MockLoader([])
        processor = MockProcessor()
        validator = MockValidator()

        populator = (VectorDBPopulator(mock_vector_store)
            .add_loader(loader)
            .add_processor(processor)
            .add_validator(validator)
            .with_progress_tracking(lambda e: None))

        assert len(populator.loaders) == 1
        assert len(populator.processors) == 1
        assert len(populator.validators) == 1
        assert populator.progress_callback is not None

    def test_successful_population(self):
        """Test successful population workflow."""
        # Mock vector store
        mock_vector_store = Mock()
        mock_vector_store.add_documents.return_value = True

        # Create populator with mock components
        loader = MockLoader([{"id": "1", "content": "Test"}])
        processor = MockProcessor()
        validator = MockValidator(is_valid=True)

        populator = (VectorDBPopulator(mock_vector_store)
            .add_loader(loader)
            .add_processor(processor)
            .add_validator(validator))

        result = populator.populate()

        assert result.success
        assert result.documents_processed == 1
        assert result.documents_stored == 1
        assert len(result.errors) == 0

        # Verify vector store was called
        mock_vector_store.add_documents.assert_called_once()

    def test_population_with_reset(self):
        """Test population with collection reset."""
        mock_vector_store = Mock()
        mock_vector_store.add_documents.return_value = True
        mock_vector_store.clear_collection.return_value = True

        loader = MockLoader([{"id": "1"}])
        populator = VectorDBPopulator(mock_vector_store).add_loader(loader)

        result = populator.populate(reset=True)

        assert result.success
        mock_vector_store.clear_collection.assert_called_once()

    def test_population_without_loaders(self):
        """Test error when no loaders configured."""
        mock_vector_store = Mock()
        populator = VectorDBPopulator(mock_vector_store)

        result = populator.populate()

        # Should fail gracefully without raising
        assert not result.success
        assert any("no loaders" in str(e).lower() for e in result.errors)

    def test_validation_failure(self):
        """Test population continues with validation failures."""
        mock_vector_store = Mock()
        mock_vector_store.add_documents.return_value = True

        loader = MockLoader([{"id": "1"}])
        validator = MockValidator(is_valid=False)

        populator = (VectorDBPopulator(mock_vector_store)
            .add_loader(loader)
            .add_validator(validator))

        result = populator.populate()

        assert not result.success  # Failed due to validation errors
        assert len(result.errors) > 0

    def test_progress_tracking(self):
        """Test progress event emission."""
        mock_vector_store = Mock()
        mock_vector_store.add_documents.return_value = True

        events = []

        def track_progress(event):
            events.append(event)

        loader = MockLoader([{"id": "1"}])
        populator = (VectorDBPopulator(mock_vector_store)
            .add_loader(loader)
            .with_progress_tracking(track_progress))

        result = populator.populate()

        # Should have events for Loading, Processing, Storing stages
        assert len(events) >= 3
        stages = [e.stage for e in events]
        assert "Loading" in stages
        assert "Storing" in stages

    def test_multiple_loaders(self):
        """Test population with multiple loaders."""
        mock_vector_store = Mock()
        mock_vector_store.add_documents.return_value = True

        loader1 = MockLoader([{"id": "1"}])
        loader2 = MockLoader([{"id": "2"}, {"id": "3"}])

        populator = (VectorDBPopulator(mock_vector_store)
            .add_loader(loader1)
            .add_loader(loader2))

        result = populator.populate()

        assert result.success
        assert result.documents_processed == 3

    def test_skip_validation(self):
        """Test skipping validation stage."""
        mock_vector_store = Mock()
        mock_vector_store.add_documents.return_value = True

        loader = MockLoader([{"id": "1"}])
        validator = MockValidator(is_valid=False)  # Would fail

        populator = (VectorDBPopulator(mock_vector_store)
            .add_loader(loader)
            .add_validator(validator))

        result = populator.populate(skip_validation=True)

        # Should succeed because validation was skipped
        assert result.success
        assert len(result.validation_results) == 0


class TestPopulationResult:
    """Test PopulationResult dataclass."""

    def test_result_str_representation(self):
        """Test string representation of result."""
        result = PopulationResult(
            success=True,
            documents_processed=10,
            documents_stored=10,
            errors=[],
            warnings=["Warning 1"],
            duration=5.5,
            metadata={"loaders": 2}
        )

        str_repr = str(result)
        assert "SUCCESS" in str_repr
        assert "10" in str_repr
        assert "5.5" in str_repr


class TestPopulationEvent:
    """Test PopulationEvent dataclass."""

    def test_event_str_representation(self):
        """Test string representation of event."""
        event = PopulationEvent(
            stage="Loading",
            progress=50.0,
            message="Loading data"
        )

        str_repr = str(event)
        assert "Loading" in str_repr
        assert "50" in str_repr
        assert "Loading data" in str_repr
