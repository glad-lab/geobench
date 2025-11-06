"""Reusable metric calculation functions."""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from collections import Counter


class MetricCalculator:
    """Static utility class for calculating evaluation metrics.

    All methods are static and can be used independently.
    Provides metrics for attack success, ranking quality, and comparative analysis.
    """

    @staticmethod
    def success_rate(
        results: List[Dict[str, Any]],
        target_field: str = "attacked_product",
        top_k: int = 5
    ) -> float:
        """Calculate attack success rate (target appears in top-K).

        Args:
            results: List of ranking results
            target_field: Field containing attacked product ID
            top_k: Number of top positions to consider

        Returns:
            Success rate as float between 0 and 1
        """
        if not results:
            return 0.0

        successes = 0
        for r in results:
            target_id = r.get(target_field)
            if not target_id:
                continue

            # Check in top_k_ids if available
            top_k_ids = r.get("top_k_ids", [])
            if top_k_ids and target_id in top_k_ids[:top_k]:
                successes += 1
                continue

            # Otherwise check ranked_products
            ranked = r.get("ranked_products", [])
            if ranked:
                top_ids = [p.get("id") for p in ranked[:top_k]]
                if target_id in top_ids:
                    successes += 1

        return successes / len(results)

    @staticmethod
    def position_1_rate(
        results: List[Dict[str, Any]],
        target_field: str = "attacked_product"
    ) -> float:
        """Calculate rate of target appearing at position 1.

        Args:
            results: List of ranking results
            target_field: Field containing attacked product ID

        Returns:
            Position-1 rate as float between 0 and 1
        """
        if not results:
            return 0.0

        position_1 = 0
        for r in results:
            target_id = r.get(target_field)
            if not target_id:
                continue

            ranked = r.get("ranked_products", [])
            if ranked and ranked[0].get("id") == target_id:
                position_1 += 1

        return position_1 / len(results)

    @staticmethod
    def mean_rank(
        results: List[Dict[str, Any]],
        target_field: str = "attacked_product"
    ) -> float:
        """Calculate mean rank of attacked product.

        Args:
            results: List of ranking results
            target_field: Field containing attacked product ID

        Returns:
            Mean rank (lower is better, 1-indexed)
        """
        if not results:
            return float('inf')

        ranks = []
        for r in results:
            ranked_ids = [p.get("id") for p in r.get("ranked_products", [])]
            target_id = r.get(target_field)

            if not target_id or not ranked_ids:
                continue

            if target_id in ranked_ids:
                ranks.append(ranked_ids.index(target_id) + 1)  # 1-indexed
            else:
                ranks.append(len(ranked_ids) + 1)  # Worst rank

        return float(np.mean(ranks)) if ranks else float('inf')

    @staticmethod
    def median_rank(
        results: List[Dict[str, Any]],
        target_field: str = "attacked_product"
    ) -> float:
        """Calculate median rank of attacked product.

        Args:
            results: List of ranking results
            target_field: Field containing attacked product ID

        Returns:
            Median rank (lower is better, 1-indexed)
        """
        if not results:
            return float('inf')

        ranks = []
        for r in results:
            ranked_ids = [p.get("id") for p in r.get("ranked_products", [])]
            target_id = r.get(target_field)

            if not target_id or not ranked_ids:
                continue

            if target_id in ranked_ids:
                ranks.append(ranked_ids.index(target_id) + 1)
            else:
                ranks.append(len(ranked_ids) + 1)

        return float(np.median(ranks)) if ranks else float('inf')

    @staticmethod
    def rank_improvement(
        baseline_results: List[Dict[str, Any]],
        attack_results: List[Dict[str, Any]],
        target_field: str = "attacked_product"
    ) -> float:
        """Calculate rank improvement from baseline to attack.

        Args:
            baseline_results: Baseline ranking results
            attack_results: Attack ranking results
            target_field: Field containing attacked product ID

        Returns:
            Mean rank improvement (positive = attack improved ranking)
        """
        baseline_rank = MetricCalculator.mean_rank(baseline_results, target_field)
        attack_rank = MetricCalculator.mean_rank(attack_results, target_field)

        if baseline_rank == float('inf') or attack_rank == float('inf'):
            return 0.0

        return baseline_rank - attack_rank  # Positive = improvement

    @staticmethod
    def attack_type_effectiveness(
        results: List[Dict[str, Any]],
        target_field: str = "attacked_product"
    ) -> Dict[str, float]:
        """Calculate success rate by attack type.

        Args:
            results: List of results with 'attack_type' field
            target_field: Field containing attacked product ID

        Returns:
            Dictionary mapping attack type to success rate
        """
        by_type: Dict[str, float] = {}
        attack_types = set(r.get("attack_type") for r in results if r.get("attack_type"))

        for attack_type in attack_types:
            type_results = [r for r in results if r.get("attack_type") == attack_type]
            if type_results:
                by_type[attack_type] = MetricCalculator.success_rate(
                    type_results,
                    target_field
                )

        return by_type

    @staticmethod
    def ranking_diversity(
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> float:
        """Calculate diversity of products appearing in top-K.

        Higher diversity means more varied products in top positions.

        Args:
            results: List of ranking results
            top_k: Number of top positions to consider

        Returns:
            Diversity score between 0 and 1
        """
        if not results:
            return 0.0

        # Count frequency of products in top-K
        product_counts: Counter = Counter()
        for r in results:
            ranked = r.get("ranked_products", [])
            top_ids = [p.get("id") for p in ranked[:top_k]]
            product_counts.update(top_ids)

        if not product_counts:
            return 0.0

        # Calculate normalized entropy
        total = sum(product_counts.values())
        probabilities = [count / total for count in product_counts.values()]
        entropy = -sum(p * np.log(p + 1e-10) for p in probabilities)

        # Normalize by maximum possible entropy
        max_entropy = np.log(len(product_counts))
        if max_entropy == 0:
            return 0.0

        return entropy / max_entropy

    @staticmethod
    def ranking_consistency(
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> float:
        """Calculate consistency of rankings across trials.

        Higher consistency means similar products appear in similar positions.

        Args:
            results: List of ranking results
            top_k: Number of top positions to consider

        Returns:
            Consistency score between 0 and 1
        """
        if len(results) < 2:
            return 1.0

        # Extract top-K rankings
        rankings = []
        for r in results:
            ranked = r.get("ranked_products", [])
            top_ids = [p.get("id") for p in ranked[:top_k]]
            rankings.append(top_ids)

        # Calculate pairwise overlap
        overlaps = []
        for i in range(len(rankings)):
            for j in range(i + 1, len(rankings)):
                overlap = len(set(rankings[i]) & set(rankings[j]))
                overlaps.append(overlap / top_k)

        return float(np.mean(overlaps)) if overlaps else 0.0

    @staticmethod
    def positional_bias_score(
        results: List[Dict[str, Any]],
        target_field: str = "attacked_product"
    ) -> Dict[str, float]:
        """Calculate positional bias metrics.

        Analyzes if attack position in context affects success.

        Args:
            results: List of results with 'attack_position' field
            target_field: Field containing attacked product ID

        Returns:
            Dictionary with position-specific success rates
        """
        by_position: Dict[str, List[bool]] = {}

        for r in results:
            position = r.get("attack_position")
            if position is None:
                continue

            target_id = r.get(target_field)
            ranked = r.get("ranked_products", [])
            success = bool(ranked and ranked[0].get("id") == target_id)

            if position not in by_position:
                by_position[position] = []
            by_position[position].append(success)

        # Calculate success rate per position
        scores = {}
        for position, successes in by_position.items():
            scores[f"position_{position}"] = sum(successes) / len(successes)

        return scores

    @staticmethod
    def calculate_statistics(
        values: List[float]
    ) -> Dict[str, float]:
        """Calculate statistical summary of values.

        Args:
            values: List of numeric values

        Returns:
            Dictionary with mean, std, min, max, median, quartiles
        """
        if not values:
            return {}

        return {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "median": float(np.median(values)),
            "q25": float(np.percentile(values, 25)),
            "q75": float(np.percentile(values, 75)),
            "count": len(values),
        }
