"""Unit tests for vector_db.validators module."""

import pytest

from src.vector_db.validators import (
    ValidationResult,
    DataValidator,
    SchemaValidator,
    AttackPatternValidator,
    IntegrityValidator,
    ContentValidator
)


class TestSchemaValidator:
    """Test SchemaValidator class."""

    def test_valid_schema(self):
        """Test validation passes for valid schema."""
        validator = SchemaValidator(required_fields=["id", "content"])
        data = [
            {"id": "1", "content": "Content 1"},
            {"id": "2", "content": "Content 2"}
        ]

        result = validator.validate(data)

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.stats["valid_items"] == 2

    def test_missing_fields(self):
        """Test validation fails for missing fields."""
        validator = SchemaValidator(required_fields=["id", "content", "category"])
        data = [
            {"id": "1", "content": "Content 1"},  # Missing category
            {"id": "2", "content": "Content 2", "category": "Cat"}
        ]

        result = validator.validate(data)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "category" in result.errors[0]

    def test_type_validation(self):
        """Test type validation."""
        validator = SchemaValidator(
            required_fields=["id"],
            field_types={"id": str, "price": float}
        )
        data = [
            {"id": "1", "price": "invalid"},  # Wrong type
            {"id": 2, "price": 10.5}  # Wrong type for id
        ]

        result = validator.validate(data)

        assert len(result.warnings) == 2


class TestAttackPatternValidator:
    """Test AttackPatternValidator class."""

    def test_detect_attack_patterns(self):
        """Test detection of attack patterns."""
        validator = AttackPatternValidator(min_attack_documents=2, require_all_types=False)
        data = [
            {"id": "1", "description": "[system] Attack pattern"},
            {"id": "2", "description": "WARNING: Danger ahead"},
            {"id": "3", "description": "Normal product"}
        ]

        result = validator.validate(data)

        assert result.is_valid
        assert result.stats["attack_documents"] == 2
        assert result.stats["attack_types"]["prompt_injection"] > 0
        assert result.stats["attack_types"]["discreditation"] > 0

    def test_insufficient_attacks(self):
        """Test validation fails for insufficient attacks."""
        validator = AttackPatternValidator(min_attack_documents=3)
        data = [
            {"id": "1", "description": "[system] Attack"},
            {"id": "2", "description": "Normal product"}
        ]

        result = validator.validate(data)

        assert not result.is_valid
        assert "expected at least 3" in result.errors[0].lower()


class TestIntegrityValidator:
    """Test IntegrityValidator class."""

    def test_unique_ids(self):
        """Test validation passes for unique IDs."""
        validator = IntegrityValidator()
        data = [
            {"id": "1", "content": "A"},
            {"id": "2", "content": "B"}
        ]

        result = validator.validate(data)

        assert result.is_valid
        assert result.stats["unique_ids"] == 2
        assert result.stats["duplicate_ids"] == 0

    def test_duplicate_ids(self):
        """Test validation fails for duplicate IDs."""
        validator = IntegrityValidator()
        data = [
            {"id": "1", "content": "A"},
            {"id": "1", "content": "B"}  # Duplicate
        ]

        result = validator.validate(data)

        assert not result.is_valid
        assert result.stats["duplicate_ids"] == 1

    def test_empty_ids(self):
        """Test handling of empty IDs."""
        validator = IntegrityValidator(allow_empty_ids=False)
        data = [{"id": "", "content": "A"}]

        result = validator.validate(data)

        assert not result.is_valid
        assert "empty" in result.errors[0].lower()


class TestContentValidator:
    """Test ContentValidator class."""

    def test_valid_content(self):
        """Test validation passes for valid content."""
        validator = ContentValidator(min_length=5)
        data = [{"id": "1", "content": "Valid content here"}]

        result = validator.validate(data)

        assert result.is_valid
        assert result.stats["valid_content"] == 1

    def test_content_too_short(self):
        """Test warning for content below minimum length."""
        validator = ContentValidator(min_length=20)
        data = [{"id": "1", "content": "Short"}]

        result = validator.validate(data)

        assert result.is_valid  # Warnings don't fail validation
        assert len(result.warnings) > 0
        assert result.stats["too_short"] == 1

    def test_encoding_validation(self):
        """Test UTF-8 encoding validation."""
        validator = ContentValidator(check_encoding=True)
        data = [{"id": "1", "content": "Valid UTF-8 content"}]

        result = validator.validate(data)

        assert result.is_valid
