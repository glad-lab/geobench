"""
Comparative analysis for cross-provider and cross-attack-type experiments.

This module provides analysis tools for comparing results across different
LLM providers, attack types, and experimental conditions.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from collections import defaultdict
import logging

from .base import BaseAnalyzer, AnalysisResult

logger = logging.getLogger(__name__)


class ComparativeAnalyzer(BaseAnalyzer):
    """
    Cross-provider and cross-attack-type comparative analysis.

    Compares experimental results across different dimensions:
        - LLM providers (OpenAI, Anthropic, Bedrock)
        - Attack types (prompt injection, discreditation, persuasion)
        - Query types or product categories
        - Time periods or experimental conditions

    Example:
        >>> analyzer = ComparativeAnalyzer()
        >>> result = analyzer.compare_providers(data)
        >>> print(result.metrics["best_provider"])
    """

    def analyze(self, data: List[Dict[str, Any]]) -> AnalysisResult:
        """
        Perform comprehensive comparative analysis.

        Automatically detects dimensions to compare (providers, attack types)
        and generates comparative metrics.

        Args:
            data: Experimental data with provider/attack type information

        Returns:
            AnalysisResult with comparative metrics
        """
        self._validate_data(data)

        # Detect comparison dimensions
        has_providers = any("provider" in item.get("metadata", {}) for item in data)
        has_attack_types = any("attack_type" in item.get("attack_info", {}) for item in data)

        metrics = {}
        insights = []

        if has_providers:
            provider_result = self.compare_providers(data)
            metrics.update(provider_result.metrics)
            insights.extend(provider_result.insights)

        if has_attack_types:
            attack_result = self.compare_attack_types(data)
            metrics.update(attack_result.metrics)
            insights.extend(attack_result.insights)

        return AnalysisResult(
            analyzer_name=self.name,
            metrics=metrics,
            insights=insights,
            metadata={"has_providers": has_providers, "has_attack_types": has_attack_types}
        )

    def compare_providers(
        self,
        data: List[Dict[str, Any]]
    ) -> AnalysisResult:
        """
        Compare results across LLM providers.

        Args:
            data: Experimental data with provider information

        Returns:
            AnalysisResult with provider comparison metrics

        Example:
            >>> data = [
            ...     {"metadata": {"provider": "openai"}, "metrics": {"success": 0.5}},
            ...     {"metadata": {"provider": "anthropic"}, "metrics": {"success": 0.6}}
            ... ]
            >>> result = analyzer.compare_providers(data)
        """
        # Group by provider
        provider_data = defaultdict(list)
        for item in data:
            provider = item.get("metadata", {}).get("provider")
            if provider:  # Only include if provider is not None or empty
                success = item.get("metrics", {}).get("success", 0.0)
                provider_data[provider].append(success)

        if not provider_data:
            raise ValueError("No provider information found in data")

        # Calculate metrics for each provider
        metrics = {}
        provider_stats = {}

        for provider, successes in provider_data.items():
            mean_success = np.mean(successes)
            std_success = np.std(successes, ddof=1) if len(successes) > 1 else 0.0

            provider_stats[provider] = {
                "mean": mean_success,
                "std": std_success,
                "n": len(successes)
            }

            metrics[f"{provider}_mean"] = mean_success
            metrics[f"{provider}_std"] = std_success
            metrics[f"{provider}_n"] = len(successes)

        # Rank providers by effectiveness
        rankings = self._rank_by_metric(provider_stats, "mean")
        metrics["best_provider"] = rankings[0][0]
        metrics["worst_provider"] = rankings[-1][0]
        metrics["provider_range"] = rankings[0][1]["mean"] - rankings[-1][1]["mean"]

        # Calculate relative performance
        best_mean = rankings[0][1]["mean"]
        for provider, stats in provider_stats.items():
            if best_mean > 0:
                metrics[f"{provider}_relative_performance"] = stats["mean"] / best_mean
            else:
                metrics[f"{provider}_relative_performance"] = 0.0

        # Generate insights
        insights = []
        insights.append(
            f"Best performing provider: {rankings[0][0]} "
            f"(mean success: {rankings[0][1]['mean']:.3f})"
        )
        insights.append(
            f"Worst performing provider: {rankings[-1][0]} "
            f"(mean success: {rankings[-1][1]['mean']:.3f})"
        )
        insights.append(
            f"Performance range across providers: {metrics['provider_range']:.3f}"
        )

        return AnalysisResult(
            analyzer_name=f"{self.name}::ProviderComparison",
            metrics=metrics,
            insights=insights,
            metadata={"num_providers": len(provider_data), "rankings": rankings}
        )

    def compare_attack_types(
        self,
        data: List[Dict[str, Any]]
    ) -> AnalysisResult:
        """
        Compare results across attack types.

        Args:
            data: Experimental data with attack type information

        Returns:
            AnalysisResult with attack type comparison metrics

        Example:
            >>> data = [
            ...     {"attack_info": {"attack_type": "prompt_injection"}, "metrics": {"success": 0.6}},
            ...     {"attack_info": {"attack_type": "persuasion"}, "metrics": {"success": 0.4}}
            ... ]
            >>> result = analyzer.compare_attack_types(data)
        """
        # Group by attack type
        attack_data = defaultdict(list)
        for item in data:
            attack_type = item.get("attack_info", {}).get("attack_type")
            if attack_type:  # Only include if attack_type is not None or empty
                success = item.get("metrics", {}).get("success", 0.0)
                attack_data[attack_type].append(success)

        if not attack_data:
            raise ValueError("No attack type information found in data")

        # Calculate metrics for each attack type
        metrics = {}
        attack_stats = {}

        for attack_type, successes in attack_data.items():
            mean_success = np.mean(successes)
            std_success = np.std(successes, ddof=1) if len(successes) > 1 else 0.0

            attack_stats[attack_type] = {
                "mean": mean_success,
                "std": std_success,
                "n": len(successes)
            }

            # Clean attack type name for metric key
            clean_name = attack_type.replace(" ", "_").lower()
            metrics[f"{clean_name}_mean"] = mean_success
            metrics[f"{clean_name}_std"] = std_success
            metrics[f"{clean_name}_n"] = len(successes)

        # Rank attack types by effectiveness
        rankings = self._rank_by_metric(attack_stats, "mean")
        metrics["most_effective_attack"] = rankings[0][0]
        metrics["least_effective_attack"] = rankings[-1][0]
        metrics["attack_effectiveness_range"] = rankings[0][1]["mean"] - rankings[-1][1]["mean"]

        # Generate insights
        insights = []
        insights.append(
            f"Most effective attack: {rankings[0][0]} "
            f"(mean success: {rankings[0][1]['mean']:.3f})"
        )
        insights.append(
            f"Least effective attack: {rankings[-1][0]} "
            f"(mean success: {rankings[-1][1]['mean']:.3f})"
        )

        # Check for statistical significance
        if len(attack_data) > 1:
            variances = [np.var(successes, ddof=1) for successes in attack_data.values()]
            if max(variances) / (min(variances) + 1e-10) > 4:
                insights.append(
                    "Warning: Large variance differences between attack types. "
                    "Consider non-parametric tests."
                )

        return AnalysisResult(
            analyzer_name=f"{self.name}::AttackTypeComparison",
            metrics=metrics,
            insights=insights,
            metadata={"num_attack_types": len(attack_data), "rankings": rankings}
        )

    def rank_by_effectiveness(
        self,
        data: List[Dict[str, Any]],
        dimension: str = "provider"
    ) -> AnalysisResult:
        """
        Rank entities by effectiveness along a dimension.

        Args:
            data: Experimental data
            dimension: Dimension to rank by ("provider", "attack_type", etc.)

        Returns:
            AnalysisResult with ranking metrics

        Example:
            >>> result = analyzer.rank_by_effectiveness(data, dimension="provider")
            >>> rankings = result.metadata["rankings"]
        """
        # Group by dimension
        dimension_data = defaultdict(list)
        for item in data:
            if dimension in item.get("metadata", {}):
                key = item["metadata"][dimension]
            elif dimension in item.get("attack_info", {}):
                key = item["attack_info"][dimension]
            else:
                continue

            success = item.get("metrics", {}).get("success", 0.0)
            dimension_data[key].append(success)

        if not dimension_data:
            raise ValueError(f"No data found for dimension: {dimension}")

        # Calculate statistics
        stats = {}
        for key, successes in dimension_data.items():
            stats[key] = {
                "mean": np.mean(successes),
                "std": np.std(successes, ddof=1) if len(successes) > 1 else 0.0,
                "n": len(successes),
                "min": np.min(successes),
                "max": np.max(successes)
            }

        # Rank by mean success
        rankings = self._rank_by_metric(stats, "mean")

        # Create metrics
        metrics = {
            "num_entities": len(stats),
            "top_entity": rankings[0][0],
            "top_mean": rankings[0][1]["mean"],
            "bottom_entity": rankings[-1][0],
            "bottom_mean": rankings[-1][1]["mean"]
        }

        # Generate insights
        insights = [
            f"Ranked {len(stats)} entities by {dimension}",
            f"Top performer: {rankings[0][0]} (mean: {rankings[0][1]['mean']:.3f})",
            f"Bottom performer: {rankings[-1][0]} (mean: {rankings[-1][1]['mean']:.3f})"
        ]

        return AnalysisResult(
            analyzer_name=f"{self.name}::Ranking",
            metrics=metrics,
            insights=insights,
            metadata={"rankings": rankings, "dimension": dimension}
        )

    def _rank_by_metric(
        self,
        stats: Dict[str, Dict[str, float]],
        metric: str
    ) -> List[tuple]:
        """
        Rank entities by a specific metric.

        Args:
            stats: Dictionary of entity statistics
            metric: Metric to rank by

        Returns:
            List of (entity, stats) tuples sorted by metric descending
        """
        return sorted(
            stats.items(),
            key=lambda x: x[1][metric],
            reverse=True
        )
