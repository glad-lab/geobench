"""
Attack effectiveness analysis module.

This module analyzes attack effectiveness including position-based analysis,
success trends over time, and pattern recognition.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from collections import defaultdict
import logging

from .base import BaseAnalyzer, AnalysisResult
from ..ranking.metrics import RankingMetrics

logger = logging.getLogger(__name__)


class EffectivenessAnalyzer(BaseAnalyzer):
    """
    Attack effectiveness analysis.

    Analyzes attack effectiveness through multiple lenses:
        - Positional bias (attack position in context)
        - Success trends across trials
        - Query-type specific effectiveness
        - Position-1 success rates

    Example:
        >>> analyzer = EffectivenessAnalyzer()
        >>> result = analyzer.positional_bias_analysis(data)
        >>> print(result.metrics["end_position_effectiveness"])
    """

    def analyze(self, data: List[Dict[str, Any]]) -> AnalysisResult:
        """
        Perform comprehensive effectiveness analysis with enhanced metrics.

        Calculates both binary (Top-K success rates) and magnitude metrics
        (absolute improvement, percentage improvement, final position).

        Args:
            data: Experimental data with attack information

        Returns:
            AnalysisResult with comprehensive effectiveness metrics

        Metrics returned:
            Binary metrics:
                - top_3_success_rate: Fraction reaching top-3 positions
                - top_5_success_rate: Fraction reaching top-5 positions
                - top_10_success_rate: Fraction reaching top-10 positions
                - position_1_rate: Fraction reaching position 1 (legacy)

            Magnitude metrics:
                - mean_absolute_improvement: Average position change
                - mean_percentage_improvement: Average % improvement
                - mean_final_position: Average final ranking position
        """
        self._validate_data(data)

        # Extract success metrics
        successes = []
        final_positions = []
        baseline_positions = []

        for item in data:
            metrics = item.get("metrics", {})
            successes.append(metrics.get("success", 0.0))

            # Track final position if available
            if "final_position" in metrics:
                final_positions.append(metrics["final_position"])

            # Track baseline position if available
            if "baseline_position" in metrics:
                baseline_positions.append(metrics["baseline_position"])

        # Determine total items for percentage calculation
        total_items = max(final_positions) if final_positions else 10  # Default to 10 if unknown

        # Calculate binary metrics (Top-K success rates)
        metrics_dict = {
            # Legacy overall metrics
            "overall_success_rate": np.mean(successes) if successes else 0.0,
            "success_std": np.std(successes, ddof=1) if len(successes) > 1 else 0.0,
            "n_trials": len(data)
        }

        # Binary metrics: Top-K success rates
        if final_positions:
            metrics_dict["top_3_success_rate"] = RankingMetrics.top_k_success_rate(final_positions, k=3)
            metrics_dict["top_5_success_rate"] = RankingMetrics.top_k_success_rate(final_positions, k=5)
            metrics_dict["top_10_success_rate"] = RankingMetrics.top_k_success_rate(final_positions, k=10)
            metrics_dict["position_1_rate"] = RankingMetrics.top_k_success_rate(final_positions, k=1)  # Legacy

        # Magnitude metrics
        if final_positions:
            metrics_dict["mean_final_position"] = RankingMetrics.mean_final_position(final_positions)

        if baseline_positions and final_positions and len(baseline_positions) == len(final_positions):
            # Absolute improvement
            absolute_improvements = RankingMetrics.absolute_position_improvement(
                baseline_positions, final_positions
            )
            metrics_dict["mean_absolute_improvement"] = np.mean(absolute_improvements)
            metrics_dict["median_absolute_improvement"] = np.median(absolute_improvements)

            # Percentage improvement
            percentage_improvements = RankingMetrics.percentage_improvement(
                baseline_positions, final_positions, total_items
            )
            metrics_dict["mean_percentage_improvement"] = np.mean(percentage_improvements)
            metrics_dict["median_percentage_improvement"] = np.median(percentage_improvements)

        # Generate insights
        insights = [
            f"Overall success rate: {metrics_dict['overall_success_rate']:.3f}",
        ]

        if "top_3_success_rate" in metrics_dict:
            insights.append(
                f"Binary metrics - Top-3: {metrics_dict['top_3_success_rate']:.3f}, "
                f"Top-5: {metrics_dict['top_5_success_rate']:.3f}, "
                f"Top-10: {metrics_dict['top_10_success_rate']:.3f}"
            )

        if "mean_final_position" in metrics_dict:
            insights.append(
                f"Magnitude metrics - Mean final position: {metrics_dict['mean_final_position']:.2f}"
            )

        if "mean_absolute_improvement" in metrics_dict:
            insights.append(
                f"Mean absolute improvement: {metrics_dict['mean_absolute_improvement']:.2f} positions"
            )

        if "mean_percentage_improvement" in metrics_dict:
            insights.append(
                f"Mean percentage improvement: {metrics_dict['mean_percentage_improvement']:.1f}%"
            )

        return AnalysisResult(
            analyzer_name=self.name,
            metrics=metrics_dict,
            insights=insights
        )

    def positional_bias_analysis(
        self,
        data: List[Dict[str, Any]]
    ) -> AnalysisResult:
        """
        Analyze attack effectiveness by position in context.

        Tests whether attack position (start, middle, end) affects success rate.
        Replicates Figure 7 from Nestaas et al., 2024.

        Args:
            data: Experimental data with position information

        Returns:
            AnalysisResult with positional bias metrics

        Example:
            >>> data = [
            ...     {"attack_info": {"position": "start"}, "metrics": {"success": 0.3}},
            ...     {"attack_info": {"position": "end"}, "metrics": {"success": 0.5}}
            ... ]
            >>> result = analyzer.positional_bias_analysis(data)
        """
        # Group by position
        position_data = defaultdict(list)
        for item in data:
            position = item.get("attack_info", {}).get("position", "unknown")
            success = item.get("metrics", {}).get("success", 0.0)
            position_data[position].append(success)

        if not position_data:
            raise ValueError("No position information found in data")

        # Calculate metrics for each position
        metrics = {}
        position_stats = {}

        for position, successes in position_data.items():
            mean_success = np.mean(successes)
            std_success = np.std(successes, ddof=1) if len(successes) > 1 else 0.0

            position_stats[position] = {
                "mean": mean_success,
                "std": std_success,
                "n": len(successes)
            }

            metrics[f"{position}_mean_success"] = mean_success
            metrics[f"{position}_std_success"] = std_success
            metrics[f"{position}_n"] = len(successes)

        # Calculate relative effectiveness (end vs start)
        if "start" in position_stats and "end" in position_stats:
            start_mean = position_stats["start"]["mean"]
            end_mean = position_stats["end"]["mean"]

            if start_mean > 0:
                metrics["end_relative_effectiveness"] = end_mean / start_mean
            else:
                metrics["end_relative_effectiveness"] = 0.0

        # Generate insights
        insights = []
        for position, stats in sorted(position_stats.items()):
            insights.append(
                f"{position.capitalize()} position: {stats['mean']:.3f} ± {stats['std']:.3f} "
                f"(n={stats['n']})"
            )

        if "end_relative_effectiveness" in metrics:
            rel_eff = metrics["end_relative_effectiveness"]
            if rel_eff > 1.2:
                insights.append(
                    f"End position is {rel_eff:.2f}x more effective than start "
                    "(supports positional bias hypothesis)"
                )
            elif rel_eff < 0.8:
                insights.append(
                    f"Start position is {1/rel_eff:.2f}x more effective than end "
                    "(contradicts positional bias hypothesis)"
                )
            else:
                insights.append(
                    "No strong positional bias detected "
                    f"(relative effectiveness: {rel_eff:.2f})"
                )

        return AnalysisResult(
            analyzer_name=f"{self.name}::PositionalBias",
            metrics=metrics,
            insights=insights,
            metadata={"positions": list(position_data.keys())}
        )

    def success_by_query_type(
        self,
        data: List[Dict[str, Any]]
    ) -> AnalysisResult:
        """
        Analyze attack effectiveness by query type.

        Args:
            data: Experimental data with query information

        Returns:
            AnalysisResult with query-type-specific metrics

        Example:
            >>> data = [
            ...     {"metadata": {"query_type": "recommendation"}, "metrics": {"success": 0.5}},
            ...     {"metadata": {"query_type": "comparison"}, "metrics": {"success": 0.3}}
            ... ]
            >>> result = analyzer.success_by_query_type(data)
        """
        # Group by query type
        query_data = defaultdict(list)
        for item in data:
            query_type = item.get("metadata", {}).get("query_type", "unknown")
            success = item.get("metrics", {}).get("success", 0.0)
            query_data[query_type].append(success)

        if not query_data:
            # Try to extract from query text
            query_data = self._infer_query_types(data)

        if not query_data:
            raise ValueError("No query type information found in data")

        # Calculate metrics for each query type
        metrics = {}
        query_stats = {}

        for query_type, successes in query_data.items():
            mean_success = np.mean(successes)
            std_success = np.std(successes, ddof=1) if len(successes) > 1 else 0.0

            query_stats[query_type] = {
                "mean": mean_success,
                "std": std_success,
                "n": len(successes)
            }

            clean_name = query_type.replace(" ", "_").lower()
            metrics[f"{clean_name}_mean"] = mean_success
            metrics[f"{clean_name}_std"] = std_success
            metrics[f"{clean_name}_n"] = len(successes)

        # Find most/least effective query types
        sorted_queries = sorted(
            query_stats.items(),
            key=lambda x: x[1]["mean"],
            reverse=True
        )

        metrics["most_effective_query_type"] = sorted_queries[0][0]
        metrics["least_effective_query_type"] = sorted_queries[-1][0]

        # Generate insights
        insights = []
        for query_type, stats in sorted_queries:
            insights.append(
                f"{query_type}: {stats['mean']:.3f} ± {stats['std']:.3f} "
                f"(n={stats['n']})"
            )

        return AnalysisResult(
            analyzer_name=f"{self.name}::QueryType",
            metrics=metrics,
            insights=insights,
            metadata={"query_types": list(query_data.keys())}
        )

    def success_trend_analysis(
        self,
        data: List[Dict[str, Any]]
    ) -> AnalysisResult:
        """
        Analyze success rate trends across trials.

        Detects whether attack effectiveness changes over time,
        which could indicate learning effects or degradation.

        Args:
            data: Experimental data sorted by trial order

        Returns:
            AnalysisResult with trend metrics

        Example:
            >>> # Data should be in trial order
            >>> result = analyzer.success_trend_analysis(data)
            >>> print(result.metrics["trend_slope"])
        """
        # Extract success rates in order
        successes = []
        trial_ids = []

        for item in data:
            if "trial_id" in item:
                trial_ids.append(item["trial_id"])
                successes.append(item.get("metrics", {}).get("success", 0.0))

        if len(successes) < 3:
            raise ValueError("Need at least 3 trials for trend analysis")

        # Sort by trial ID if available
        if trial_ids:
            sorted_data = sorted(zip(trial_ids, successes))
            trial_ids, successes = zip(*sorted_data)
            trial_ids = list(trial_ids)
            successes = list(successes)
        else:
            trial_ids = list(range(len(successes)))

        # Calculate linear trend
        x = np.array(trial_ids)
        y = np.array(successes)

        # Linear regression
        slope, intercept = np.polyfit(x, y, 1)
        r_squared = np.corrcoef(x, y)[0, 1] ** 2

        metrics = {
            "trend_slope": float(slope),
            "trend_intercept": float(intercept),
            "r_squared": float(r_squared),
            "early_mean": np.mean(successes[:len(successes)//3]),
            "late_mean": np.mean(successes[-len(successes)//3:]),
            "n_trials": len(successes)
        }

        # Generate insights
        insights = []
        if abs(slope) > 0.001:
            direction = "increasing" if slope > 0 else "decreasing"
            insights.append(
                f"Success rate is {direction} over time "
                f"(slope={slope:.4f}, R²={r_squared:.3f})"
            )
        else:
            insights.append(
                f"Success rate is stable over time (slope={slope:.4f})"
            )

        early_late_diff = metrics["late_mean"] - metrics["early_mean"]
        if abs(early_late_diff) > 0.1:
            direction = "improved" if early_late_diff > 0 else "degraded"
            insights.append(
                f"Performance {direction} from early to late trials "
                f"(Δ={early_late_diff:.3f})"
            )

        return AnalysisResult(
            analyzer_name=f"{self.name}::Trend",
            metrics=metrics,
            insights=insights,
            metadata={"n_trials": len(successes)}
        )

    def _infer_query_types(
        self,
        data: List[Dict[str, Any]]
    ) -> Dict[str, List[float]]:
        """
        Infer query types from query text if not explicitly provided.

        Args:
            data: Experimental data

        Returns:
            Dictionary mapping query types to success rates
        """
        query_data = defaultdict(list)

        for item in data:
            query = item.get("metadata", {}).get("query", "").lower()
            success = item.get("metrics", {}).get("success", 0.0)

            # Simple heuristic-based classification
            if "best" in query or "recommend" in query:
                query_type = "recommendation"
            elif "compare" in query or "vs" in query:
                query_type = "comparison"
            elif "how" in query or "what" in query:
                query_type = "informational"
            else:
                query_type = "general"

            query_data[query_type].append(success)

        return dict(query_data)
