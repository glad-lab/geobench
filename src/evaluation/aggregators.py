"""Result aggregation strategies."""

from typing import List, Dict, Any
import numpy as np
from .base import EvaluationResult


class ResultAggregator:
    """Aggregates multiple EvaluationResults.

    Provides methods for combining results from multiple evaluators
    or multiple runs of the same evaluator.
    """

    @staticmethod
    def aggregate(results: List[EvaluationResult]) -> Dict[str, Any]:
        """Aggregate multiple evaluation results.

        Args:
            results: List of EvaluationResult objects

        Returns:
            Dictionary with aggregated metrics and summary statistics
        """
        if not results:
            return {}

        all_metrics: Dict[str, Any] = {}

        # Collect all metric keys
        metric_keys = set()
        for result in results:
            metric_keys.update(result.metrics.keys())

        # Aggregate each metric
        for key in metric_keys:
            values = [
                r.metrics.get(key, np.nan)
                for r in results
            ]
            # Filter out NaN values
            values = [v for v in values if not np.isnan(v)]

            if values:
                all_metrics[f"{key}_mean"] = float(np.mean(values))
                all_metrics[f"{key}_std"] = float(np.std(values))
                all_metrics[f"{key}_min"] = float(np.min(values))
                all_metrics[f"{key}_max"] = float(np.max(values))
                all_metrics[f"{key}_median"] = float(np.median(values))
                all_metrics[f"{key}_count"] = len(values)

        # Aggregate status information
        all_metrics["total_results"] = len(results)
        all_metrics["passed_count"] = sum(1 for r in results if r.passed)
        all_metrics["failed_count"] = sum(1 for r in results if not r.passed)
        all_metrics["pass_rate"] = all_metrics["passed_count"] / len(results)

        # Collect all errors and warnings
        all_errors = []
        all_warnings = []
        for r in results:
            all_errors.extend(r.errors)
            all_warnings.extend(r.warnings)

        all_metrics["total_errors"] = len(all_errors)
        all_metrics["total_warnings"] = len(all_warnings)
        all_metrics["unique_errors"] = len(set(all_errors))
        all_metrics["unique_warnings"] = len(set(all_warnings))

        return all_metrics

    @staticmethod
    def combine_by_evaluator(
        results: List[EvaluationResult]
    ) -> Dict[str, Dict[str, Any]]:
        """Aggregate results grouped by evaluator name.

        Args:
            results: List of EvaluationResult objects

        Returns:
            Dictionary mapping evaluator name to aggregated metrics
        """
        by_evaluator: Dict[str, List[EvaluationResult]] = {}

        # Group by evaluator
        for result in results:
            name = result.evaluator_name
            if name not in by_evaluator:
                by_evaluator[name] = []
            by_evaluator[name].append(result)

        # Aggregate each group
        aggregated = {}
        for name, group_results in by_evaluator.items():
            aggregated[name] = ResultAggregator.aggregate(group_results)

        return aggregated

    @staticmethod
    def summary_report(results: List[EvaluationResult]) -> str:
        """Generate human-readable summary report.

        Args:
            results: List of EvaluationResult objects

        Returns:
            Formatted summary string
        """
        if not results:
            return "No results to summarize"

        agg = ResultAggregator.aggregate(results)
        by_eval = ResultAggregator.combine_by_evaluator(results)

        report_lines = [
            "=" * 60,
            "EVALUATION SUMMARY REPORT",
            "=" * 60,
            f"Total Results: {agg['total_results']}",
            f"Passed: {agg['passed_count']} ({agg['pass_rate']:.1%})",
            f"Failed: {agg['failed_count']}",
            f"Total Errors: {agg['total_errors']}",
            f"Total Warnings: {agg['total_warnings']}",
            "",
            "BY EVALUATOR:",
            "-" * 60,
        ]

        for evaluator_name, metrics in by_eval.items():
            report_lines.append(f"\n{evaluator_name}:")
            report_lines.append(f"  Results: {metrics['total_results']}")
            report_lines.append(f"  Pass Rate: {metrics['pass_rate']:.1%}")

            # Show key metrics if available
            key_metrics = [
                k for k in metrics.keys()
                if k.endswith("_mean") and not k.startswith("total_")
            ]
            for metric in sorted(key_metrics):
                base_name = metric.replace("_mean", "")
                mean_val = metrics[metric]
                std_val = metrics.get(f"{base_name}_std", 0)
                report_lines.append(f"  {base_name}: {mean_val:.4f} ± {std_val:.4f}")

        report_lines.append("=" * 60)

        return "\n".join(report_lines)


class MetricAggregator:
    """Aggregates metrics across multiple experiments.

    Provides statistical analysis of metric distributions.
    """

    @staticmethod
    def compute_statistics(values: List[float]) -> Dict[str, float]:
        """Compute statistical summary of values.

        Args:
            values: List of numeric values

        Returns:
            Dictionary with comprehensive statistics
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
            "iqr": float(np.percentile(values, 75) - np.percentile(values, 25)),
            "variance": float(np.var(values)),
            "count": len(values),
        }

    @staticmethod
    def confidence_interval(
        values: List[float],
        confidence: float = 0.95
    ) -> Dict[str, float]:
        """Calculate confidence interval for values.

        Args:
            values: List of numeric values
            confidence: Confidence level (default 0.95 for 95% CI)

        Returns:
            Dictionary with CI bounds and statistics
        """
        if not values:
            return {}

        from scipy import stats as scipy_stats

        mean = np.mean(values)
        sem = scipy_stats.sem(values)
        ci = scipy_stats.t.interval(
            confidence,
            len(values) - 1,
            loc=mean,
            scale=sem
        )

        return {
            "mean": float(mean),
            "sem": float(sem),
            "ci_lower": float(ci[0]),
            "ci_upper": float(ci[1]),
            "confidence_level": confidence,
        }

    @staticmethod
    def compare_distributions(
        baseline: List[float],
        treatment: List[float]
    ) -> Dict[str, Any]:
        """Compare two distributions statistically.

        Args:
            baseline: Baseline values
            treatment: Treatment values

        Returns:
            Dictionary with comparison statistics
        """
        from scipy import stats as scipy_stats

        if not baseline or not treatment:
            return {}

        # T-test
        t_stat, t_pval = scipy_stats.ttest_ind(baseline, treatment)

        # Mann-Whitney U test (non-parametric)
        u_stat, u_pval = scipy_stats.mannwhitneyu(
            baseline,
            treatment,
            alternative='two-sided'
        )

        # Effect size (Cohen's d)
        pooled_std = np.sqrt(
            (np.var(baseline) + np.var(treatment)) / 2
        )
        if pooled_std > 0:
            cohens_d = (np.mean(treatment) - np.mean(baseline)) / pooled_std
        else:
            cohens_d = 0.0

        return {
            "baseline_mean": float(np.mean(baseline)),
            "treatment_mean": float(np.mean(treatment)),
            "difference": float(np.mean(treatment) - np.mean(baseline)),
            "t_statistic": float(t_stat),
            "t_pvalue": float(t_pval),
            "u_statistic": float(u_stat),
            "u_pvalue": float(u_pval),
            "cohens_d": float(cohens_d),
            "significant_at_05": bool(t_pval < 0.05),
            "significant_at_01": bool(t_pval < 0.01),
        }
