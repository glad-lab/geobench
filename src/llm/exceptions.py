"""
Custom exception classes for LLM client operations.

This module defines domain-specific exceptions that provide context-rich
error handling for different LLM provider failure modes.
"""

from typing import Optional, Dict, Any


class LLMError(Exception):
    """Base exception for all LLM-related errors."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize LLM error with context.

        Args:
            message: Human-readable error message
            provider: LLM provider name (e.g., 'openai', 'anthropic')
            model: Model identifier
            details: Additional error context
        """
        self.provider = provider
        self.model = model
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        """Format error message with context."""
        parts = [super().__str__()]
        if self.provider:
            parts.append(f"Provider: {self.provider}")
        if self.model:
            parts.append(f"Model: {self.model}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)


class LLMRateLimitError(LLMError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Suggested seconds to wait before retry
            **kwargs: Additional context passed to base class
        """
        self.retry_after = retry_after
        if retry_after:
            message = f"{message} (retry after {retry_after}s)"
        super().__init__(message, **kwargs)


class LLMAuthenticationError(LLMError):
    """Raised when API authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        api_key_hint: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize authentication error.

        Args:
            message: Error message
            api_key_hint: Hint about expected API key format or source
            **kwargs: Additional context passed to base class
        """
        self.api_key_hint = api_key_hint
        if api_key_hint:
            message = f"{message}. {api_key_hint}"
        super().__init__(message, **kwargs)


class LLMTimeoutError(LLMError):
    """Raised when API request times out."""

    def __init__(
        self,
        message: str = "Request timeout",
        timeout_seconds: Optional[float] = None,
        **kwargs
    ) -> None:
        """
        Initialize timeout error.

        Args:
            message: Error message
            timeout_seconds: Request timeout duration
            **kwargs: Additional context passed to base class
        """
        self.timeout_seconds = timeout_seconds
        if timeout_seconds:
            message = f"{message} (timeout: {timeout_seconds}s)"
        super().__init__(message, **kwargs)


class LLMValidationError(LLMError):
    """Raised when request or response validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        field: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field name that failed validation
            **kwargs: Additional context passed to base class
        """
        self.field = field
        if field:
            message = f"{message} (field: {field})"
        super().__init__(message, **kwargs)


class LLMModelNotFoundError(LLMError):
    """Raised when specified model is not available."""

    def __init__(
        self,
        message: str = "Model not found",
        available_models: Optional[list] = None,
        **kwargs
    ) -> None:
        """
        Initialize model not found error.

        Args:
            message: Error message
            available_models: List of available models
            **kwargs: Additional context passed to base class
        """
        self.available_models = available_models
        if available_models:
            message = f"{message}. Available models: {', '.join(available_models[:5])}"
        super().__init__(message, **kwargs)


class LLMContextLengthError(LLMError):
    """Raised when input exceeds model's context length."""

    def __init__(
        self,
        message: str = "Context length exceeded",
        input_tokens: Optional[int] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Initialize context length error.

        Args:
            message: Error message
            input_tokens: Number of input tokens
            max_tokens: Maximum allowed tokens
            **kwargs: Additional context passed to base class
        """
        self.input_tokens = input_tokens
        self.max_tokens = max_tokens
        if input_tokens and max_tokens:
            message = f"{message} ({input_tokens} tokens > {max_tokens} max)"
        super().__init__(message, **kwargs)
