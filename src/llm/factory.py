"""
Factory pattern implementation for creating LLM clients.

This module provides a centralized factory for instantiating provider-specific
LLM clients with consistent configuration and validation.
"""

import os
import logging
from typing import Optional, List, Dict, Any

from .base import LLMClient
from .config import ConfigBuilder, LLMConfig
from .exceptions import LLMValidationError

logger = logging.getLogger(__name__)


class LLMClientFactory:
    """
    Factory for creating LLM clients based on provider configuration.

    This implements the Factory pattern to encapsulate client creation logic
    and provide a consistent interface for obtaining provider-specific clients.

    Example:
        >>> factory = LLMClientFactory()
        >>> client = factory.create_client(provider="anthropic", model="claude-3-haiku-20240307")
        >>> response = client.generate_text("Rank these products...")
    """

    # Provider-to-implementation mapping
    _PROVIDERS = {
        'openai': ('OpenAIClient', 'openai_client'),
        'anthropic': ('AnthropicClient', 'anthropic'),
        'bedrock': ('BedrockClient', 'bedrock'),
        'llama': ('LLaMAClient', 'llama'),
    }

    @classmethod
    def create_client(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[LLMConfig] = None,
        **kwargs
    ) -> LLMClient:
        """
        Create appropriate LLM client based on provider.

        Args:
            provider: API provider ('openai', 'anthropic', 'bedrock', 'llama')
                     If None, reads from API_PROVIDER environment variable
            model: Model name. If None, reads from LLM_MODEL environment variable
            config: Pre-built configuration object (overrides other parameters)
            **kwargs: Additional client parameters passed to constructor

        Returns:
            Configured LLM client instance

        Raises:
            LLMValidationError: If provider is unsupported or configuration is invalid

        Example:
            >>> # Using environment variables
            >>> client = LLMClientFactory.create_client()
            >>>
            >>> # Explicit configuration
            >>> client = LLMClientFactory.create_client(
            ...     provider="anthropic",
            ...     model="claude-3-haiku-20240307",
            ...     temperature=0.7
            ... )
        """
        # Use configuration object if provided
        if config:
            return cls._create_from_config(config)

        # Resolve provider and model from parameters or environment
        provider = cls._resolve_provider(provider)
        model = cls._resolve_model(model, provider)

        logger.info(f"Creating {provider} client with model: {model}")

        # Validate provider
        if provider not in cls._PROVIDERS:
            raise LLMValidationError(
                f"Unsupported provider: {provider}",
                field='provider',
                details={
                    'supported_providers': list(cls._PROVIDERS.keys()),
                    'requested': provider
                }
            )

        # Get provider implementation
        class_name, module_name = cls._PROVIDERS[provider]

        try:
            # Dynamic import of provider module
            from importlib import import_module
            module = import_module(f'.{module_name}', package='llm')
            client_class = getattr(module, class_name)

            # Instantiate client
            return client_class(model=model, **kwargs)

        except ImportError as e:
            raise LLMValidationError(
                f"Failed to import {provider} client: {e}",
                provider=provider,
                details={'error': str(e)}
            ) from e

        except Exception as e:
            raise LLMValidationError(
                f"Failed to create {provider} client: {e}",
                provider=provider,
                model=model,
                details={'error': str(e)}
            ) from e

    @classmethod
    def _create_from_config(cls, config: LLMConfig) -> LLMClient:
        """
        Create client from configuration object.

        Args:
            config: Provider-specific configuration

        Returns:
            Configured LLM client
        """
        # Determine provider from config type
        from .config import OpenAIConfig, AnthropicConfig, BedrockConfig, LLaMAConfig

        provider_map = {
            OpenAIConfig: 'openai',
            AnthropicConfig: 'anthropic',
            BedrockConfig: 'bedrock',
            LLaMAConfig: 'llama',
        }

        provider = provider_map.get(type(config))
        if not provider:
            raise LLMValidationError(
                f"Unknown configuration type: {type(config)}",
                details={'config_type': str(type(config))}
            )

        # Extract parameters from config
        params = {
            'model': config.model,
            'temperature': config.temperature,
            'max_tokens': config.max_tokens,
            'timeout': config.timeout,
            'max_retries': config.max_retries,
            **config.extra_params
        }

        # Add provider-specific parameters
        if hasattr(config, 'api_key') and config.api_key:
            params['api_key'] = config.api_key
        if hasattr(config, 'region_name') and config.region_name:
            params['region_name'] = config.region_name
        if hasattr(config, 'aws_profile') and config.aws_profile:
            params['aws_profile'] = config.aws_profile
        if hasattr(config, 'api_base') and config.api_base:
            params['api_base'] = config.api_base

        return cls.create_client(provider=provider, **params)

    @staticmethod
    def _resolve_provider(provider: Optional[str]) -> str:
        """
        Resolve provider from parameter or environment.

        Args:
            provider: Provider string or None

        Returns:
            Resolved provider name

        Raises:
            LLMValidationError: If provider cannot be resolved
        """
        if provider:
            return provider.lower()

        provider = os.getenv("API_PROVIDER")
        if provider:
            return provider.lower()

        raise LLMValidationError(
            "Provider not specified",
            field='provider',
            details={
                'hint': 'Set API_PROVIDER environment variable or pass provider parameter'
            }
        )

    @staticmethod
    def _resolve_model(model: Optional[str], provider: str) -> str:
        """
        Resolve model from parameter or environment with provider-specific defaults.

        Args:
            model: Model string or None
            provider: Provider name

        Returns:
            Resolved model name
        """
        if model:
            return model

        # Check environment variable
        model = os.getenv("LLM_MODEL")
        if model:
            return model

        # Provider-specific defaults
        defaults = {
            'openai': 'gpt-3.5-turbo',
            'anthropic': 'claude-3-haiku-20240307',
            'bedrock': 'meta.llama3-8b-instruct-v1:0',
            'llama': 'llama-2-70b-chat',
        }

        default_model = defaults.get(provider)
        if default_model:
            logger.info(f"No model specified, using default for {provider}: {default_model}")
            return default_model

        raise LLMValidationError(
            f"Model not specified for provider: {provider}",
            field='model',
            provider=provider,
            details={
                'hint': 'Set LLM_MODEL environment variable or pass model parameter'
            }
        )

    @staticmethod
    def get_available_models(provider: str) -> List[str]:
        """
        Get list of available models for a provider.

        Args:
            provider: Provider name

        Returns:
            List of available model identifiers

        Example:
            >>> models = LLMClientFactory.get_available_models("anthropic")
            >>> print(models)
            ['claude-3-haiku-20240307', 'claude-3-sonnet-20240229', ...]
        """
        models_map = {
            'openai': [
                "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125",
                "gpt-4", "gpt-4-32k", "gpt-4-1106-preview", "gpt-4-0125-preview",
                "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4o", "gpt-4o-mini"
            ],
            'anthropic': [
                "claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229",
                "claude-3-5-sonnet-20240620", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"
            ],
            'bedrock': [
                "meta.llama3-8b-instruct-v1:0", "meta.llama3-70b-instruct-v1:0",
                "meta.llama2-13b-chat-v1", "meta.llama2-70b-chat-v1",
            ],
            'llama': [
                "llama-2-7b-chat", "llama-2-13b-chat", "llama-2-70b-chat",
                "llama-3-8b-instruct", "code-llama-7b-instruct",
                "code-llama-13b-instruct", "code-llama-34b-instruct"
            ],
        }

        return models_map.get(provider.lower(), [])

    @staticmethod
    def get_supported_providers() -> List[str]:
        """
        Get list of supported provider names.

        Returns:
            List of provider names
        """
        return list(LLMClientFactory._PROVIDERS.keys())


def create_llm_client(**kwargs) -> LLMClient:
    """
    Convenience function to create LLM client with environment-based configuration.

    This is a shorthand for LLMClientFactory.create_client() for simpler usage.

    Args:
        **kwargs: Client configuration parameters

    Returns:
        Configured LLM client instance

    Example:
        >>> from llm import create_llm_client
        >>> client = create_llm_client(provider="anthropic", model="claude-3-haiku-20240307")
    """
    return LLMClientFactory.create_client(**kwargs)
