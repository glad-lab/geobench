"""
Ranking quality metrics and evaluation tools.

This module provides metrics for evaluating ranking quality including
NDCG, MRR, MAP, and precision@k.
"""

from typing import List, Set, Dict
import math
import logging

logger = logging.getLogger(__name__)


class RankingMetrics:
    """
    Calculate ranking quality metrics.

    Provides standard information retrieval metrics for evaluating
    ranking quality against ground truth relevance judgments.

    All methods are static for stateless metric calculation.

    Examples:
        >>> predicted = ["doc1", "doc2", "doc3"]
        >>> relevant = ["doc2", "doc3"]
        >>> RankingMetrics.precision_at_k(predicted, relevant, k=2)
        0.5
    """

    @staticmethod
    def precision_at_k(
        predicted_ranking: List[str],
        relevant_items: Set[str],
        k: int = 10
    ) -> float:
        """
        Calculate Precision@K metric.

        Measures what fraction of top-k results are relevant.

        Args:
            predicted_ranking: Predicted ranking as list of IDs
            relevant_items: Set of relevant item IDs
            k: Number of top results to consider

        Returns:
            Precision@K score (0.0-1.0)

        Examples:
            >>> RankingMetrics.precision_at_k(
            ...     ["a", "b", "c", "d"],
            ...     {"b", "d"},
            ...     k=3
            ... )
            0.6666666666666666
        """
        if k <= 0:
            raise ValueError("k must be positive")

        top_k = predicted_ranking[:k]
        relevant_in_top_k = sum(1 for item in top_k if item in relevant_items)

        return relevant_in_top_k / k if k > 0 else 0.0

    @staticmethod
    def recall_at_k(
        predicted_ranking: List[str],
        relevant_items: Set[str],
        k: int = 10
    ) -> float:
        """
        Calculate Recall@K metric.

        Measures what fraction of relevant items appear in top-k.

        Args:
            predicted_ranking: Predicted ranking as list of IDs
            relevant_items: Set of relevant item IDs
            k: Number of top results to consider

        Returns:
            Recall@K score (0.0-1.0)

        Examples:
            >>> RankingMetrics.recall_at_k(
            ...     ["a", "b", "c"],
            ...     {"b", "c", "d"},
            ...     k=2
            ... )
            0.3333333333333333
        """
        if not relevant_items:
            return 0.0

        if k <= 0:
            raise ValueError("k must be positive")

        top_k = predicted_ranking[:k]
        relevant_in_top_k = sum(1 for item in top_k if item in relevant_items)

        return relevant_in_top_k / len(relevant_items)

    @staticmethod
    def mean_reciprocal_rank(
        rankings: List[List[str]],
        relevant_items: List[str]
    ) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR).

        Measures how high the first relevant item appears on average.

        Args:
            rankings: List of rankings (each a list of item IDs)
            relevant_items: List of relevant item IDs for each query

        Returns:
            MRR score (0.0-1.0)

        Raises:
            ValueError: If rankings and relevant_items lengths don't match

        Examples:
            >>> rankings = [["a", "b", "c"], ["x", "y", "z"]]
            >>> relevant = ["b", "x"]
            >>> RankingMetrics.mean_reciprocal_rank(rankings, relevant)
            1.0
        """
        if len(rankings) != len(relevant_items):
            raise ValueError("rankings and relevant_items must have same length")

        if not rankings:
            return 0.0

        reciprocal_ranks = []

        for ranking, relevant_item in zip(rankings, relevant_items):
            # Find position of relevant item (1-indexed)
            for pos, item in enumerate(ranking, 1):
                if item == relevant_item:
                    reciprocal_ranks.append(1.0 / pos)
                    break
            else:
                # Relevant item not found
                reciprocal_ranks.append(0.0)

        return sum(reciprocal_ranks) / len(reciprocal_ranks)

    @staticmethod
    def ndcg(
        predicted_ranking: List[str],
        ideal_ranking: List[str],
        k: int = 10
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain (NDCG@K).

        Measures ranking quality considering both relevance and position.
        Returns 1.0 for perfect ranking, 0.0 for worst.

        Args:
            predicted_ranking: Predicted ranking as list of IDs
            ideal_ranking: Ideal ranking as list of IDs
            k: Number of top results to consider

        Returns:
            NDCG@K score (0.0-1.0)

        Examples:
            >>> predicted = ["a", "b", "c", "d"]
            >>> ideal = ["b", "a", "c", "d"]
            >>> RankingMetrics.ndcg(predicted, ideal, k=4)
            0.9831...
        """
        if k <= 0:
            raise ValueError("k must be positive")

        # Calculate DCG for predicted ranking
        dcg = RankingMetrics._dcg(predicted_ranking, ideal_ranking, k)

        # Calculate ideal DCG (perfect ordering)
        idcg = RankingMetrics._dcg(ideal_ranking, ideal_ranking, k)

        # Normalize
        if idcg == 0:
            return 0.0

        return dcg / idcg

    @staticmethod
    def _dcg(
        ranking: List[str],
        ideal_ranking: List[str],
        k: int
    ) -> float:
        """
        Calculate Discounted Cumulative Gain (DCG).

        Args:
            ranking: Ranking to evaluate
            ideal_ranking: Ideal ranking for relevance scoring
            k: Number of top results to consider

        Returns:
            DCG score
        """
        # Create relevance map (position in ideal ranking = relevance)
        relevance_map = {
            item: len(ideal_ranking) - pos
            for pos, item in enumerate(ideal_ranking)
        }

        dcg_score = 0.0
        for pos, item in enumerate(ranking[:k], 1):
            relevance = relevance_map.get(item, 0)
            # Standard DCG formula: rel / log2(pos + 1)
            dcg_score += relevance / math.log2(pos + 1)

        return dcg_score

    @staticmethod
    def average_precision(
        predicted_ranking: List[str],
        relevant_items: Set[str]
    ) -> float:
        """
        Calculate Average Precision (AP).

        Measures precision at each relevant position.

        Args:
            predicted_ranking: Predicted ranking as list of IDs
            relevant_items: Set of relevant item IDs

        Returns:
            AP score (0.0-1.0)

        Examples:
            >>> RankingMetrics.average_precision(
            ...     ["a", "b", "c", "d"],
            ...     {"b", "d"}
            ... )
            0.6666666666666666
        """
        if not relevant_items:
            return 0.0

        num_relevant = 0
        precision_sum = 0.0

        for pos, item in enumerate(predicted_ranking, 1):
            if item in relevant_items:
                num_relevant += 1
                precision_at_pos = num_relevant / pos
                precision_sum += precision_at_pos

        return precision_sum / len(relevant_items) if relevant_items else 0.0

    @staticmethod
    def mean_average_precision(
        rankings: List[List[str]],
        relevant_sets: List[Set[str]]
    ) -> float:
        """
        Calculate Mean Average Precision (MAP).

        Average of AP scores across multiple queries.

        Args:
            rankings: List of rankings
            relevant_sets: List of relevant item sets for each query

        Returns:
            MAP score (0.0-1.0)

        Raises:
            ValueError: If lengths don't match

        Examples:
            >>> rankings = [["a", "b", "c"], ["x", "y", "z"]]
            >>> relevant = [{"b", "c"}, {"x"}]
            >>> RankingMetrics.mean_average_precision(rankings, relevant)
            0.8333333333333333
        """
        if len(rankings) != len(relevant_sets):
            raise ValueError("rankings and relevant_sets must have same length")

        if not rankings:
            return 0.0

        ap_scores = [
            RankingMetrics.average_precision(ranking, relevant)
            for ranking, relevant in zip(rankings, relevant_sets)
        ]

        return sum(ap_scores) / len(ap_scores)

    @staticmethod
    def evaluate_ranking(
        predicted_ranking: List[str],
        ideal_ranking: List[str],
        relevant_items: Set[str],
        k_values: List[int] = [1, 3, 5, 10]
    ) -> Dict[str, float]:
        """
        Comprehensive ranking evaluation.

        Calculates multiple metrics for a single ranking.

        Args:
            predicted_ranking: Predicted ranking
            ideal_ranking: Ideal ranking
            relevant_items: Set of relevant items
            k_values: List of k values for P@K and R@K

        Returns:
            Dictionary of metric names to scores

        Examples:
            >>> metrics = RankingMetrics.evaluate_ranking(
            ...     ["a", "b", "c"],
            ...     ["b", "a", "c"],
            ...     {"a", "b"},
            ...     k_values=[1, 3]
            ... )
            >>> metrics["ndcg@10"]
            0.98...
        """
        results = {}

        # NDCG at various k values
        for k in k_values:
            results[f"ndcg@{k}"] = RankingMetrics.ndcg(
                predicted_ranking, ideal_ranking, k
            )

        # Precision and Recall at k
        for k in k_values:
            results[f"precision@{k}"] = RankingMetrics.precision_at_k(
                predicted_ranking, relevant_items, k
            )
            results[f"recall@{k}"] = RankingMetrics.recall_at_k(
                predicted_ranking, relevant_items, k
            )

        # Average Precision
        results["average_precision"] = RankingMetrics.average_precision(
            predicted_ranking, relevant_items
        )

        return results

    @staticmethod
    def top_k_success_rate(positions: List[int], k: int = 3) -> float:
        """
        Calculate Top-K success rate (binary metric).

        Measures what fraction of products reached top-K positions.
        This is a binary threshold metric - did the product reach the threshold or not?

        Args:
            positions: List of final positions (1-indexed)
            k: Position threshold (default: 3 for top-3)

        Returns:
            Success rate (0.0-1.0)

        Examples:
            >>> # 2 out of 3 products reached top-3
            >>> RankingMetrics.top_k_success_rate([1, 2, 5], k=3)
            0.6666666666666666

            >>> # All products reached top-5
            >>> RankingMetrics.top_k_success_rate([1, 3, 5], k=5)
            1.0
        """
        if not positions:
            return 0.0
        if k <= 0:
            raise ValueError("k must be positive")

        successes = sum(1 for p in positions if p <= k)
        return successes / len(positions)

    @staticmethod
    def absolute_position_improvement(
        baseline_positions: List[int],
        final_positions: List[int]
    ) -> List[int]:
        """
        Calculate absolute position improvement (magnitude metric).

        Measures how many positions each product improved.
        Positive values indicate improvement (moved up in ranking).

        Args:
            baseline_positions: Original positions before attack (1-indexed)
            final_positions: Final positions after attack (1-indexed)

        Returns:
            List of position changes (positive = improvement)

        Examples:
            >>> # Product improved from position 10 to 3 (+7 positions)
            >>> RankingMetrics.absolute_position_improvement([10], [3])
            [7]

            >>> # Mixed results
            >>> RankingMetrics.absolute_position_improvement([5, 10, 3], [2, 8, 5])
            [3, 2, -2]
        """
        if len(baseline_positions) != len(final_positions):
            raise ValueError("baseline and final positions must have same length")

        return [baseline - final for baseline, final in zip(baseline_positions, final_positions)]

    @staticmethod
    def percentage_improvement(
        baseline_positions: List[int],
        final_positions: List[int],
        total_items: int
    ) -> List[float]:
        """
        Calculate percentage improvement (magnitude metric).

        Measures improvement as a percentage of the total ranking space.
        Example: Moving from position 10 to 3 in a 10-item list = 70% improvement.

        Args:
            baseline_positions: Original positions before attack (1-indexed)
            final_positions: Final positions after attack (1-indexed)
            total_items: Total number of items in ranking

        Returns:
            List of percentage improvements (0-100 range)

        Examples:
            >>> # 10→3 in 10 items = 7/10 = 70% improvement
            >>> RankingMetrics.percentage_improvement([10], [3], 10)
            [70.0]

            >>> # Mixed results in 20-item ranking
            >>> RankingMetrics.percentage_improvement([15, 10], [5, 15], 20)
            [50.0, -25.0]
        """
        if len(baseline_positions) != len(final_positions):
            raise ValueError("baseline and final positions must have same length")
        if total_items <= 0:
            raise ValueError("total_items must be positive")

        percentages = []
        for baseline, final in zip(baseline_positions, final_positions):
            improvement = baseline - final
            percentage = (improvement / total_items) * 100
            percentages.append(percentage)

        return percentages

    @staticmethod
    def mean_final_position(positions: List[int]) -> float:
        """
        Calculate mean final position (magnitude metric).

        Measures the average final ranking position.
        Lower values indicate better overall performance.

        Args:
            positions: List of final positions (1-indexed)

        Returns:
            Mean position

        Examples:
            >>> RankingMetrics.mean_final_position([1, 2, 3])
            2.0

            >>> RankingMetrics.mean_final_position([1, 5, 10])
            5.333333333333333
        """
        if not positions:
            return 0.0

        return sum(positions) / len(positions)
