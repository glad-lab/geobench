"""
Data validators for vector database population.

This module provides abstract and concrete data validator implementations
for validating data integrity, schema compliance, and attack pattern
preservation before insertion into the vector database.

Classes:
    ValidationResult: Result of validation operation
    DataValidator: Abstract base class for all data validators
    SchemaValidator: Validates data against required schema
    AttackPatternValidator: Validates attack patterns are preserved
    IntegrityValidator: Validates data integrity (no duplicates, valid IDs)
    ContentValidator: Validates content quality and requirements

Example:
    >>> from vector_db import SchemaValidator, AttackPatternValidator
    >>> schema_val = SchemaValidator(required_fields=["id", "content", "category"])
    >>> attack_val = AttackPatternValidator()
    >>>
    >>> result = schema_val.validate(documents)
    >>> if not result.is_valid:
    ...     print(f"Validation errors: {result.errors}")
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass, field
import logging
import re

from .exceptions import ValidationError as VectorDBValidationError

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validation operation.

    Attributes:
        is_valid: Whether validation passed
        errors: List of error messages
        warnings: List of warning messages
        stats: Validation statistics
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Format validation result as string."""
        status = "VALID" if self.is_valid else "INVALID"
        parts = [f"Validation: {status}"]

        if self.errors:
            parts.append(f"Errors: {len(self.errors)}")
            parts.extend(f"  - {error}" for error in self.errors[:5])
            if len(self.errors) > 5:
                parts.append(f"  ... and {len(self.errors) - 5} more errors")

        if self.warnings:
            parts.append(f"Warnings: {len(self.warnings)}")
            parts.extend(f"  - {warning}" for warning in self.warnings[:5])
            if len(self.warnings) > 5:
                parts.append(f"  ... and {len(self.warnings) - 5} more warnings")

        if self.stats:
            parts.append("Statistics:")
            for key, value in self.stats.items():
                parts.append(f"  {key}: {value}")

        return "\n".join(parts)


class DataValidator(ABC):
    """Abstract base class for data validators.

    All data validators must implement the validate() method to check
    data quality and integrity.
    """

    @abstractmethod
    def validate(self, data: List[Dict[str, Any]]) -> ValidationResult:
        """Validate data.

        Args:
            data: Data to validate

        Returns:
            Validation result with errors, warnings, and statistics
        """
        pass


class SchemaValidator(DataValidator):
    """Validates data against required schema.

    This validator checks that all items have required fields and
    optionally validates field types.

    Example:
        >>> validator = SchemaValidator(
        ...     required_fields=["id", "content", "category"],
        ...     optional_fields=["name", "description"]
        ... )
        >>> result = validator.validate(documents)
        >>> assert result.is_valid
    """

    def __init__(
        self,
        required_fields: List[str],
        optional_fields: Optional[List[str]] = None,
        field_types: Optional[Dict[str, type]] = None
    ):
        """Initialize schema validator.

        Args:
            required_fields: Fields that must be present in all items
            optional_fields: Fields that may be present (for documentation)
            field_types: Expected types for fields (e.g., {"id": str, "price": float})
        """
        self.required_fields = required_fields
        self.optional_fields = optional_fields or []
        self.field_types = field_types or {}

        logger.debug(
            f"Initialized SchemaValidator with required_fields={required_fields}, "
            f"field_types={field_types}"
        )

    def validate(self, data: List[Dict[str, Any]]) -> ValidationResult:
        """Check all items have required fields.

        Args:
            data: Data to validate

        Returns:
            Validation result with missing field errors
        """
        errors = []
        warnings = []
        stats = {
            "total_items": len(data),
            "valid_items": 0,
            "missing_field_count": 0,
            "type_mismatch_count": 0
        }

        for i, item in enumerate(data):
            item_id = item.get("id", f"item_{i}")
            item_errors = []

            # Check required fields
            for field in self.required_fields:
                if field not in item:
                    item_errors.append(f"Missing required field '{field}'")
                    stats["missing_field_count"] += 1

            # Check field types if specified
            for field, expected_type in self.field_types.items():
                if field in item and not isinstance(item[field], expected_type):
                    actual_type = type(item[field]).__name__
                    expected_type_name = expected_type.__name__
                    warnings.append(
                        f"Item {item_id}: Field '{field}' has type {actual_type}, "
                        f"expected {expected_type_name}"
                    )
                    stats["type_mismatch_count"] += 1

            if item_errors:
                errors.append(f"Item {item_id}: {', '.join(item_errors)}")
            else:
                stats["valid_items"] += 1

        is_valid = len(errors) == 0

        if is_valid:
            logger.info(f"Schema validation passed for {len(data)} items")
        else:
            logger.warning(
                f"Schema validation failed: {len(errors)} errors, {len(warnings)} warnings"
            )

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            stats=stats
        )


