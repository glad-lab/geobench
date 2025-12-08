"""Shared utility functions for the noquery project."""

from .config import (
    load_dotenv_if_available,
    resolve_openai_api_key,
    setup_api_keys,
)
from .data_loading import (
    extract_category,
    list_categories,
    load_changed_json,
    load_changed_json_with_ids,
    load_need_improve,
    read_json,
)
from .methods import (
    METHOD_REGISTRY,
    create_method_instance,
    get_method_class,
    list_available_methods,
)

__all__ = [
    # config
    "load_dotenv_if_available",
    "resolve_openai_api_key",
    "setup_api_keys",
    # data_loading
    "extract_category",
    "list_categories",
    "load_changed_json",
    "load_changed_json_with_ids",
    "load_need_improve",
    "read_json",
    # methods
    "METHOD_REGISTRY",
    "create_method_instance",
    "get_method_class",
    "list_available_methods",
]
