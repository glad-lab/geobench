"""
LLaMA API client implementation (legacy).

Provides integration with LLaMA models via OpenAI-compatible API.
Note: This is deprecated in favor of BedrockClient for AWS-hosted LLaMA models.
"""

import os
import logging
from typing import Any, Dict, List, Optional

from .base import LLMClient, LLMResponse
from .config import LLaMAConfig
from .exceptions import LLMError, LLMAuthenticationError, LLMValidationError

logger = logging.getLogger(__name__)


def _import_requests():
    """Lazy import of requests library."""
    try:
        import requests
        return requests
    except ImportError as e:
        raise ImportError(
            "requests library is required. Install with: pip install requests"
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


class LLaMAClient(LLMClient):
    """
    LLaMA API client with OpenAI-compatible interface.

    DEPRECATED: Consider using BedrockClient for AWS-hosted LLaMA models.
    """

    def __init__(
        self,
        model: str = "llama-2-70b-chat",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        **kwargs
    ) -> None:
        """Initialize LLaMA client."""
        requests = _import_requests()

        logger.warning(
            "LLaMAClient is deprecated. Consider using BedrockClient for "
            "AWS-hosted LLaMA models with better reliability and performance."
        )

        self.config = LLaMAConfig(
            model=model,
            api_key=api_key,
            api_base=api_base,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_params=kwargs
        )

        self.model = model
        self.api_key = api_key or os.getenv("LLAMA_API_KEY")
        self.api_base = api_base or os.getenv("LLAMA_API_BASE")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.session = requests.Session()

        if not self.api_key or not self.api_base:
            raise LLMAuthenticationError(
                "LLaMA API key and base URL are required",
                api_key_hint="Set LLAMA_API_KEY and LLAMA_API_BASE environment variables",
                provider="llama",
                model=model
            )

        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

        logger.info(f"Initialized LLaMA client: model={model}")

    @property
    def provider_name(self) -> str:
        return "llama"

    @property
    def model_name(self) -> str:
        return self.model

    def _format_messages_for_llama(self, messages: List[Any]) -> str:
        """Format LangChain messages for LLaMA chat format."""
        HumanMessage, SystemMessage = _import_langchain()

        formatted_parts = []

        for message in messages:
            if isinstance(message, SystemMessage):
                formatted_parts.append(f"<s>[INST] <<SYS>>\n{message.content}\n<</SYS>>\n")
            elif isinstance(message, HumanMessage):
                if formatted_parts and not formatted_parts[-1].endswith("[/INST]"):
                    formatted_parts.append(f"{message.content} [/INST]")
                else:
                    formatted_parts.append(f"<s>[INST] {message.content} [/INST]")
            else:
                formatted_parts.append(f"<s>[INST] {message.content} [/INST]")

        return " ".join(formatted_parts)

    def generate(self, messages: List[Any], **kwargs) -> LLMResponse:
        """Generate response using LLaMA API."""
        requests = _import_requests()

        try:
            prompt = self._format_messages_for_llama(messages)

            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "stream": False
            }

            response = self.session.post(
                f"{self.api_base}/completions",
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            result = response.json()

            if "choices" not in result or not result["choices"]:
                raise LLMValidationError(
                    "No choices in LLaMA API response",
                    provider="llama",
                    model=self.model
                )

            choice = result["choices"][0]
            content = choice.get("text", "").strip()

            return LLMResponse(
                content=content,
                model=self.model,
                usage=result.get("usage"),
                finish_reason=choice.get("finish_reason"),
                metadata={"provider": "llama", "api_base": self.api_base}
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"LLaMA API request error: {e}")
            raise LLMError(
                f"LLaMA API request failed: {e}",
                provider="llama",
                model=self.model
            ) from e

        except Exception as e:
            logger.error(f"LLaMA API error: {e}")
            raise LLMError(
                f"LLaMA API error: {e}",
                provider="llama",
                model=self.model
            ) from e

    def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from text prompt."""
        HumanMessage, _ = _import_langchain()
        messages = [HumanMessage(content=prompt)]
        return self.generate(messages, **kwargs)
