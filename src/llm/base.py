"""
Base classes and interfaces for LLM client implementations.

This module defines the abstract base class and common data structures
used across all LLM provider implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LLMResponse:
    """
    Standardized response format for all LLM providers.

    This ensures consistent response handling regardless of the underlying
    provider (OpenAI, Anthropic, Bedrock, etc.).

    Attributes:
        content: Generated text content
        model: Model identifier used for generation
        usage: Token usage statistics (prompt, completion, total)
        finish_reason: Reason for generation completion (stop, length, etc.)
        metadata: Provider-specific metadata and diagnostic information
    """

    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Initialize default values for optional fields."""
        if self.usage is None:
            self.usage = {}
        if self.metadata is None:
            self.metadata = {}

    @property
    def total_tokens(self) -> int:
        """Get total token count from usage statistics."""
        if not self.usage:
            return 0
        return self.usage.get('total_tokens', 0)

    @property
    def prompt_tokens(self) -> int:
        """Get prompt token count from usage statistics."""
        if not self.usage:
            return 0
        return self.usage.get('prompt_tokens', 0)

    @property
    def completion_tokens(self) -> int:
        """Get completion token count from usage statistics."""
        if not self.usage:
            return 0
        return self.usage.get('completion_tokens', 0)

    def __str__(self) -> str:
        """Format response for display."""
        token_info = f"({self.total_tokens} tokens)" if self.usage else ""
        return f"LLMResponse[{self.model}] {token_info}: {self.content[:100]}..."


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.

    This defines the interface that all provider-specific implementations
    must follow, ensuring consistent behavior across different LLM providers.

    The Template Method pattern is used here to define the skeleton of
    the generation algorithm, with provider-specific steps implemented
    in subclasses.
    """

    @abstractmethod
    def generate(
        self,
        messages: List[Any],
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from a list of messages.

        Args:
            messages: List of message objects (format depends on provider)
            **kwargs: Additional generation parameters (temperature, max_tokens, etc.)

        Returns:
            LLMResponse with generated content and metadata

        Raises:
            LLMError: Base exception for LLM-related errors
            LLMRateLimitError: When rate limit is exceeded
            LLMAuthenticationError: When authentication fails
            LLMTimeoutError: When request times out
        """
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from a text prompt.

        This is a convenience method that wraps the prompt in the
        appropriate message format for the provider.

        Args:
            prompt: Text prompt for generation
            **kwargs: Additional generation parameters

        Returns:
            LLMResponse with generated content and metadata

        Raises:
            Same as generate() method
        """
        pass

    def validate_parameters(self, **kwargs) -> None:
        """
        Validate generation parameters.

        Subclasses can override this to add provider-specific validation.

        Args:
            **kwargs: Parameters to validate

        Raises:
            LLMValidationError: When parameters are invalid
        """
        from .exceptions import LLMValidationError

        # Common parameter validation
        if 'temperature' in kwargs:
            temp = kwargs['temperature']
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                raise LLMValidationError(
                    f"Temperature must be between 0 and 2, got {temp}",
                    field='temperature'
                )

        if 'max_tokens' in kwargs:
            max_tok = kwargs['max_tokens']
            if not isinstance(max_tok, int) or max_tok <= 0:
                raise LLMValidationError(
                    f"max_tokens must be positive integer, got {max_tok}",
                    field='max_tokens'
                )

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name for this client."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the model name for this client."""
        pass


class RetryMixin:
    """
    Mixin class providing retry logic with exponential backoff.

    This can be mixed into LLM client implementations to provide
    consistent retry behavior across providers.
    """

    def _should_retry(self, error: Exception, attempt: int, max_retries: int) -> bool:
        """
        Determine if request should be retried based on error type.

        Args:
            error: Exception that occurred
            attempt: Current attempt number (0-indexed)
            max_retries: Maximum number of retry attempts

        Returns:
            True if request should be retried
        """
        from .exceptions import (
            LLMRateLimitError,
            LLMTimeoutError,
            LLMAuthenticationError,
            LLMValidationError,
        )

        # Don't retry if max attempts reached
        if attempt >= max_retries:
            return False

        # Don't retry on auth or validation errors (permanent failures)
        if isinstance(error, (LLMAuthenticationError, LLMValidationError)):
            return False

        # Retry on rate limit and timeout errors
        if isinstance(error, (LLMRateLimitError, LLMTimeoutError)):
            return True

        # Retry on server errors (5xx) - check error message
        error_msg = str(error).lower()
        if any(phrase in error_msg for phrase in ['server error', '5', 'overloaded']):
            return True

        return False

    def _calculate_backoff(
        self,
        attempt: int,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ) -> float:
        """
        Calculate exponential backoff delay with jitter.

        Args:
            attempt: Current attempt number (0-indexed)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds

        Returns:
            Delay in seconds before next retry
        """
        import random

        # Exponential backoff: base_delay * 2^attempt
        delay = min(base_delay * (2 ** attempt), max_delay)

        # Add jitter (random value up to 1 second)
        jitter = random.uniform(0, 1)
        return delay + jitter
