"""
Base classes and abstractions for ranking systems.

This module provides abstract base classes, data models, and exceptions
for the ranking package following SOLID principles.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import time


class RankingStrategy(Enum):
    """Enumeration of available ranking strategies."""

    LLM_DIRECT = "llm_direct"  # Direct LLM ranking
    LLM_WITH_SCORES = "llm_with_scores"  # LLM ranking with relevance scores
    RAG = "rag"  # Retrieval-augmented generation
    EMBEDDING_SIMILARITY = "embedding_similarity"  # Pure embedding-based


class RankingError(Exception):
    """Base exception for ranking-related errors."""
    pass


class RankingValidationError(RankingError):
    """Exception raised when ranking inputs are invalid."""
    pass


class RankingExecutionError(RankingError):
    """Exception raised during ranking execution."""
    pass


@dataclass
class Product:
    """
    Represents a product with its description.

    This is a lightweight data class for products used in ranking operations.
    For full product management, use domain-specific models.

    Attributes:
        id: Unique product identifier
        name: Product name
        description: Product description text
        category: Optional product category
        metadata: Optional additional product metadata

    Raises:
        ValueError: If id, name, or description are empty

    Examples:
        >>> product = Product(
        ...     id="prod_001",
        ...     name="Camera Pro X1",
        ...     description="Professional camera with 45MP sensor",
        ...     category="Electronics"
        ... )
    """

    id: str
    name: str
    description: str
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate product data after initialization."""
        if not self.id or not self.id.strip():
            raise ValueError("Product ID cannot be empty")
        if not self.name or not self.name.strip():
            raise ValueError("Product name cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("Product description cannot be empty")


@dataclass
class RankingResult:
    """
    Result of a ranking operation.

    Contains ranked products with scores and metadata about the ranking process.

    Attributes:
        query: The search query that was ranked
        rankings: List of (product_id, score) tuples in rank order
        strategy: The ranking strategy used
        raw_response: Optional raw LLM response text
        ranking_time: Time taken for ranking in seconds
        metadata: Optional additional metadata about ranking

    Examples:
        >>> result = RankingResult(
        ...     query="best camera",
        ...     rankings=[("cam_001", 0.95), ("cam_002", 0.87)],
        ...     strategy=RankingStrategy.LLM_DIRECT,
        ...     ranking_time=1.23
        ... )
    """

    query: str
    rankings: List[Tuple[str, float]]
    strategy: RankingStrategy
    raw_response: Optional[str] = None
    ranking_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate ranking result data."""
        if not self.query or not self.query.strip():
            raise ValueError("Query cannot be empty")
        if not self.rankings:
            raise ValueError("Rankings list cannot be empty")

        # Validate all scores are between 0 and 1
        for product_id, score in self.rankings:
            if not isinstance(score, (int, float)):
                raise ValueError(f"Score must be numeric, got {type(score)} for {product_id}")
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"Score must be between 0 and 1, got {score} for {product_id}")

    def get_top_k(self, k: int) -> List[Tuple[str, float]]:
        """
        Get top k ranked products.

        Args:
            k: Number of top products to return

        Returns:
            List of top k (product_id, score) tuples

        Examples:
            >>> result.get_top_k(3)
            [("prod_1", 0.95), ("prod_2", 0.87), ("prod_3", 0.76)]
        """
        return self.rankings[:k]

    def get_product_rank(self, product_id: str) -> Optional[int]:
        """
        Get rank position of a specific product.

        Args:
            product_id: Product identifier to find

        Returns:
            Rank position (1-indexed) or None if not found

        Examples:
            >>> result.get_product_rank("prod_002")
            2
        """
        for rank, (pid, _) in enumerate(self.rankings, 1):
            if pid == product_id:
                return rank
        return None

    def get_product_score(self, product_id: str) -> Optional[float]:
        """
        Get relevance score of a specific product.

        Args:
            product_id: Product identifier to find

        Returns:
            Relevance score or None if not found

        Examples:
            >>> result.get_product_score("prod_001")
            0.95
        """
        for pid, score in self.rankings:
            if pid == product_id:
                return score
        return None


class BaseRanker(ABC):
    """
    Abstract base class for all ranking strategies.

    This class defines the interface that all rankers must implement.
    Follows the Template Method pattern with concrete validation and
    abstract ranking methods.

    The ranking workflow is:
    1. Validate inputs
    2. Start timing
    3. Execute ranking (implemented by subclasses)
    4. Record timing
    5. Return result
    """

    def rank(
        self,
        query: str,
        products: List[Product],
        top_k: Optional[int] = None,
        **kwargs
    ) -> RankingResult:
        """
        Rank products by relevance to query.

        This is the main public interface for ranking. It handles validation
        and timing, delegating the actual ranking to _rank_products.

        Args:
            query: Search query string
            products: List of products to rank
            top_k: Optional limit on number of results
            **kwargs: Additional strategy-specific parameters

        Returns:
            RankingResult with ranked products and metadata

        Raises:
            RankingValidationError: If inputs are invalid
            RankingExecutionError: If ranking fails

        Examples:
            >>> ranker = LLMRanker(llm_client)
            >>> result = ranker.rank("best camera", products, top_k=5)
        """
        # Validate inputs
        self.validate_inputs(query, products)

        # Track timing
        start_time = time.time()

        try:
            # Execute ranking (implemented by subclasses)
            result = self._rank_products(query, products, top_k, **kwargs)

            # Record timing
            result.ranking_time = time.time() - start_time

            return result

        except RankingError:
            # Re-raise ranking errors
            raise
        except Exception as e:
            # Wrap other exceptions
            raise RankingExecutionError(f"Ranking failed: {str(e)}") from e

    @abstractmethod
    def _rank_products(
        self,
        query: str,
        products: List[Product],
        top_k: Optional[int],
        **kwargs
    ) -> RankingResult:
        """
        Execute the ranking strategy.

        This method must be implemented by subclasses to provide
        the actual ranking logic.

        Args:
            query: Search query string
            products: List of products to rank
            top_k: Optional limit on number of results
            **kwargs: Additional strategy-specific parameters

        Returns:
            RankingResult with ranked products
        """
        pass

    def validate_inputs(
        self,
        query: str,
        products: List[Product]
    ) -> None:
        """
        Validate ranking inputs.

        Args:
            query: Search query to validate
            products: Products list to validate

        Raises:
            RankingValidationError: If inputs are invalid

        Examples:
            >>> ranker.validate_inputs("", products)
            RankingValidationError: Query cannot be empty
        """
        if not query or not query.strip():
            raise RankingValidationError("Query cannot be empty")

        if not products:
            raise RankingValidationError("Products list cannot be empty")

        if not isinstance(products, list):
            raise RankingValidationError("Products must be a list")

        # Validate product types
        for i, product in enumerate(products):
            if not isinstance(product, Product):
                raise RankingValidationError(
                    f"Product at index {i} must be a Product instance, "
                    f"got {type(product)}"
                )

    def _create_default_rankings(
        self,
        products: List[Product]
    ) -> List[Tuple[str, float]]:
        """
        Create default rankings when ranking fails.

        Returns products in original order with exponentially decreasing scores.

        Args:
            products: List of products

        Returns:
            List of (product_id, score) tuples
        """
        return [
            (product.id, 1.0 / (i + 1))
            for i, product in enumerate(products)
        ]
