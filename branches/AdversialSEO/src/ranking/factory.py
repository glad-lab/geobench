"""
Factory for creating ranking system instances.

This module provides a centralized factory for creating rankers
with appropriate configuration.
"""

from typing import Optional, Dict, Any
from enum import Enum
import logging

from .base import BaseRanker, RankingStrategy
from .llm_ranker import LLMRanker
from .rag_ranker import RAGRanker

logger = logging.getLogger(__name__)


class RankerFactory:
    """
    Factory for creating ranking system instances.

    Provides a centralized way to create rankers with consistent
    configuration. Follows the Factory pattern for object creation.

    Examples:
        >>> from src.llm import create_llm_client
        >>> llm = create_llm_client(provider="anthropic")
        >>> factory = RankerFactory(llm_client=llm)
        >>> ranker = factory.create_ranker("llm")
    """

    def __init__(
        self,
        llm_client=None,
        embeddings=None,
        **default_params
    ):
        """
        Initialize ranker factory.

        Args:
            llm_client: Default LLM client for rankers
            embeddings: Default embedding model for RAG
            **default_params: Default parameters for all rankers
        """
        self.llm_client = llm_client
        self.embeddings = embeddings
        self.default_params = default_params

        logger.info("Initialized RankerFactory")

    def create_ranker(
        self,
        ranker_type: str,
        **kwargs
    ) -> BaseRanker:
        """
        Create a ranker instance.

        Args:
            ranker_type: Type of ranker ("llm", "rag")
            **kwargs: Ranker-specific parameters

        Returns:
            Configured ranker instance

        Raises:
            ValueError: If ranker_type is unknown or required params missing

        Examples:
            >>> ranker = factory.create_ranker("llm", temperature=0.0)
            >>> ranker = factory.create_ranker("rag", top_k=10)
        """
        ranker_type = ranker_type.lower()

        # Merge default and specific parameters
        params = {**self.default_params, **kwargs}

        if ranker_type in ("llm", "llm_direct"):
            return self._create_llm_ranker(params)

        elif ranker_type == "rag":
            return self._create_rag_ranker(params)

        else:
            raise ValueError(
                f"Unknown ranker type: {ranker_type}. "
                f"Valid types are: 'llm', 'rag'"
            )

    def _create_llm_ranker(self, params: Dict[str, Any]) -> LLMRanker:
        """
        Create LLM ranker instance.

        Args:
            params: Ranker parameters

        Returns:
            Configured LLMRanker

        Raises:
            ValueError: If llm_client not provided
        """
        llm_client = params.pop('llm_client', self.llm_client)

        if llm_client is None:
            raise ValueError(
                "llm_client is required for LLM ranker. "
                "Provide it to factory or create_ranker()."
            )

        return LLMRanker(llm_client, **params)

    def _create_rag_ranker(self, params: Dict[str, Any]) -> RAGRanker:
        """
        Create RAG ranker instance.

        Args:
            params: Ranker parameters

        Returns:
            Configured RAGRanker

        Raises:
            ValueError: If required components not provided
        """
        embeddings = params.pop('embeddings', self.embeddings)
        llm_client = params.pop('llm_client', self.llm_client)

        if embeddings is None:
            raise ValueError(
                "embeddings is required for RAG ranker. "
                "Provide it to factory or create_ranker()."
            )

        if llm_client is None:
            raise ValueError(
                "llm_client is required for RAG ranker. "
                "Provide it to factory or create_ranker()."
            )

        return RAGRanker(embeddings, llm_client, **params)

    def create_from_strategy(
        self,
        strategy: RankingStrategy,
        **kwargs
    ) -> BaseRanker:
        """
        Create ranker from RankingStrategy enum.

        Args:
            strategy: RankingStrategy enum value
            **kwargs: Ranker parameters

        Returns:
            Configured ranker instance

        Examples:
            >>> ranker = factory.create_from_strategy(
            ...     RankingStrategy.LLM_DIRECT
            ... )
        """
        strategy_map = {
            RankingStrategy.LLM_DIRECT: "llm",
            RankingStrategy.LLM_WITH_SCORES: "llm",
            RankingStrategy.RAG: "rag",
        }

        ranker_type = strategy_map.get(strategy)

        if ranker_type is None:
            raise ValueError(f"No ranker mapping for strategy: {strategy}")

        return self.create_ranker(ranker_type, **kwargs)


def create_ranker(
    ranker_type: str = "llm",
    llm_client=None,
    embeddings=None,
    **kwargs
) -> BaseRanker:
    """
    Convenience function to create a ranker.

    Args:
        ranker_type: Type of ranker ("llm", "rag")
        llm_client: LLM client instance
        embeddings: Embedding model (for RAG)
        **kwargs: Additional ranker parameters

    Returns:
        Configured ranker instance

    Examples:
        >>> from src.llm import create_llm_client
        >>> llm = create_llm_client()
        >>> ranker = create_ranker("llm", llm_client=llm)
    """
    factory = RankerFactory(llm_client=llm_client, embeddings=embeddings)
    return factory.create_ranker(ranker_type, **kwargs)