class AttackPatternValidator(DataValidator):
    """Validates attack patterns are preserved in dataset.

    This validator ensures that adversarial attack patterns from the
    paper are present in the dataset for research purposes.

    Attack patterns checked:
    - Prompt injection: [system] instructions
    - Discreditation: WARNING statements
    - Persuasion: blind puppies, wildlife conservation

    Example:
        >>> validator = AttackPatternValidator()
        >>> result = validator.validate(documents)
        >>> print(f"Found {result.stats['attack_documents']} attack documents")
    """

    # Attack patterns from original paper
    ATTACK_PATTERNS = {
        "prompt_injection": [
            r"\[system\]",
            r"mention only",
            r"ignore.*instructions"
        ],
        "discreditation": [
            r"WARNING:",
            r"harmful materials",
            r"toxic compounds",
            r"safety certification"
        ],
        "persuasion": [
            r"blind puppies",
            r"wildlife conservation",
            r"guide dog",
            r"rainforest habitat"
        ]
    }

    def __init__(
        self,
        min_attack_documents: int = 3,
        require_all_types: bool = True
    ):
        """Initialize attack pattern validator.

        Args:
            min_attack_documents: Minimum number of attack documents expected
            require_all_types: Whether all attack types must be present
        """
        self.min_attack_documents = min_attack_documents
        self.require_all_types = require_all_types

        logger.debug(
            f"Initialized AttackPatternValidator with min_attack_documents={min_attack_documents}, "
            f"require_all_types={require_all_types}"
        )

    def validate(self, data: List[Dict[str, Any]]) -> ValidationResult:
        """Check attack patterns exist in dataset.

        Args:
            data: Data to validate

        Returns:
            Validation result with attack pattern statistics
        """
        errors = []
        warnings = []
        stats = {
            "total_documents": len(data),
            "attack_documents": 0,
            "attack_types": {}
        }

        # Initialize attack type counters
        for attack_type in self.ATTACK_PATTERNS:
            stats["attack_types"][attack_type] = 0

        # Check each document for attack patterns
        for item in data:
            content = item.get("description", item.get("content", ""))
            if not content:
                continue

            content_lower = content.lower()
            found_attack = False

            # Check each attack type
            for attack_type, patterns in self.ATTACK_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        stats["attack_types"][attack_type] += 1
                        found_attack = True
                        break

                if found_attack:
                    break

            if found_attack:
                stats["attack_documents"] += 1

        # Validate minimum attack documents
        if stats["attack_documents"] < self.min_attack_documents:
            errors.append(
                f"Found only {stats['attack_documents']} attack documents, "
                f"expected at least {self.min_attack_documents}"
            )

        # Validate all attack types present if required
        if self.require_all_types:
            for attack_type, count in stats["attack_types"].items():
                if count == 0:
                    errors.append(f"No documents found with {attack_type} attack pattern")

        # Add warnings for low counts
        for attack_type, count in stats["attack_types"].items():
            if count > 0 and count < 2:
                warnings.append(f"Only {count} document with {attack_type} attack pattern")

        is_valid = len(errors) == 0

        if is_valid:
            logger.info(
                f"Attack pattern validation passed: "
                f"{stats['attack_documents']} attack documents found"
            )
        else:
            logger.warning(
                f"Attack pattern validation failed: {len(errors)} errors"
            )

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            stats=stats
        )


