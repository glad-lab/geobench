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
        Perform comprehensive effectiveness analysis.

        Args:
            data: Experimental data with attack information

        Returns:
            AnalysisResult with effectiveness metrics
        """
        self._validate_data(data)

        # Extract success metrics
        successes = []
        positions = []

        for item in data:
            metrics = item.get("metrics", {})
            successes.append(metrics.get("success", 0.0))

            # Track final position if available
            if "final_position" in metrics:
                positions.append(metrics["final_position"])

        # Calculate aggregate metrics
        metrics_dict = {
            "overall_success_rate": np.mean(successes) if successes else 0.0,
            "success_std": np.std(successes, ddof=1) if len(successes) > 1 else 0.0,
            "position_1_rate": sum(1 for p in positions if p == 1) / len(positions) if positions else 0.0,
            "mean_final_position": np.mean(positions) if positions else 0.0,
            "n_trials": len(data)
        }

        insights = [
            f"Overall success rate: {metrics_dict['overall_success_rate']:.3f}",
            f"Position-1 rate: {metrics_dict['position_1_rate']:.3f}",
            f"Mean final position: {metrics_dict['mean_final_position']:.2f}"
        ]

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
