"""
LLM-based ranking implementations.

This module provides ranking strategies that use Large Language Models
to rank products based on textual relevance.
"""

from typing import List, Optional, Dict, Any, Tuple
import logging
import re

from .base import (
    BaseRanker,
    Product,
    RankingResult,
    RankingStrategy,
    RankingExecutionError,
)

logger = logging.getLogger(__name__)


# Default prompts for different ranking modes
DEFAULT_RANKING_PROMPT = """Query: {query}

Products:
{products_text}

Rank these products from 1 to {num_products} based on relevance to the query.
Return only the ranking as a numbered list with product IDs.

Example format:
1. [product_id]
2. [product_id]
etc."""


DEFAULT_SCORING_PROMPT = """Query: {query}

Products:
{products_text}

Rank these products from 1 to {num_products} based on relevance to the query.
Also provide a relevance score (0-100) for each product.

Format: 1. [Product ID] (Score: XX)

Example:
1. prod_001 (Score: 95)
2. prod_002 (Score: 82)
etc."""


class LLMRanker(BaseRanker):
    """
    LLM-based product ranking using direct prompting.

    This ranker uses an LLM to directly rank products based on their
    descriptions and the search query. It supports both simple ranking
    and ranking with relevance scores.

    Attributes:
        llm_client: LLM client instance (from src.llm package)
        system_prompt: Optional system prompt to guide ranking
        temperature: LLM temperature parameter
        max_tokens: Maximum tokens to generate

    Examples:
        >>> from src.llm import create_llm_client
        >>> llm = create_llm_client(provider="anthropic")
        >>> ranker = LLMRanker(llm, temperature=0.0)
        >>> result = ranker.rank("best camera", products)
    """

    def __init__(
        self,
        llm_client,  # From src.llm
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        Initialize LLM ranker.

        Args:
            llm_client: LLM client instance supporting generate_text()
            system_prompt: Optional system prompt for ranking
            temperature: LLM temperature (0 for deterministic)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional LLM client parameters

        Raises:
            ValueError: If llm_client doesn't have generate_text method
        """
        if not hasattr(llm_client, 'generate_text'):
            raise ValueError(
                "llm_client must have a generate_text() method. "
                "Use an LLMClient from src.llm package."
            )

        self.llm_client = llm_client
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extra_params = kwargs

        logger.info(
            f"Initialized LLMRanker with model: {getattr(llm_client, 'model', 'unknown')}"
        )

    def _rank_products(
        self,
        query: str,
        products: List[Product],
        top_k: Optional[int] = None,
        **kwargs
    ) -> RankingResult:
        """
        Execute LLM-based ranking.

        Args:
            query: Search query
            products: List of products to rank
            top_k: Optional limit (not used in this implementation)
            **kwargs: Additional parameters including 'return_scores'

        Returns:
            RankingResult with LLM-generated rankings
        """
        return_scores = kwargs.get('return_scores', False)

        # Build prompt
        prompt = self._build_ranking_prompt(query, products, return_scores)

        try:
            # Call LLM
            response = self.llm_client.generate_text(
                prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **self.extra_params
            )

            # Parse response
            rankings = self._parse_ranking_response(
                response.content,
                products,
                return_scores
            )

            # Determine strategy
            strategy = (
                RankingStrategy.LLM_WITH_SCORES if return_scores
                else RankingStrategy.LLM_DIRECT
            )

            return RankingResult(
                query=query,
                rankings=rankings,
                strategy=strategy,
                raw_response=response.content,
                metadata={
                    "model": response.model,
                    "provider": response.metadata.get("provider") if response.metadata else "unknown",
                    "temperature": self.temperature,
                    "usage": response.usage,
                    "return_scores": return_scores,
                }
            )

        except Exception as e:
            logger.error(f"LLM ranking failed: {e}")
            # Return default rankings on failure
            default_rankings = self._create_default_rankings(products)

            return RankingResult(
                query=query,
                rankings=default_rankings,
                strategy=RankingStrategy.LLM_DIRECT,
                metadata={"error": str(e), "fallback": True}
            )

    def _build_ranking_prompt(
        self,
        query: str,
        products: List[Product],
        return_scores: bool
    ) -> str:
        """
        Build the ranking prompt for the LLM.

        Args:
            query: Search query
            products: List of products
            return_scores: Whether to request relevance scores

        Returns:
            Formatted prompt string
        """
        # Format products
        products_text = "\n\n".join([
            f"Product {i+1} (ID: {p.id}):\n"
            f"Name: {p.name}\n"
            f"Description: {p.description}"
            for i, p in enumerate(products)
        ])

        # Choose prompt template
        template = DEFAULT_SCORING_PROMPT if return_scores else DEFAULT_RANKING_PROMPT

        # Fill template
        prompt = template.format(
            query=query,
            products_text=products_text,
            num_products=len(products)
        )

        return prompt

    def _parse_ranking_response(
        self,
        response: str,
        products: List[Product],
        has_scores: bool
    ) -> List[Tuple[str, float]]:
        """
        Parse LLM response to extract rankings.

        Handles various response formats and errors gracefully.

        Args:
            response: Raw LLM response text
            products: Original product list
            has_scores: Whether response contains scores

        Returns:
            List of (product_id, score) tuples in rank order
        """
        lines = response.strip().split("\n")
        rankings = []
        product_ids = {p.id for p in products}
        seen_ids = set()

        for i, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                continue

            # Try to find product ID in this line
            found_id = None
            for pid in product_ids:
                if pid in line and pid not in seen_ids:
                    found_id = pid
                    break

            if found_id:
                # Calculate score
                if has_scores:
                    # Try to extract score from line
                    score = self._extract_score_from_line(line)
                else:
                    # Use reciprocal rank as score
                    score = 1.0 / (len(rankings) + 1)

                rankings.append((found_id, score))
                seen_ids.add(found_id)

        # Add any missing products with zero score
        for p in products:
            if p.id not in seen_ids:
                rankings.append((p.id, 0.0))

        return rankings

    def _extract_score_from_line(self, line: str) -> float:
        """
        Extract relevance score from a ranking line.

        Args:
            line: Line containing score information

        Returns:
            Normalized score (0.0-1.0)
        """
        # Look for "Score: XX" pattern
        score_match = re.search(r'Score:\s*(\d+)', line, re.IGNORECASE)

        if score_match:
            try:
                raw_score = float(score_match.group(1))
                # Normalize to 0-1 range (assuming input is 0-100)
                return min(raw_score / 100.0, 1.0)
            except ValueError:
                pass

        # Default to reciprocal rank if score not found
        return 1.0 / (len(line.split()) + 1)

    def _default_system_prompt(self) -> str:
        """
        Get default system prompt for ranking.

        Returns:
            System prompt string
        """
        return (
            "You are a helpful assistant that ranks products by relevance to search queries. "
            "Always return rankings in the exact format requested."
        )
