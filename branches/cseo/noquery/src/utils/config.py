"""
Configuration utilities for the noquery project.

Provides unified API key resolution and configuration management.
"""

import os
import warnings
from pathlib import Path
from typing import Optional

from .data_loading import read_json


def resolve_openai_api_key(
    config_path: str = "config.json",
    raise_on_missing: bool = True
) -> Optional[str]:
    """
    Resolve OpenAI API key from multiple sources.

    Priority order:
    1. Environment variable OPENAI_API_KEY
    2. config.json file (if exists)
    3. .env file support (via environment)
    4. Error or None (based on raise_on_missing)

    Args:
        config_path: Path to config.json file (relative to current directory)
        raise_on_missing: If True, raise EnvironmentError when key not found.
                         If False, return None and issue warning.

    Returns:
        API key string, or None if raise_on_missing=False and key not found

    Raises:
        EnvironmentError: If API key not found and raise_on_missing=True
    """
    # Check environment variable first
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key

    # Try config.json
    if os.path.exists(config_path):
        try:
            cfg = read_json(config_path)
            if isinstance(cfg, dict):
                key = cfg.get("OPENAI_API_KEY")
                if key:
                    # Set in environment for downstream libraries
                    os.environ["OPENAI_API_KEY"] = key
                    return key
        except Exception as e:
            warnings.warn(f"Failed to read config file {config_path}: {e}")

    # Try legacy fallback (should be empty after security fixes)
    try:
        from noquery.src.config.keys import OPENAI_API_KEY_FALLBACK
        if OPENAI_API_KEY_FALLBACK:
            warnings.warn(
                "Using OPENAI_API_KEY_FALLBACK from keys.py. "
                "This is deprecated and insecure. Please use environment variables or config.json.",
                DeprecationWarning
            )
            os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY_FALLBACK
            return OPENAI_API_KEY_FALLBACK
    except (ImportError, AttributeError):
        pass

    # Not found
    error_msg = (
        "OPENAI_API_KEY not found. Please set it using one of:\n"
        "1. Environment variable: export OPENAI_API_KEY='sk-...'\n"
        "2. Config file: Create config.json with {\"OPENAI_API_KEY\": \"sk-...\"}\n"
        "3. .env file: Create .env with OPENAI_API_KEY=sk-..."
    )

    if raise_on_missing:
        raise EnvironmentError(error_msg)
    else:
        warnings.warn(error_msg)
        return None


def load_dotenv_if_available():
    """
    Load .env file if python-dotenv is installed.

    This is a convenience function that automatically loads environment
    variables from a .env file if the python-dotenv package is available.
    """
    try:
        from dotenv import load_dotenv
        env_path = Path.cwd() / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        # python-dotenv not installed, skip
        pass


def setup_api_keys(config_path: str = "config.json"):
    """
    Set up all required API keys for the project.

    This is a convenience function that should be called at the start
    of each script to ensure all API keys are properly configured.

    Args:
        config_path: Path to config.json file

    Raises:
        EnvironmentError: If required API keys are not found
    """
    # Try to load .env first
    load_dotenv_if_available()

    # Resolve OpenAI key
    resolve_openai_api_key(config_path, raise_on_missing=True)

    # Could add other API keys here in the future
    # e.g., Anthropic, Cohere, etc.
