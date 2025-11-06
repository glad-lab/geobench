"""
Anthropic Claude API client implementation.

Provides integration with Anthropic's Claude models with comprehensive error
handling, rate limiting, and automatic retries.
"""

import os
import time
import logging
from typing import Any, Dict, List, Optional, Tuple

from .base import LLMClient, LLMResponse, RetryMixin
from .config import AnthropicConfig
from .exceptions import (
    LLMError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMTimeoutError,
    LLMValidationError,
    LLMModelNotFoundError,
)

logger = logging.getLogger(__name__)

# Lazy imports
def _import_anthropic():
    """Lazy import of Anthropic SDK."""
    try:
        import anthropic
        return anthropic
    except ImportError as e:
        raise ImportError(
            "anthropic library is required. Install with: pip install anthropic"
        ) from e


def _import_langchain():
    """Lazy import of LangChain message types."""
    try:
        from langchain.schema import HumanMessage, SystemMessage
        return HumanMessage, SystemMessage
    except ImportError as e:
        raise ImportError(
            "langchain is required. Install with: pip install langchain"
        ) from e


class AnthropicClient(LLMClient, RetryMixin):
    """
    Anthropic Claude API client with comprehensive error handling and rate limiting.

    This implementation follows the Strategy pattern for message formatting and
    uses the Template Method pattern for retry logic.

    Attributes:
        model: Claude model identifier
        config: Client configuration
        client: Anthropic SDK client instance

    Example:
        >>> client = AnthropicClient(model="claude-3-haiku-20240307")
        >>> response = client.generate_text("Rank these products...")
        >>> print(response.content)
    """

    # Valid Claude model identifiers
    VALID_MODELS = [
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229",
        "claude-3-opus-20240229",
        "claude-3-5-sonnet-20240620",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
    ]

    def __init__(
        self,
        model: str = "claude-3-haiku-20240307",
        api_key: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        max_retries: int = 3,
        **kwargs
    ) -> None:
        """
        Initialize Anthropic client.

        Args:
            model: Claude model name (claude-3-haiku, claude-3-sonnet, claude-3-opus)
            api_key: Anthropic API key (reads from ANTHROPIC_API_KEY if not provided)
            temperature: Generation temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate (auto-set based on model if None)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for rate limiting
            **kwargs: Additional Anthropic client parameters

        Raises:
            LLMAuthenticationError: If API key is not provided or invalid
            LLMValidationError: If model is not valid
        """
        anthropic = _import_anthropic()

        # Create configuration
        self.config = AnthropicConfig(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout or 60,
            max_retries=max_retries,
            extra_params=kwargs
        )

        self.model = model
        self.max_retries = max_retries
        self.timeout = self.config.timeout

        # Validate model
        if model not in self.VALID_MODELS:
            logger.warning(
                f"Model '{model}' not in known valid models: {self.VALID_MODELS}. "
                "Proceeding anyway, but this may fail."
            )

        # Get and validate API key
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMAuthenticationError(
                "Anthropic API key not found",
                api_key_hint=(
                    "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter. "
                    "Get your key from: https://console.anthropic.com/"
                ),
                provider="anthropic",
                model=model
            )

        # Initialize Anthropic client
        try:
            self.client = anthropic.Anthropic(
                api_key=api_key,
                timeout=self.timeout,
                max_retries=0,  # We handle retries ourselves
                **kwargs
            )
        except Exception as e:
            raise LLMError(
                f"Failed to initialize Anthropic client: {e}",
                provider="anthropic",
                model=model
            ) from e

        logger.info(
            f"Initialized Anthropic client: model={model}, "
            f"max_tokens={self.config.max_tokens}, timeout={self.timeout}s"
        )

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "anthropic"

    @property
    def model_name(self) -> str:
        """Get model name."""
        return self.model

    def _format_messages_for_anthropic(
        self,
        messages: List[Any]
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Format LangChain messages for Anthropic Claude API.

        Anthropic has a specific message format where system messages are
        separated from user messages.

        Args:
            messages: List of LangChain message objects

        Returns:
            Tuple of (system_message, formatted_messages)
        """
        HumanMessage, SystemMessage = _import_langchain()

        system_message = ""
        formatted_messages = []

        for message in messages:
            if isinstance(message, SystemMessage):
                system_message = message.content
            elif isinstance(message, HumanMessage):
                formatted_messages.append({
                    "role": "user",
                    "content": message.content
                })
            else:
                # Handle generic message objects
                content = str(message.content) if hasattr(message, 'content') else str(message)
                formatted_messages.append({
                    "role": "user",
                    "content": content
                })

        # Ensure we have at least one message
        if not formatted_messages and messages:
            content = " ".join(str(msg) for msg in messages)
            formatted_messages.append({
                "role": "user",
                "content": content
            })

        return system_message, formatted_messages

    def generate(
        self,
        messages: List[Any],
        **kwargs
    ) -> LLMResponse:
        """
        Generate response using Anthropic Claude API with comprehensive error handling.

        Implements automatic retry logic with exponential backoff for transient errors.

        Args:
            messages: List of message objects (LangChain format)
            **kwargs: Override generation parameters (temperature, max_tokens, etc.)

        Returns:
            LLMResponse with generated content and metadata

        Raises:
            LLMRateLimitError: When rate limit exceeded after retries
            LLMAuthenticationError: When API key is invalid
            LLMTimeoutError: When request times out after retries
            LLMModelNotFoundError: When model is not available
            LLMError: For other API errors
        """
        # Validate parameters
        self.validate_parameters(**kwargs)

        for attempt in range(self.max_retries + 1):
            try:
                # Format messages for Anthropic API
                system_message, formatted_messages = self._format_messages_for_anthropic(messages)

                # Build API parameters
                api_params = {
                    "model": self.model,
                    "messages": formatted_messages,
                    "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                    "temperature": kwargs.get("temperature", self.config.temperature),
                }

                if system_message:
                    api_params["system"] = system_message

                if self.timeout:
                    api_params["timeout"] = self.timeout

                # Make API call
                response = self.client.messages.create(**api_params)

                # Extract content from response
                content = self._extract_content(response)

                # Extract usage statistics
                usage = self._extract_usage(response)

                return LLMResponse(
                    content=content,
                    model=self.model,
                    usage=usage,
                    finish_reason=getattr(response, 'stop_reason', 'stop'),
                    metadata={
                        "provider": "anthropic",
                        "attempt": attempt + 1,
                        "response_id": getattr(response, 'id', None),
                        "response_type": getattr(response, 'type', None)
                    }
                )

            except Exception as e:
                # Handle provider-specific errors
                error = self._handle_error(e, attempt)

                if self._should_retry(error, attempt, self.max_retries):
                    delay = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Retrying after {delay:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                    time.sleep(delay)
                    continue
                else:
                    raise error

        # Should never reach here due to exception handling, but just in case
        raise LLMError(
            "Unexpected error in retry loop",
            provider="anthropic",
            model=self.model
        )

    def generate_text(
        self,
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from text prompt.

        Convenience method that wraps the prompt in a HumanMessage.

        Args:
            prompt: Text prompt for generation
            **kwargs: Override generation parameters

        Returns:
            LLMResponse with generated content and metadata
        """
        HumanMessage, _ = _import_langchain()
        messages = [HumanMessage(content=prompt)]
        return self.generate(messages, **kwargs)

    def _extract_content(self, response: Any) -> str:
        """Extract text content from Anthropic response."""
        if not response.content or len(response.content) == 0:
            return ""

        content_blocks = []
        for block in response.content:
            if hasattr(block, 'text'):
                content_blocks.append(block.text)
            elif hasattr(block, 'content'):
                content_blocks.append(str(block.content))
            else:
                content_blocks.append(str(block))

        return "".join(content_blocks)

    def _extract_usage(self, response: Any) -> Dict[str, int]:
        """Extract token usage from Anthropic response."""
        if not hasattr(response, 'usage'):
            return {}

        return {
            "prompt_tokens": getattr(response.usage, 'input_tokens', 0),
            "completion_tokens": getattr(response.usage, 'output_tokens', 0),
            "total_tokens": (
                getattr(response.usage, 'input_tokens', 0) +
                getattr(response.usage, 'output_tokens', 0)
            )
        }

    def _handle_error(self, error: Exception, attempt: int) -> Exception:
        """
        Convert provider-specific errors to domain exceptions.

        Args:
            error: Original exception from Anthropic API
            attempt: Current attempt number

        Returns:
            Domain-specific exception
        """
        error_msg = str(error).lower()

        # Rate limit errors
        if "rate_limit_error" in error_msg or "429" in error_msg:
            return LLMRateLimitError(
                "Anthropic rate limit exceeded",
                provider="anthropic",
                model=self.model,
                details={"attempt": attempt + 1}
            )

        # Authentication errors
        if "invalid_request_error" in error_msg or "authentication_error" in error_msg:
            return LLMAuthenticationError(
                "Invalid Anthropic API key or request",
                api_key_hint="Check ANTHROPIC_API_KEY environment variable",
                provider="anthropic",
                model=self.model
            )

        # Model not found errors
        if "not_found_error" in error_msg or ("model" in error_msg and "not" in error_msg):
            return LLMModelNotFoundError(
                f"Model '{self.model}' not available",
                available_models=self.VALID_MODELS,
                provider="anthropic",
                model=self.model
            )

        # Server errors (overloaded, internal error)
        if "overloaded_error" in error_msg or "internal_server_error" in error_msg:
            return LLMError(
                "Anthropic server overloaded or experiencing errors",
                provider="anthropic",
                model=self.model,
                details={"attempt": attempt + 1}
            )

        # Timeout errors
        if "timeout" in error_msg:
            return LLMTimeoutError(
                "Anthropic request timeout",
                timeout_seconds=self.timeout,
                provider="anthropic",
                model=self.model
            )

        # Generic error
        return LLMError(
            f"Anthropic API error: {error}",
            provider="anthropic",
            model=self.model,
            details={"attempt": attempt + 1, "original_error": str(error)}
        )
