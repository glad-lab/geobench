"""
Factory pattern for analyzer creation.

This module provides a factory for creating analyzer instances
with centralized configuration and registry.
"""

from typing import Dict, Type, Optional, Any
import logging

from .base import BaseAnalyzer
from .statistical import StatisticalAnalyzer
from .comparative import ComparativeAnalyzer
from .effectiveness import EffectivenessAnalyzer

logger = logging.getLogger(__name__)


class AnalyzerFactory:
    """
    Factory for creating analyzer instances (Factory pattern).

    Centralizes analyzer instantiation logic and provides extensibility
    for new analyzer types through registration.

    The factory maintains a registry mapping analyzer type names to
    their implementation classes.

    Example:
        >>> factory = AnalyzerFactory()
        >>> analyzer = factory.create("statistical", confidence_level=0.95)
        >>> # Or create from config
        >>> analyzers = factory.create_from_config({
        ...     "statistical": {"confidence_level": 0.95},
        ...     "comparative": {}
        ... })
    """

    _registry: Dict[str, Type[BaseAnalyzer]] = {
        "statistical": StatisticalAnalyzer,
        "comparative": ComparativeAnalyzer,
        "effectiveness": EffectivenessAnalyzer,
    }

    @classmethod
    def create(
        cls,
        analyzer_type: str,
        **kwargs: Any
    ) -> BaseAnalyzer:
        """
        Create analyzer instance based on type.

        Args:
            analyzer_type: Type of analyzer to create
                          ("statistical", "comparative", "effectiveness")
            **kwargs: Arguments to pass to analyzer constructor

        Returns:
            Configured analyzer instance

        Raises:
            ValueError: If analyzer type not registered

        Example:
            >>> analyzer = AnalyzerFactory.create("statistical", confidence_level=0.95)
            >>> analyzer = AnalyzerFactory.create("comparative")
            >>> analyzer = AnalyzerFactory.create("effectiveness")
        """
        analyzer_class = cls._registry.get(analyzer_type.lower())

        if not analyzer_class:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Unknown analyzer type: {analyzer_type}. "
                f"Available types: {available}"
            )

        logger.debug(f"Creating analyzer: {analyzer_type} with kwargs: {kwargs}")
        return analyzer_class(**kwargs)

    @classmethod
    def create_all(cls, **common_kwargs: Any) -> list[BaseAnalyzer]:
        """
        Create instances of all registered analyzers.

        Args:
            **common_kwargs: Common arguments to pass to all analyzers

        Returns:
            List of all analyzer instances

        Example:
            >>> analyzers = AnalyzerFactory.create_all(confidence_level=0.95)
            >>> # Creates StatisticalAnalyzer, ComparativeAnalyzer, EffectivenessAnalyzer
        """
        analyzers = []
        for analyzer_type in cls._registry.keys():
            try:
                analyzer = cls.create(analyzer_type, **common_kwargs)
                analyzers.append(analyzer)
            except TypeError as e:
                # Some kwargs might not apply to all analyzers
                logger.warning(
                    f"Failed to create {analyzer_type} with common kwargs: {e}. "
                    f"Creating with defaults."
                )
                analyzer = cls.create(analyzer_type)
                analyzers.append(analyzer)

        return analyzers

    @classmethod
    def create_from_config(
        cls,
        config: Dict[str, Dict[str, Any]]
    ) -> list[BaseAnalyzer]:
        """
        Create analyzers from configuration dictionary.

        Args:
            config: Dictionary mapping analyzer types to their kwargs
                   Example: {
                       "statistical": {"confidence_level": 0.95},
                       "comparative": {},
                       "effectiveness": {"name": "MyEffectivenessAnalyzer"}
                   }

        Returns:
            List of configured analyzer instances

        Example:
            >>> config = {
            ...     "statistical": {"confidence_level": 0.99},
            ...     "comparative": {},
            ... }
            >>> analyzers = AnalyzerFactory.create_from_config(config)
        """
        analyzers = []

        for analyzer_type, kwargs in config.items():
            try:
                analyzer = cls.create(analyzer_type, **kwargs)
                analyzers.append(analyzer)
                logger.debug(f"Created {analyzer_type} from config")
            except Exception as e:
                logger.error(
                    f"Failed to create analyzer {analyzer_type} from config: {e}"
                )
                # Continue creating other analyzers
                continue

        return analyzers

    @classmethod
    def register(
        cls,
        analyzer_type: str,
        analyzer_class: Type[BaseAnalyzer]
    ) -> None:
        """
        Register new analyzer type (Open/Closed principle).

        Allows extension without modifying factory code.

        Args:
            analyzer_type: Name for the analyzer type
            analyzer_class: Analyzer class to register

        Raises:
            TypeError: If analyzer_class is not a BaseAnalyzer subclass

        Example:
            >>> class CustomAnalyzer(BaseAnalyzer):
            ...     def analyze(self, data):
            ...         return AnalysisResult(...)
            >>>
            >>> AnalyzerFactory.register("custom", CustomAnalyzer)
            >>> analyzer = AnalyzerFactory.create("custom")
        """
        if not issubclass(analyzer_class, BaseAnalyzer):
            raise TypeError(
                f"Analyzer class must be a subclass of BaseAnalyzer, "
                f"got {analyzer_class}"
            )

        cls._registry[analyzer_type.lower()] = analyzer_class
        logger.info(f"Registered analyzer type: {analyzer_type}")

    @classmethod
    def list_types(cls) -> list[str]:
        """
        List all registered analyzer types.

        Returns:
            List of analyzer type names

        Example:
            >>> types = AnalyzerFactory.list_types()
            >>> print(types)  # ['statistical', 'comparative', 'effectiveness']
        """
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, analyzer_type: str) -> bool:
        """
        Check if analyzer type is registered.

        Args:
            analyzer_type: Type to check

        Returns:
            True if registered, False otherwise

        Example:
            >>> if AnalyzerFactory.is_registered("statistical"):
            ...     analyzer = AnalyzerFactory.create("statistical")
        """
        return analyzer_type.lower() in cls._registry
