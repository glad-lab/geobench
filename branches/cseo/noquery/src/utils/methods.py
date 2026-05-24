"""
Method registry for C-SEO improvement methods.

Provides centralized mapping from method names to implementation classes.
"""

from typing import Dict, Type

from noquery.src.methods.citation_boosting import CitationBoosting
from noquery.src.methods.content_improvement import ContentImprovement
from noquery.src.methods.geo_methods import (
    Authoritative,
    Citations,
    Fluency,
    Quotes,
    SimpleLanguage,
    Statistics,
    TechnicalTerms,
    UniqueWords,
)
from noquery.src.methods.llmstxt import LLMstxt


# Central registry of all available methods
METHOD_REGISTRY: Dict[str, Type[CitationBoosting]] = {
    "Authoritative": Authoritative,
    "Statistics": Statistics,
    "Citations": Citations,
    "Fluency": Fluency,
    "UniqueWords": UniqueWords,
    "TechnicalTerms": TechnicalTerms,
    "SimpleLanguage": SimpleLanguage,
    "Quotes": Quotes,
    "ContentImprovement": ContentImprovement,
    "LLMstxt": LLMstxt,
}


def get_method_class(method_name: str) -> Type[CitationBoosting]:
    """
    Get the implementation class for a given method name.

    Args:
        method_name: Name of the method (e.g., "Authoritative", "Statistics")

    Returns:
        The method class

    Raises:
        ValueError: If method_name is not recognized
    """
    if method_name not in METHOD_REGISTRY:
        available = ", ".join(sorted(METHOD_REGISTRY.keys()))
        raise ValueError(
            f"Unknown method: {method_name}. Available methods: {available}"
        )
    return METHOD_REGISTRY[method_name]


def list_available_methods() -> list[str]:
    """
    Get a list of all available method names.

    Returns:
        Sorted list of method names
    """
    return sorted(METHOD_REGISTRY.keys())


def create_method_instance(
    method_name: str,
    llm_helper,
    **kwargs
) -> CitationBoosting:
    """
    Create an instance of a method with the given LLM helper.

    Args:
        method_name: Name of the method
        llm_helper: LLM helper instance (e.g., OpenAIHelper)
        **kwargs: Additional arguments to pass to the method constructor

    Returns:
        Instance of the method

    Raises:
        ValueError: If method_name is not recognized
    """
    method_class = get_method_class(method_name)
    return method_class(llm=llm_helper, **kwargs)
