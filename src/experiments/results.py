"""
Result aggregation and serialization for experiments.

This module provides utilities for aggregating, serializing, and loading
experiment results with comprehensive metadata preservation.

Design Patterns:
    - Aggregate Pattern: Combine multiple experiment results
    - Serialization Pattern: JSON persistence with schema versioning
    - Factory Method: Load results from files
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import json
import logging
import numpy as np

from .base import ExperimentResult, TrialResult, ExperimentConfig, ExperimentType

logger = logging.getLogger(__name__)


def convert_numpy_types(obj: Any) -> Any:
    """
    Convert numpy types to native Python types for JSON serialization.

    Args:
        obj: Object potentially containing numpy types

    Returns:
        Object with numpy types converted to native Python types
    """
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


class ResultAggregator:
    """
    Aggregates results from multiple experiments.

    This class combines results from multiple experiment runs, computing
    aggregate statistics and providing serialization capabilities.

    Features:
        - Cross-experiment metric aggregation
        - JSON serialization with metadata
        - Result loading and validation
        - Statistical summary generation

    Example:
        >>> aggregator = ResultAggregator()
        >>> aggregator.add_result(baseline_result)
        >>> aggregator.add_result(attack_result)
        >>> summary = aggregator.aggregate_metrics()
        >>> aggregator.to_json("results_summary.json")
    """

    def __init__(self):
        """Initialize empty aggregator."""
        self.results: List[ExperimentResult] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }

    def add_result(self, result: ExperimentResult) -> None:
        """
        Add experiment result to aggregator.

        Args:
            result: ExperimentResult to add

        Example:
            >>> aggregator.add_result(experiment.run())
        """
        self.results.append(result)
        logger.info(
            f"Added result: {result.config.experiment_type.value} "
            f"({len(result.trials)} trials)"
        )

    def add_results(self, results: List[ExperimentResult]) -> None:
        """
        Add multiple experiment results.

        Args:
            results: List of ExperimentResult objects

        Example:
            >>> aggregator.add_results(runner.run_all())
        """
        for result in results:
            self.add_result(result)

    def aggregate_metrics(self) -> Dict[str, Any]:
        """
        Aggregate metrics across all experiments.

        Computes summary statistics across all experiment results,
        grouping by experiment type.

        Returns:
            Dictionary with aggregate metrics by experiment type

        Example:
            >>> metrics = aggregator.aggregate_metrics()
            >>> print(metrics['single_attack']['success_mean'])
        """
        if not self.results:
            logger.warning("No results to aggregate")
            return {}

        # Group by experiment type
        by_type: Dict[str, List[ExperimentResult]] = {}
        for result in self.results:
            exp_type = result.config.experiment_type.value
            if exp_type not in by_type:
                by_type[exp_type] = []
            by_type[exp_type].append(result)

        # Aggregate for each type
        aggregated = {}
        for exp_type, results in by_type.items():
            aggregated[exp_type] = self._aggregate_type(results)

        # Overall statistics
        aggregated["overall"] = {
            "total_experiments": len(self.results),
            "total_trials": sum(len(r.trials) for r in self.results),
            "experiment_types": list(by_type.keys()),
        }

        logger.info(
            f"Aggregated metrics for {len(self.results)} experiments "
            f"across {len(by_type)} types"
        )

        return aggregated

    def _aggregate_type(self, results: List[ExperimentResult]) -> Dict[str, Any]:
        """
        Aggregate metrics for single experiment type.

        Args:
            results: Results of same experiment type

        Returns:
            Aggregate metrics dictionary
        """
        # Collect all aggregate metrics
        all_metrics = [r.aggregate_metrics for r in results]

        # Find common metric keys
        if not all_metrics:
            return {}

        common_keys = set(all_metrics[0].keys())
        for metrics in all_metrics[1:]:
            common_keys &= set(metrics.keys())

        # Compute statistics for each metric
        aggregated = {}
        for key in common_keys:
            values = [m[key] for m in all_metrics if isinstance(m.get(key), (int, float))]

            if values:
                aggregated[f"{key}_mean"] = np.mean(values)
                aggregated[f"{key}_std"] = np.std(values)
                aggregated[f"{key}_min"] = np.min(values)
                aggregated[f"{key}_max"] = np.max(values)

        # Add metadata
        aggregated["num_experiments"] = len(results)
        aggregated["total_trials"] = sum(len(r.trials) for r in results)

        return aggregated

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert aggregator to dictionary.

        Returns:
            Dictionary representation with all results and metadata

        Example:
            >>> data = aggregator.to_dict()
            >>> print(json.dumps(data, indent=2))
        """
        return {
            "metadata": self.metadata,
            "num_experiments": len(self.results),
            "aggregate_metrics": self.aggregate_metrics(),
            "results": [self._result_to_dict(r) for r in self.results]
        }

    def _result_to_dict(self, result: ExperimentResult) -> Dict[str, Any]:
        """
        Convert ExperimentResult to dictionary.

        Args:
            result: ExperimentResult to convert

        Returns:
            Dictionary representation
        """
        return {
            "config": {
                "experiment_type": result.config.experiment_type.value,
                "num_trials": result.config.num_trials,
                "num_products": result.config.num_products,
                "query": result.config.query,
                "model": result.config.model,
                "provider": result.config.provider,
                "random_seed": result.config.random_seed,
            },
            "aggregate_metrics": result.aggregate_metrics,
            "metadata": result.metadata,
            "timestamp": result.timestamp,
            "num_trials": len(result.trials),
        }

    def to_json(self, file_path: str) -> None:
        """
        Save results to JSON file.

        Creates parent directories if needed and writes formatted JSON.

        Args:
            file_path: Path to output file

        Example:
            >>> aggregator.to_json("data/results/summary.json")
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = self.to_dict()
        data = convert_numpy_types(data)

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {len(self.results)} results to {file_path}")

    @classmethod
    def from_json(cls, file_path: str) -> 'ResultAggregator':
        """
        Load results from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            ResultAggregator with loaded results

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
            ValueError: If file format is invalid

        Example:
            >>> aggregator = ResultAggregator.from_json("data/results/summary.json")
            >>> metrics = aggregator.aggregate_metrics()
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Result file not found: {file_path}")

        with open(path, 'r') as f:
            data = json.load(f)

        aggregator = cls()

        # Load metadata
        if "metadata" in data:
            aggregator.metadata = data["metadata"]

        # Load results (simplified - we don't reconstruct full TrialResult objects)
        # This is because we're primarily interested in aggregate metrics
        if "results" in data:
            logger.warning(
                "Loading results from JSON provides aggregate metrics only. "
                "Individual trial data is not reconstructed."
            )

        logger.info(f"Loaded results from {file_path}")

        return aggregator

    def get_summary(self) -> str:
        """
        Get human-readable summary of results.

        Returns:
            Formatted summary string

        Example:
            >>> print(aggregator.get_summary())
        """
        if not self.results:
            return "No results available"

        metrics = self.aggregate_metrics()

        lines = [
            "=" * 60,
            "Experiment Results Summary",
            "=" * 60,
            f"Total experiments: {metrics.get('overall', {}).get('total_experiments', 0)}",
            f"Total trials: {metrics.get('overall', {}).get('total_trials', 0)}",
            "",
        ]

        # Summary for each experiment type
        for exp_type, type_metrics in metrics.items():
            if exp_type == "overall":
                continue

            lines.append(f"{exp_type.upper()}:")
            lines.append("-" * 40)

            for key, value in type_metrics.items():
                if isinstance(value, float):
                    lines.append(f"  {key}: {value:.4f}")
                else:
                    lines.append(f"  {key}: {value}")

            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def filter_by_type(
        self, experiment_type: ExperimentType
    ) -> 'ResultAggregator':
        """
        Create new aggregator with only specific experiment type.

        Args:
            experiment_type: Type to filter for

        Returns:
            New ResultAggregator with filtered results

        Example:
            >>> baseline_results = aggregator.filter_by_type(ExperimentType.BASELINE)
            >>> baseline_metrics = baseline_results.aggregate_metrics()
        """
        filtered = ResultAggregator()

        for result in self.results:
            if result.config.experiment_type == experiment_type:
                filtered.add_result(result)

        logger.info(
            f"Filtered to {len(filtered.results)} results of type "
            f"{experiment_type.value}"
        )

        return filtered

    def clear(self) -> None:
        """
        Clear all results from aggregator.

        Example:
            >>> aggregator.clear()
        """
        self.results = []
        logger.info("Cleared all results")