class IntegrityValidator(DataValidator):
    """Validates data integrity (no duplicates, valid IDs, etc.).

    This validator checks for:
    - Duplicate IDs
    - Missing or empty IDs
    - Duplicate content (exact matches)
    - Invalid field values

    Example:
        >>> validator = IntegrityValidator(check_duplicate_content=True)
        >>> result = validator.validate(documents)
        >>> assert result.is_valid
    """

    def __init__(
        self,
        check_duplicate_content: bool = False,
        allow_empty_ids: bool = False
    ):
        """Initialize integrity validator.

        Args:
            check_duplicate_content: Whether to check for duplicate content
            allow_empty_ids: Whether to allow empty/missing IDs
        """
        self.check_duplicate_content = check_duplicate_content
        self.allow_empty_ids = allow_empty_ids

        logger.debug(
            f"Initialized IntegrityValidator with check_duplicate_content={check_duplicate_content}, "
            f"allow_empty_ids={allow_empty_ids}"
        )

    def validate(self, data: List[Dict[str, Any]]) -> ValidationResult:
        """Check data integrity.

        Args:
            data: Data to validate

        Returns:
            Validation result with integrity errors
        """
        errors = []
        warnings = []
        stats = {
            "total_documents": len(data),
            "unique_ids": 0,
            "duplicate_ids": 0,
            "empty_ids": 0,
            "duplicate_content": 0
        }

        # Track IDs and content
        seen_ids: Set[str] = set()
        seen_content: Set[str] = set()
        duplicate_ids: Set[str] = set()

        for i, item in enumerate(data):
            item_id = item.get("id", "")

            # Check for empty IDs
            if not item_id:
                stats["empty_ids"] += 1
                if not self.allow_empty_ids:
                    errors.append(f"Item at index {i} has empty or missing ID")
                continue

            # Check for duplicate IDs
            if item_id in seen_ids:
                stats["duplicate_ids"] += 1
                duplicate_ids.add(item_id)
                errors.append(f"Duplicate ID found: {item_id}")
            else:
                seen_ids.add(item_id)
                stats["unique_ids"] += 1

            # Check for duplicate content if enabled
            if self.check_duplicate_content:
                content = item.get("content", item.get("description", ""))
                if content:
                    if content in seen_content:
                        stats["duplicate_content"] += 1
                        warnings.append(
                            f"Duplicate content found in item {item_id}"
                        )
                    else:
                        seen_content.add(content)

        # Add summary warnings
        if duplicate_ids:
            warnings.append(
                f"Found {len(duplicate_ids)} IDs with duplicates: "
                f"{', '.join(list(duplicate_ids)[:5])}"
            )

        is_valid = len(errors) == 0

        if is_valid:
            logger.info(
                f"Integrity validation passed: {stats['unique_ids']} unique documents"
            )
        else:
            logger.warning(
                f"Integrity validation failed: {len(errors)} errors, {len(warnings)} warnings"
            )

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            stats=stats
        )


class ContentValidator(DataValidator):
    """Validates content quality and requirements.

    This validator checks:
    - Minimum content length
    - Content encoding (valid UTF-8)
    - Presence of meaningful text

    Example:
        >>> validator = ContentValidator(min_length=10, check_encoding=True)
        >>> result = validator.validate(documents)
    """

    def __init__(
        self,
        min_length: int = 0,
        max_length: Optional[int] = None,
        check_encoding: bool = True,
        content_field: str = "content"
    ):
        """Initialize content validator.

        Args:
            min_length: Minimum content length (0 = no minimum)
            max_length: Maximum content length (None = no maximum)
            check_encoding: Whether to validate UTF-8 encoding
            content_field: Field to validate content from
        """
        self.min_length = min_length
        self.max_length = max_length
        self.check_encoding = check_encoding
        self.content_field = content_field

        logger.debug(
            f"Initialized ContentValidator with min_length={min_length}, "
            f"max_length={max_length}, content_field='{content_field}'"
        )

    def validate(self, data: List[Dict[str, Any]]) -> ValidationResult:
        """Validate content quality.

        Args:
            data: Data to validate

        Returns:
            Validation result with content quality errors
        """
        errors = []
        warnings = []
        stats = {
            "total_documents": len(data),
            "valid_content": 0,
            "too_short": 0,
            "too_long": 0,
            "encoding_errors": 0,
            "empty_content": 0
        }

        for i, item in enumerate(data):
            item_id = item.get("id", f"item_{i}")
            content = item.get(self.content_field, "")

            # Check for empty content
            if not content:
                stats["empty_content"] += 1
                warnings.append(f"Item {item_id} has empty {self.content_field}")
                continue

            # Check content length
            content_length = len(content)

            if content_length < self.min_length:
                stats["too_short"] += 1
                warnings.append(
                    f"Item {item_id}: Content too short ({content_length} < {self.min_length})"
                )

            if self.max_length and content_length > self.max_length:
                stats["too_long"] += 1
                warnings.append(
                    f"Item {item_id}: Content too long ({content_length} > {self.max_length})"
                )

            # Check encoding if enabled
            if self.check_encoding:
                try:
                    content.encode('utf-8')
                except UnicodeEncodeError as e:
                    stats["encoding_errors"] += 1
                    errors.append(
                        f"Item {item_id}: Invalid UTF-8 encoding at position {e.start}"
                    )
                    continue

            stats["valid_content"] += 1

        is_valid = len(errors) == 0

        if is_valid:
            logger.info(
                f"Content validation passed: {stats['valid_content']} valid documents"
            )
        else:
            logger.warning(
                f"Content validation failed: {len(errors)} errors, {len(warnings)} warnings"
            )

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            stats=stats
        )
