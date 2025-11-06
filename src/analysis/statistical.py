"""
Statistical analysis for experimental results.

This module provides statistical tests and analyses including t-tests,
ANOVA, chi-square tests, and correlation analysis.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from scipy import stats
import logging

from .base import BaseAnalyzer, AnalysisResult

logger = logging.getLogger(__name__)


class StatisticalAnalyzer(BaseAnalyzer):
    """
    Statistical analysis of experimental results.

    Provides comprehensive statistical testing including:
        - T-tests for comparing two groups
        - ANOVA for comparing multiple groups
        - Chi-square for categorical data
        - Pearson correlation for relationships
        - Effect size calculations (Cohen's d)

    Attributes:
        confidence_level: Confidence level for statistical tests (default: 0.95)

    Example:
        >>> analyzer = StatisticalAnalyzer(confidence_level=0.95)
        >>> result = analyzer.t_test(baseline_data, treatment_data)
        >>> print(f"p-value: {result.metrics['p_value']}")
    """

    def __init__(
        self,
        name: Optional[str] = None,
        confidence_level: float = 0.95
    ):
        """
        Initialize statistical analyzer.

        Args:
            name: Analyzer name
            confidence_level: Confidence level for tests (0-1)
        """
        super().__init__(name)
        self.confidence_level = confidence_level

    def analyze(self, data: List[Dict[str, Any]]) -> AnalysisResult:
        """
        Perform comprehensive statistical analysis.

        Args:
            data: Experimental data with metrics

        Returns:
            AnalysisResult with statistical metrics
        """
        self._validate_data(data)

        # Extract success rates
        success_rates = [
            item.get("metrics", {}).get("success", 0.0)
            for item in data
        ]

        metrics = self._compute_descriptive_stats(success_rates)
        insights = self._generate_insights(metrics)

        return AnalysisResult(
            analyzer_name=self.name,
            metrics=metrics,
            insights=insights,
            confidence=self.confidence_level,
            metadata={"n": len(data)}
        )

    def t_test(
        self,
        group1: List[float],
        group2: List[float],
        paired: bool = False
    ) -> AnalysisResult:
        """
        Perform t-test comparing two groups.

        Args:
            group1: First group of values
            group2: Second group of values
            paired: Whether to use paired t-test

        Returns:
            AnalysisResult with t-test statistics

        Example:
            >>> baseline = [0.2, 0.3, 0.25, 0.28]
            >>> treatment = [0.5, 0.6, 0.55, 0.58]
            >>> result = analyzer.t_test(baseline, treatment)
        """
        if len(group1) == 0 or len(group2) == 0:
            raise ValueError("Cannot perform t-test on empty groups")

        # Perform t-test
        if paired:
            if len(group1) != len(group2):
                raise ValueError("Paired t-test requires equal length groups")
            statistic, p_value = stats.ttest_rel(group1, group2)
            test_name = "Paired t-test"
        else:
            statistic, p_value = stats.ttest_ind(group1, group2)
            test_name = "Independent t-test"

        # Calculate effect size (Cohen's d)
        cohens_d = self._cohens_d(group1, group2)

        # Calculate confidence interval
        ci = self._confidence_interval(group2)

        metrics = {
            "t_statistic": float(statistic),
            "p_value": float(p_value),
            "cohens_d": cohens_d,
            "group1_mean": np.mean(group1),
            "group2_mean": np.mean(group2),
            "group1_std": np.std(group1, ddof=1),
            "group2_std": np.std(group2, ddof=1),
            "ci_lower": ci[0],
            "ci_upper": ci[1],
            "significant": p_value < (1 - self.confidence_level)
        }

        # Generate insights
        insights = []
        if metrics["significant"]:
            direction = "higher" if metrics["group2_mean"] > metrics["group1_mean"] else "lower"
            insights.append(
                f"{test_name} shows statistically significant difference "
                f"(p={p_value:.4f}). Group 2 mean is {direction} than Group 1."
            )
            insights.append(f"Effect size (Cohen's d): {cohens_d:.2f}")
        else:
            insights.append(
                f"{test_name} shows no statistically significant difference "
                f"(p={p_value:.4f})"
            )

        return AnalysisResult(
            analyzer_name=f"{self.name}::{test_name}",
            metrics=metrics,
            insights=insights,
            confidence=self.confidence_level,
            metadata={"test_type": "t_test", "paired": paired}
        )

    def anova(
        self,
        groups: List[List[float]],
        group_names: Optional[List[str]] = None
    ) -> AnalysisResult:
        """
        Perform one-way ANOVA comparing multiple groups.

        Args:
            groups: List of groups, where each group is a list of values
            group_names: Optional names for each group

        Returns:
            AnalysisResult with ANOVA statistics

        Example:
            >>> groups = [
            ...     [0.2, 0.3, 0.25],  # Baseline
            ...     [0.5, 0.6, 0.55],  # Attack 1
            ...     [0.4, 0.5, 0.45]   # Attack 2
            ... ]
            >>> result = analyzer.anova(groups)
        """
        if len(groups) < 2:
            raise ValueError("ANOVA requires at least 2 groups")

        if any(len(g) == 0 for g in groups):
            raise ValueError("Cannot perform ANOVA with empty groups")

        # Perform ANOVA
        f_statistic, p_value = stats.f_oneway(*groups)

        # Calculate group statistics
        group_stats = {}
        for i, group in enumerate(groups):
            name = group_names[i] if group_names else f"Group_{i}"
            group_stats[f"{name}_mean"] = np.mean(group)
            group_stats[f"{name}_std"] = np.std(group, ddof=1)

        metrics = {
            "f_statistic": float(f_statistic),
            "p_value": float(p_value),
            "significant": p_value < (1 - self.confidence_level),
            "num_groups": len(groups),
            **group_stats
        }

        # Generate insights
        insights = []
        if metrics["significant"]:
            insights.append(
                f"One-way ANOVA shows statistically significant difference "
                f"between groups (F={f_statistic:.2f}, p={p_value:.4f})"
            )
            means = [np.mean(g) for g in groups]
            best_idx = np.argmax(means)
            best_name = group_names[best_idx] if group_names else f"Group_{best_idx}"
            insights.append(f"Highest mean: {best_name} ({means[best_idx]:.3f})")
        else:
            insights.append(
                f"One-way ANOVA shows no statistically significant difference "
                f"between groups (p={p_value:.4f})"
            )

        return AnalysisResult(
            analyzer_name=f"{self.name}::ANOVA",
            metrics=metrics,
            insights=insights,
            confidence=self.confidence_level,
            metadata={"test_type": "anova", "num_groups": len(groups)}
        )

    def chi_square(
        self,
        observed: List[int],
        expected: Optional[List[int]] = None
    ) -> AnalysisResult:
        """
        Perform chi-square goodness of fit test.

        Args:
            observed: Observed frequencies
            expected: Expected frequencies (uniform if not provided)

        Returns:
            AnalysisResult with chi-square statistics

        Example:
            >>> observed = [30, 45, 25]  # Success counts per attack type
            >>> result = analyzer.chi_square(observed)
        """
        if len(observed) == 0:
            raise ValueError("Cannot perform chi-square test on empty data")

        if expected is None:
            # Uniform distribution
            expected = [sum(observed) / len(observed)] * len(observed)

        # Perform chi-square test
        chi2_statistic, p_value = stats.chisquare(observed, expected)

        metrics = {
            "chi2_statistic": float(chi2_statistic),
            "p_value": float(p_value),
            "significant": p_value < (1 - self.confidence_level),
            "degrees_of_freedom": len(observed) - 1
        }

        # Generate insights
        insights = []
        if metrics["significant"]:
            insights.append(
                f"Chi-square test shows significant deviation from expected "
                f"distribution (χ²={chi2_statistic:.2f}, p={p_value:.4f})"
            )
        else:
            insights.append(
                f"Chi-square test shows no significant deviation from expected "
                f"distribution (p={p_value:.4f})"
            )

        return AnalysisResult(
            analyzer_name=f"{self.name}::ChiSquare",
            metrics=metrics,
            insights=insights,
            confidence=self.confidence_level,
            metadata={"test_type": "chi_square"}
        )

    def pearson_correlation(
        self,
        x: List[float],
        y: List[float]
    ) -> AnalysisResult:
        """
        Calculate Pearson correlation between two variables.

        Args:
            x: First variable
            y: Second variable

        Returns:
            AnalysisResult with correlation statistics

        Example:
            >>> positions = [1, 2, 3, 4, 5]
            >>> success_rates = [0.6, 0.5, 0.4, 0.3, 0.2]
            >>> result = analyzer.pearson_correlation(positions, success_rates)
        """
        if len(x) != len(y):
            raise ValueError("Variables must have equal length")

        if len(x) < 2:
            raise ValueError("Need at least 2 data points for correlation")

        # Calculate Pearson correlation
        r, p_value = stats.pearsonr(x, y)

        metrics = {
            "correlation": float(r),
            "p_value": float(p_value),
            "r_squared": float(r ** 2),
            "significant": p_value < (1 - self.confidence_level)
        }

        # Generate insights
        insights = []
        if metrics["significant"]:
            if abs(r) > 0.7:
                strength = "strong"
            elif abs(r) > 0.4:
                strength = "moderate"
            else:
                strength = "weak"

            direction = "positive" if r > 0 else "negative"
            insights.append(
                f"Found {strength} {direction} correlation "
                f"(r={r:.3f}, p={p_value:.4f})"
            )
        else:
            insights.append(f"No significant correlation found (p={p_value:.4f})")

        return AnalysisResult(
            analyzer_name=f"{self.name}::Correlation",
            metrics=metrics,
            insights=insights,
            confidence=self.confidence_level,
            metadata={"test_type": "pearson_correlation"}
        )

    def _compute_descriptive_stats(self, values: List[float]) -> Dict[str, float]:
        """Compute descriptive statistics."""
        if not values:
            return {}

        arr = np.array(values)
        ci = self._confidence_interval(values)

        return {
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr, ddof=1)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "q1": float(np.percentile(arr, 25)),
            "q3": float(np.percentile(arr, 75)),
            "ci_lower": ci[0],
            "ci_upper": ci[1],
            "n": len(values)
        }

    def _confidence_interval(
        self,
        values: List[float]
    ) -> Tuple[float, float]:
        """Calculate confidence interval for values."""
        if len(values) < 2:
            return (0.0, 0.0)

        ci = stats.t.interval(
            self.confidence_level,
            len(values) - 1,
            loc=np.mean(values),
            scale=stats.sem(values)
        )
        return (float(ci[0]), float(ci[1]))

    def _cohens_d(self, group1: List[float], group2: List[float]) -> float:
        """Calculate Cohen's d effect size."""
        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

        if pooled_std == 0:
            return 0.0

        return float((np.mean(group2) - np.mean(group1)) / pooled_std)

    def _generate_insights(self, metrics: Dict[str, float]) -> List[str]:
        """Generate human-readable insights from metrics."""
        insights = []

        if "mean" in metrics:
            insights.append(
                f"Mean success rate: {metrics['mean']:.3f} "
                f"(95% CI: [{metrics.get('ci_lower', 0):.3f}, "
                f"{metrics.get('ci_upper', 0):.3f}])"
            )

        if "std" in metrics:
            cv = metrics["std"] / metrics["mean"] if metrics["mean"] > 0 else 0
            if cv > 0.5:
                insights.append(
                    f"High variability detected (CV={cv:.2f}). "
                    f"Results may be unstable."
                )

        return insights
