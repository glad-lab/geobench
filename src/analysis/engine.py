"""
Analysis engine with pluggable analyzers (Composite pattern).

This module orchestrates multiple analyzers to run comprehensive analysis
on experimental data.
"""

from typing import List, Dict, Any
import logging

from .base import BaseAnalyzer, AnalysisResult

logger = logging.getLogger(__name__)


class AnalysisEngine:
    """
    Orchestrates multiple analyzers (Composite pattern).

    Allows combining multiple analysis strategies for comprehensive
    results. Implements Builder pattern for fluent configuration.

    The engine runs all registered analyzers on the provided data
    and aggregates their results.

    Attributes:
        analyzers: List of registered analyzers

    Example:
        >>> from analysis import AnalysisEngine, StatisticalAnalyzer, ComparativeAnalyzer
        >>> engine = AnalysisEngine()
        >>> engine.add_analyzer(StatisticalAnalyzer())
        >>> engine.add_analyzer(ComparativeAnalyzer())
        >>> results = engine.run_analysis(data)
        >>> for result in results:
        ...     print(f"{result.analyzer_name}: {result.metrics}")
    """

    def __init__(self):
        """Initialize empty analysis engine."""
        self.analyzers: List[BaseAnalyzer] = []

    def add_analyzer(self, analyzer: BaseAnalyzer) -> 'AnalysisEngine':
        """
        Add analyzer to the engine (Builder pattern).

        Args:
            analyzer: Analyzer instance to add

        Returns:
            Self for method chaining

        Example:
            >>> engine = AnalysisEngine()
            >>> engine.add_analyzer(StatisticalAnalyzer()) \\
            ...       .add_analyzer(ComparativeAnalyzer()) \\
            ...       .add_analyzer(EffectivenessAnalyzer())
        """
        if not isinstance(analyzer, BaseAnalyzer):
            raise TypeError(
                f"Analyzer must be instance of BaseAnalyzer, got {type(analyzer)}"
            )

        self.analyzers.append(analyzer)
        logger.debug(f"Added analyzer: {analyzer.name}")
        return self

    def run_analysis(
        self,
        data: List[Dict[str, Any]]
    ) -> List[AnalysisResult]:
        """
        Run all analyzers on data.

        Executes each registered analyzer in sequence and collects
        their results. Continues execution even if one analyzer fails,
        logging errors for failed analyzers.

        Args:
            data: Raw experimental data

        Returns:
            List of AnalysisResult from each successful analyzer

        Raises:
            ValueError: If no analyzers are registered or data is empty

        Example:
            >>> results = engine.run_analysis(experiment_data)
            >>> for result in results:
            ...     print(f"Analyzer: {result.analyzer_name}")
            ...     print(f"Metrics: {result.metrics}")
            ...     print(f"Insights: {result.insights}")
        """
        if not self.analyzers:
            raise ValueError("No analyzers registered. Use add_analyzer() first.")

        if not data:
            raise ValueError("Cannot analyze empty data")

        logger.info(f"Running {len(self.analyzers)} analyzers on {len(data)} data points")

        results = []
        for analyzer in self.analyzers:
            try:
                logger.debug(f"Running analyzer: {analyzer.name}")
                result = analyzer.analyze(data)
                results.append(result)
                logger.debug(
                    f"Analyzer {analyzer.name} completed. "
                    f"Metrics: {len(result.metrics)}, Insights: {len(result.insights)}"
                )
            except Exception as e:
                logger.error(
                    f"Analyzer {analyzer.name} failed with error: {str(e)}",
                    exc_info=True
                )
                # Continue with other analyzers
                continue

        if not results:
            logger.warning("All analyzers failed to produce results")

        return results

    def aggregate_results(
        self,
        results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """
        Aggregate results from multiple analyzers.

        Combines metrics and insights from all analyzers into a
        single comprehensive report.

        Args:
            results: List of AnalysisResult from run_analysis()

        Returns:
            Dictionary with aggregated metrics and insights

        Example:
            >>> results = engine.run_analysis(data)
            >>> summary = engine.aggregate_results(results)
            >>> print(summary["all_insights"])
        """
        if not results:
            return {
                "metrics": {},
                "insights": [],
                "analyzers_run": 0,
                "total_metrics": 0
            }

        # Collect all metrics
        all_metrics = {}
        for result in results:
            # Prefix metrics with analyzer name to avoid collisions
            prefix = result.analyzer_name.split("::")[-1]  # Get last part of name
            for key, value in result.metrics.items():
                all_metrics[f"{prefix}_{key}"] = value

        # Collect all insights
        all_insights = []
        for result in results:
            for insight in result.insights:
                all_insights.append(f"[{result.analyzer_name}] {insight}")

        # Aggregate metadata
        aggregated = {
            "metrics": all_metrics,
            "insights": all_insights,
            "analyzers_run": len(results),
            "total_metrics": sum(len(r.metrics) for r in results),
            "total_insights": len(all_insights),
            "analyzer_names": [r.analyzer_name for r in results]
        }

        return aggregated

    def clear_analyzers(self) -> 'AnalysisEngine':
        """
        Remove all registered analyzers.

        Returns:
            Self for method chaining

        Example:
            >>> engine.clear_analyzers().add_analyzer(new_analyzer)
        """
        self.analyzers = []
        logger.debug("Cleared all analyzers")
        return self

    def __len__(self) -> int:
        """Return number of registered analyzers."""
        return len(self.analyzers)

    def __repr__(self) -> str:
        """String representation of engine."""
        analyzer_names = [a.name for a in self.analyzers]
        return f"AnalysisEngine(analyzers={analyzer_names})"
