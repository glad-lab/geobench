"""
OpenAI API client implementation using LangChain.

Provides integration with OpenAI's GPT models with comprehensive error
handling, rate limiting, and automatic retries.
"""

import os
import time
import logging
from typing import Any, Dict, List, Optional

from .base import LLMClient, LLMResponse, RetryMixin
from .config import OpenAIConfig
from .exceptions import (
    LLMError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMTimeoutError,
    LLMModelNotFoundError,
    LLMContextLengthError,
)

logger = logging.getLogger(__name__)


def _import_langchain():
    """Lazy import of LangChain OpenAI integration."""
    try:
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage
        return ChatOpenAI, HumanMessage
    except ImportError as e:
        raise ImportError(
            "langchain-openai is required. Install with: pip install langchain langchain-openai"
        ) from e


class OpenAIClient(LLMClient, RetryMixin):
    """
    OpenAI API client using LangChain with comprehensive error handling.

    Attributes:
        model: OpenAI model identifier
        config: Client configuration
        client: LangChain ChatOpenAI instance
    """

    VALID_MODELS = [
        "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125",
        "gpt-4", "gpt-4-32k", "gpt-4-1106-preview", "gpt-4-0125-preview",
        "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4o", "gpt-4o-mini"
    ]

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        max_retries: int = 3,
        **kwargs
    ) -> None:
        """Initialize OpenAI client."""
        ChatOpenAI, _ = _import_langchain()

        self.config = OpenAIConfig(
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

        if model not in self.VALID_MODELS:
            logger.warning(f"Model '{model}' not in known valid models. Proceeding anyway.")

        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMAuthenticationError(
                "OpenAI API key not found",
                api_key_hint="Set OPENAI_API_KEY environment variable. Get key from: https://platform.openai.com/api-keys",
                provider="openai",
                model=model
            )

        try:
            self.client = ChatOpenAI(
                model=model,
                openai_api_key=api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.timeout,
                max_retries=0,  # Handle retries ourselves
                **kwargs
            )
        except Exception as e:
            raise LLMError(
                f"Failed to initialize OpenAI client: {e}",
                provider="openai",
                model=model
            ) from e

        logger.info(f"Initialized OpenAI client: model={model}, max_tokens={self.config.max_tokens}")

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self.model

    def generate(self, messages: List[Any], **kwargs) -> LLMResponse:
        """Generate response using ChatOpenAI with comprehensive error handling."""
        self.validate_parameters(**kwargs)

        for attempt in range(self.max_retries + 1):
            try:
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = self.timeout

                response = self.client.invoke(messages, **kwargs)

                response_metadata = getattr(response, 'response_metadata', {})
                token_usage = response_metadata.get('token_usage', {})

                return LLMResponse(
                    content=response.content,
                    model=self.model,
                    usage=token_usage if isinstance(token_usage, dict) else {},
                    finish_reason=response_metadata.get('finish_reason', 'stop'),
                    metadata={
                        "provider": "openai",
                        "attempt": attempt + 1,
                        "response_metadata": response_metadata
                    }
                )

            except Exception as e:
                error = self._handle_error(e, attempt)

                if self._should_retry(error, attempt, self.max_retries):
                    delay = self._calculate_backoff(attempt)
                    logger.warning(f"Retrying after {delay:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})")
                    time.sleep(delay)
                    continue
                else:
                    raise error

        raise LLMError("Unexpected error in retry loop", provider="openai", model=self.model)

    def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from text prompt."""
        _, HumanMessage = _import_langchain()
        messages = [HumanMessage(content=prompt)]
        return self.generate(messages, **kwargs)

    def _handle_error(self, error: Exception, attempt: int) -> Exception:
        """Convert provider-specific errors to domain exceptions."""
        error_msg = str(error).lower()

        if "rate limit" in error_msg or "429" in error_msg:
            return LLMRateLimitError(
                "OpenAI rate limit exceeded",
                provider="openai",
                model=self.model,
                details={"attempt": attempt + 1}
            )

        if "invalid api key" in error_msg or "unauthorized" in error_msg:
            return LLMAuthenticationError(
                "Invalid OpenAI API key",
                api_key_hint="Check OPENAI_API_KEY environment variable",
                provider="openai",
                model=self.model
            )

        if "model not found" in error_msg or "does not exist" in error_msg:
            return LLMModelNotFoundError(
                f"Model '{self.model}' not available",
                available_models=self.VALID_MODELS,
                provider="openai",
                model=self.model
            )

        if "context length" in error_msg or "maximum context" in error_msg:
            return LLMContextLengthError(
                f"Input too long for model '{self.model}'",
                provider="openai",
                model=self.model
            )

        if "timeout" in error_msg:
            return LLMTimeoutError(
                "OpenAI request timeout",
                timeout_seconds=self.timeout,
                provider="openai",
                model=self.model
            )

        return LLMError(
            f"OpenAI API error: {error}",
            provider="openai",
            model=self.model,
            details={"attempt": attempt + 1, "original_error": str(error)}
        )