class ResultComparator:
    """
    Compare results from different experiments.

    Provides utilities for statistical comparison of experiment results,
    useful for validating hypotheses and measuring improvements.

    Example:
        >>> comparator = ResultComparator()
        >>> comparison = comparator.compare(baseline_result, attack_result)
        >>> print(comparison['success_improvement'])
    """

    @staticmethod
    def compare(
        baseline: ExperimentResult,
        treatment: ExperimentResult
    ) -> Dict[str, Any]:
        """
        Compare two experiment results.

        Args:
            baseline: Baseline experiment result
            treatment: Treatment experiment result

        Returns:
            Dictionary with comparison metrics

        Example:
            >>> comparison = ResultComparator.compare(baseline, attack)
            >>> print(f"Improvement: {comparison['improvement']:.2%}")
        """
        baseline_metrics = baseline.aggregate_metrics
        treatment_metrics = treatment.aggregate_metrics

        # Find common metrics
        common_keys = set(baseline_metrics.keys()) & set(treatment_metrics.keys())

        comparison = {
            "baseline_type": baseline.config.experiment_type.value,
            "treatment_type": treatment.config.experiment_type.value,
        }

        # Compute deltas for common metrics
        for key in common_keys:
            baseline_val = baseline_metrics[key]
            treatment_val = treatment_metrics[key]

            if isinstance(baseline_val, (int, float)) and isinstance(treatment_val, (int, float)):
                comparison[f"{key}_baseline"] = baseline_val
                comparison[f"{key}_treatment"] = treatment_val
                comparison[f"{key}_delta"] = treatment_val - baseline_val

                if baseline_val != 0:
                    comparison[f"{key}_percent_change"] = (
                        (treatment_val - baseline_val) / baseline_val * 100
                    )

        return comparison

    @staticmethod
    def rank_by_metric(
        results: List[ExperimentResult],
        metric_key: str,
        ascending: bool = False
    ) -> List[ExperimentResult]:
        """
        Rank experiment results by specific metric.

        Args:
            results: List of experiment results
            metric_key: Metric key to rank by
            ascending: If True, rank ascending; else descending

        Returns:
            Sorted list of experiment results

        Example:
            >>> ranked = ResultComparator.rank_by_metric(
            ...     results,
            ...     "success_mean",
            ...     ascending=False
            ... )
        """
        def get_metric(result: ExperimentResult) -> float:
            value = result.aggregate_metrics.get(metric_key, float('-inf'))
            return value if isinstance(value, (int, float)) else float('-inf')

        return sorted(results, key=get_metric, reverse=not ascending)
