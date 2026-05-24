"""
Configuration dataclasses for LLM clients.

This module provides type-safe configuration objects for different LLM providers,
supporting the Builder pattern for complex client construction.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class LLMConfig:
    """Base configuration for all LLM clients."""

    model: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    timeout: int = 60
    max_retries: int = 3
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.temperature < 0.0 or self.temperature > 2.0:
            raise ValueError(f"Temperature must be between 0.0 and 2.0, got {self.temperature}")
        if self.timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {self.timeout}")
        if self.max_retries < 0:
            raise ValueError(f"Max retries must be non-negative, got {self.max_retries}")


@dataclass
class BedrockConfig(LLMConfig):
    """Configuration for AWS Bedrock client."""

    region_name: Optional[str] = None
    aws_profile: Optional[str] = None

    # Default models with appropriate token limits
    DEFAULT_MODELS = {
        "meta.llama3-8b-instruct-v1:0": 2048,
        "meta.llama3-70b-instruct-v1:0": 4096,
        "meta.llama2-13b-chat-v1": 2048,
        "meta.llama2-70b-chat-v1": 4096,
    }

    def __post_init__(self) -> None:
        """Set default max_tokens based on model if not specified."""
        super().__post_init__()
        if self.max_tokens is None and self.model in self.DEFAULT_MODELS:
            self.max_tokens = self.DEFAULT_MODELS[self.model]
        if self.max_tokens is None:
            self.max_tokens = 2048  # Safe default


@dataclass
class OpenAIConfig(LLMConfig):
    """Configuration for OpenAI client."""

    api_key: Optional[str] = None

    # Default models with appropriate token limits
    DEFAULT_MODELS = {
        "gpt-3.5-turbo": 1000,
        "gpt-3.5-turbo-16k": 4000,
        "gpt-4": 2000,
        "gpt-4-32k": 8000,
        "gpt-4-turbo": 4000,
        "gpt-4o": 4000,
        "gpt-4o-mini": 2000,
    }

    def __post_init__(self) -> None:
        """Set default max_tokens based on model if not specified."""
        super().__post_init__()
        if self.max_tokens is None:
            for model_key, tokens in self.DEFAULT_MODELS.items():
                if model_key in self.model:
                    self.max_tokens = tokens
                    break
        if self.max_tokens is None:
            self.max_tokens = 1000  # Safe default


@dataclass
class AnthropicConfig(LLMConfig):
    """Configuration for Anthropic Claude client."""

    api_key: Optional[str] = None

    # Default models with appropriate token limits
    DEFAULT_MODELS = {
        "claude-3-haiku": 1000,
        "claude-3-sonnet": 2000,
        "claude-3-opus": 4000,
        "claude-3-5-sonnet": 2000,
        "claude-3-5-haiku": 1000,
    }

    def __post_init__(self) -> None:
        """Set default max_tokens based on model if not specified."""
        super().__post_init__()
        if self.max_tokens is None:
            for model_key, tokens in self.DEFAULT_MODELS.items():
                if model_key in self.model.lower():
                    self.max_tokens = tokens
                    break
        if self.max_tokens is None:
            self.max_tokens = 1000  # Safe default


@dataclass
class LLaMAConfig(LLMConfig):
    """Configuration for LLaMA API client (legacy)."""

    api_key: Optional[str] = None
    api_base: Optional[str] = None

    def __post_init__(self) -> None:
        """Set default max_tokens if not specified."""
        super().__post_init__()
        if self.max_tokens is None:
            self.max_tokens = 2048  # Standard for LLaMA models


class ConfigBuilder:
    """
    Builder pattern for constructing LLM configurations.

    This allows for fluent, step-by-step configuration construction
    with validation at each step.

    Example:
        >>> config = (ConfigBuilder()
        ...     .for_provider("anthropic")
        ...     .with_model("claude-3-haiku-20240307")
        ...     .with_temperature(0.7)
        ...     .with_max_retries(5)
        ...     .build())
    """

    def __init__(self) -> None:
        """Initialize builder with default values."""
        self._provider: Optional[str] = None
        self._config_class: Optional[type] = None
        self._params: Dict[str, Any] = {}

    def for_provider(self, provider: str) -> 'ConfigBuilder':
        """
        Set the LLM provider.

        Args:
            provider: Provider name ('openai', 'anthropic', 'bedrock', 'llama')

        Returns:
            Self for method chaining
        """
        provider_map = {
            'openai': OpenAIConfig,
            'anthropic': AnthropicConfig,
            'bedrock': BedrockConfig,
            'llama': LLaMAConfig,
        }
        self._provider = provider.lower()
        self._config_class = provider_map.get(self._provider)
        if not self._config_class:
            raise ValueError(f"Unknown provider: {provider}")
        return self

    def with_model(self, model: str) -> 'ConfigBuilder':
        """Set the model name."""
        self._params['model'] = model
        return self

    def with_temperature(self, temperature: float) -> 'ConfigBuilder':
        """Set the generation temperature."""
        self._params['temperature'] = temperature
        return self

    def with_max_tokens(self, max_tokens: int) -> 'ConfigBuilder':
        """Set the maximum tokens to generate."""
        self._params['max_tokens'] = max_tokens
        return self

    def with_timeout(self, timeout: int) -> 'ConfigBuilder':
        """Set the request timeout in seconds."""
        self._params['timeout'] = timeout
        return self

    def with_max_retries(self, max_retries: int) -> 'ConfigBuilder':
        """Set the maximum retry attempts."""
        self._params['max_retries'] = max_retries
        return self

    def with_api_key(self, api_key: str) -> 'ConfigBuilder':
        """Set the API key."""
        self._params['api_key'] = api_key
        return self

    def with_region(self, region: str) -> 'ConfigBuilder':
        """Set AWS region (Bedrock only)."""
        self._params['region_name'] = region
        return self

    def with_profile(self, profile: str) -> 'ConfigBuilder':
        """Set AWS profile (Bedrock only)."""
        self._params['aws_profile'] = profile
        return self

    def with_api_base(self, api_base: str) -> 'ConfigBuilder':
        """Set API base URL (LLaMA only)."""
        self._params['api_base'] = api_base
        return self

    def with_extra(self, **kwargs) -> 'ConfigBuilder':
        """Add extra parameters to configuration."""
        self._params.setdefault('extra_params', {}).update(kwargs)
        return self

    def build(self) -> LLMConfig:
        """
        Build and validate the configuration.

        Returns:
            Provider-specific LLMConfig instance

        Raises:
            ValueError: If provider not set or model not specified
        """
        if not self._config_class:
            raise ValueError("Provider must be set before building config")
        if 'model' not in self._params:
            raise ValueError("Model must be specified")

        return self._config_class(**self._params)
