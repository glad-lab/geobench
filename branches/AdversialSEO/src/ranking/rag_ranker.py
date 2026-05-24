"""
RAG (Retrieval-Augmented Generation) ranking implementation.

This module provides ranking that combines embedding-based retrieval
with LLM-based reranking for improved accuracy.
"""

from typing import List, Optional, Dict, Any
import logging
import numpy as np

from .base import (
    BaseRanker,
    Product,
    RankingResult,
    RankingStrategy,
    RankingValidationError,
)
from .llm_ranker import LLMRanker

logger = logging.getLogger(__name__)


class RAGRanker(BaseRanker):
    """
    RAG-based ranking combining retrieval and LLM reranking.

    This ranker first uses embedding similarity to retrieve top-k candidates,
    then uses an LLM to rerank them for final ordering. This two-stage
    approach is more efficient and often more accurate than LLM-only ranking.

    Attributes:
        embeddings: Embedding model (OpenAI or similar)
        llm_client: LLM client for reranking
        top_k: Number of candidates to retrieve before reranking
        llm_ranker: Internal LLM ranker instance

    Examples:
        >>> from langchain_openai import OpenAIEmbeddings
        >>> from src.llm import create_llm_client
        >>> embeddings = OpenAIEmbeddings()
        >>> llm = create_llm_client(provider="anthropic")
        >>> ranker = RAGRanker(embeddings, llm, top_k=10)
        >>> result = ranker.rank("best camera", products)
    """

    def __init__(
        self,
        embeddings,  # OpenAIEmbeddings or similar
        llm_client,  # From src.llm
        top_k: int = 10,
        use_retrieval: bool = True,
        **kwargs
    ):
        """
        Initialize RAG ranker.

        Args:
            embeddings: Embedding model with embed_query and embed_documents methods
            llm_client: LLM client for reranking
            top_k: Number of candidates to retrieve
            use_retrieval: Whether to use retrieval step (can disable for testing)
            **kwargs: Additional parameters passed to LLM ranker

        Raises:
            ValueError: If embeddings or llm_client are invalid
        """
        # Validate embeddings
        if not hasattr(embeddings, 'embed_query') or not hasattr(embeddings, 'embed_documents'):
            raise ValueError(
                "embeddings must have embed_query() and embed_documents() methods. "
                "Use OpenAIEmbeddings or similar."
            )

        # Validate LLM client
        if not hasattr(llm_client, 'generate_text'):
            raise ValueError(
                "llm_client must have a generate_text() method. "
                "Use an LLMClient from src.llm package."
            )

        self.embeddings = embeddings
        self.llm_client = llm_client
        self.top_k = top_k
        self.use_retrieval = use_retrieval

        # Create internal LLM ranker for reranking
        self.llm_ranker = LLMRanker(llm_client, **kwargs)

        logger.info(
            f"Initialized RAGRanker with top_k={top_k}, "
            f"model={getattr(llm_client, 'model', 'unknown')}"
        )

    def _rank_products(
        self,
        query: str,
        products: List[Product],
        top_k: Optional[int] = None,
        **kwargs
    ) -> RankingResult:
        """
        Execute RAG-based ranking.

        First retrieves top-k candidates using embeddings, then reranks
        with LLM for final ordering.

        Args:
            query: Search query
            products: List of products to rank
            top_k: Optional override for retrieval limit
            **kwargs: Additional parameters

        Returns:
            RankingResult with RAG-generated rankings
        """
        use_retrieval = kwargs.get('use_retrieval', self.use_retrieval)
        retrieval_k = top_k or self.top_k

        # Step 1: Retrieval (if enabled and products > top_k)
        if use_retrieval and len(products) > retrieval_k:
            logger.debug(f"Retrieving top {retrieval_k} candidates from {len(products)} products")
            retrieved_products = self._retrieve_top_k(query, products, retrieval_k)
        else:
            logger.debug("Skipping retrieval, using all products")
            retrieved_products = products

        # Step 2: LLM reranking
        logger.debug(f"Reranking {len(retrieved_products)} products with LLM")
        llm_result = self.llm_ranker.rank(query, retrieved_products, **kwargs)

        # Update strategy and metadata
        llm_result.strategy = RankingStrategy.RAG
        llm_result.metadata.update({
            "retrieval_used": use_retrieval,
            "top_k": retrieval_k,
            "num_retrieved": len(retrieved_products),
            "total_products": len(products),
        })

        return llm_result

    def _retrieve_top_k(
        self,
        query: str,
        products: List[Product],
        k: int
    ) -> List[Product]:
        """
        Retrieve top-k products using embedding similarity.

        Args:
            query: Search query
            products: All available products
            k: Number of products to retrieve

        Returns:
            List of top-k most similar products

        Raises:
            RankingValidationError: If embedding fails
        """
        try:
            # Get query embedding
            query_embedding = self.embeddings.embed_query(query)

            # Get product embeddings
            product_texts = [
                f"{p.name}: {p.description}"
                for p in products
            ]
            product_embeddings = self.embeddings.embed_documents(product_texts)

            # Calculate similarities
            similarities = []
            for i, prod_emb in enumerate(product_embeddings):
                similarity = self._cosine_similarity(query_embedding, prod_emb)
                similarities.append((products[i], similarity))

            # Sort by similarity (descending) and return top-k
            similarities.sort(key=lambda x: x[1], reverse=True)
            retrieved = [item[0] for item in similarities[:k]]

            logger.debug(
                f"Retrieved {len(retrieved)} products with similarities: "
                f"{[f'{s[1]:.3f}' for s in similarities[:k]]}"
            )

            return retrieved

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            raise RankingValidationError(f"Embedding-based retrieval failed: {e}") from e

    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0-1)
        """
        # Convert to numpy arrays for efficient computation
        a = np.array(vec1)
        b = np.array(vec2)

        # Compute dot product and norms
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        # Avoid division by zero
        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))
