"""
LLM client module for multi-provider language model integration.

This module provides a unified interface for interacting with different LLM providers
including AWS Bedrock, OpenAI, Anthropic Claude, and legacy LLaMA.

Classes:
    LLMResponse: Standardized response format across all providers
    LLMClient: Abstract base class for LLM clients
    LLMClientFactory: Factory for creating provider-specific clients
    BedrockClient: AWS Bedrock client implementation
    OpenAIClient: OpenAI client implementation
    AnthropicClient: Anthropic Claude client implementation
    LLaMAClient: Legacy LLaMA client implementation

Example:
    >>> from llm import create_llm_client
    >>> client = create_llm_client(provider="anthropic", model="claude-3-haiku-20240307")
    >>> response = client.generate_text("Rank these products...")
    >>> print(response.content)
"""

from .base import LLMResponse, LLMClient
from .factory import LLMClientFactory, create_llm_client
from .bedrock import BedrockClient
from .openai_client import OpenAIClient
from .anthropic import AnthropicClient
from .llama import LLaMAClient
from .config import (
    LLMConfig,
    BedrockConfig,
    OpenAIConfig,
    AnthropicConfig,
    LLaMAConfig,
)
from .exceptions import (
    LLMError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMTimeoutError,
    LLMValidationError,
)

__all__ = [
    # Core classes
    'LLMResponse',
    'LLMClient',
    'LLMClientFactory',
    'create_llm_client',

    # Provider implementations
    'BedrockClient',
    'OpenAIClient',
    'AnthropicClient',
    'LLaMAClient',

    # Configuration
    'LLMConfig',
    'BedrockConfig',
    'OpenAIConfig',
    'AnthropicConfig',
    'LLaMAConfig',

    # Exceptions
    'LLMError',
    'LLMRateLimitError',
    'LLMAuthenticationError',
    'LLMTimeoutError',
    'LLMValidationError',
]

__version__ = '2.0.0'
