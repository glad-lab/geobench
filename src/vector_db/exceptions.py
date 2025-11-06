"""
Custom exceptions for vector database operations.

This module defines the exception hierarchy for vector database operations,
providing specific error types for different failure scenarios.

Exception Hierarchy:
    VectorDBError (base)
    ├── DataLoadError: Data loading failures
    ├── DataSourceError: Invalid or missing data sources
    ├── ProcessingError: Data processing failures
    ├── ValidationError: Data validation failures
    ├── PopulationError: Database population failures
    └── EmbeddingError: Embedding generation failures

Example:
    >>> from vector_db.exceptions import DataLoadError
    >>> try:
    ...     loader.load()
    ... except DataLoadError as e:
    ...     logger.error(f"Failed to load data: {e}")
"""

from typing import Optional, Any


class VectorDBError(Exception):
    """Base exception for all vector database operations.

    Attributes:
        message: Error message
        details: Additional error details
        original_error: Original exception if wrapped
    """

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize vector database error.

        Args:
            message: Human-readable error message
            details: Additional error context
            original_error: Original exception if this wraps another error
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.original_error = original_error

    def __str__(self) -> str:
        """Format error message with details."""
        parts = [self.message]

        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            parts.append(f"Details: {details_str}")

        if self.original_error:
            parts.append(f"Caused by: {type(self.original_error).__name__}: {self.original_error}")

        return " | ".join(parts)


class DataLoadError(VectorDBError):
    """Raised when data loading fails.

    This exception is raised when data cannot be loaded from the source,
    such as file read errors, parsing errors, or invalid data formats.

    Example:
        >>> raise DataLoadError(
        ...     "Failed to load products",
        ...     details={"file": "products.json", "line": 42},
        ...     original_error=json_decode_error
        ... )
    """
    pass


class DataSourceError(VectorDBError):
    """Raised when data source is invalid or inaccessible.

    This exception is raised when the data source doesn't exist,
    is not accessible, or doesn't meet validation requirements.

    Example:
        >>> raise DataSourceError(
        ...     "Dataset file not found",
        ...     details={"path": "/path/to/products.json"}
        ... )
    """
    pass


class ProcessingError(VectorDBError):
    """Raised when data processing fails.

    This exception is raised when data processing operations fail,
    such as transformation errors, batch processing failures, or
    embedding generation errors.

    Example:
        >>> raise ProcessingError(
        ...     "Failed to generate embeddings",
        ...     details={"batch_size": 100, "failed_count": 5}
        ... )
    """
    pass


class ValidationError(VectorDBError):
    """Raised when data validation fails.

    This exception is raised when data doesn't meet validation requirements,
    such as missing required fields, invalid schemas, or integrity violations.

    Example:
        >>> raise ValidationError(
        ...     "Missing required fields",
        ...     details={"missing_fields": ["id", "description"], "item_count": 10}
        ... )
    """
    pass


class PopulationError(VectorDBError):
    """Raised when database population fails.

    This exception is raised when the vector database population process
    encounters errors, such as connection failures, insertion errors, or
    collection creation failures.

    Example:
        >>> raise PopulationError(
        ...     "Failed to populate vector database",
        ...     details={"collection": "adversarial_seo", "documents_failed": 25}
        ... )
    """
    pass


class EmbeddingError(VectorDBError):
    """Raised when embedding generation fails.

    This exception is raised when embedding generation encounters errors,
    such as API failures, rate limits, or invalid input.

    Example:
        >>> raise EmbeddingError(
        ...     "OpenAI API rate limit exceeded",
        ...     details={"provider": "openai", "texts_failed": 100}
        ... )
    """
    pass
