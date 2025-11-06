"""
Base classes for analysis components.

This module provides abstract base classes and data structures for the analysis package.

Design Patterns:
    - Strategy Pattern: BaseAnalyzer defines interchangeable analysis algorithms
    - Data Class: AnalysisResult provides immutable result container
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class AnalysisResult:
    """
    Result of analysis operation.

    Immutable container for analysis outputs including computed metrics,
    visualizations, insights, and confidence scores.

    Attributes:
        analyzer_name: Name of analyzer that produced this result
        metrics: Computed numerical metrics
        visualizations: Visualization data (plots, charts, etc.)
        insights: Human-readable insights and interpretations
        confidence: Confidence score for the analysis (0-1)
        metadata: Additional metadata about the analysis

    Example:
        >>> result = AnalysisResult(
        ...     analyzer_name="StatisticalAnalyzer",
        ...     metrics={"mean": 0.38, "std": 0.15, "p_value": 0.001},
        ...     visualizations={"histogram": plot_data},
        ...     insights=["Statistically significant effect detected"],
        ...     confidence=0.95
        ... )
    """

    analyzer_name: str
    metrics: Dict[str, float]
    visualizations: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAnalyzer(ABC):
    """
    Abstract base for analyzers (Strategy pattern).

    Analyzers transform experimental results into actionable insights
    and visualizations. Each analyzer implements a specific analysis
    strategy that can be composed with others.

    The analyze() method is the core algorithm that subclasses must
    implement. It takes raw data and returns structured AnalysisResult.

    Example:
        >>> class MyAnalyzer(BaseAnalyzer):
        ...     def analyze(self, data):
        ...         metrics = self._compute_metrics(data)
        ...         return AnalysisResult(
        ...             analyzer_name=self.name,
        ...             metrics=metrics
        ...         )
        >>>
        >>> analyzer = MyAnalyzer()
        >>> result = analyzer.analyze(experiment_data)
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize analyzer with optional name.

        Args:
            name: Human-readable name for this analyzer.
                 Defaults to class name if not provided.
        """
        self.name = name or self.__class__.__name__

    @abstractmethod
    def analyze(self, data: List[Dict[str, Any]]) -> AnalysisResult:
        """
        Analyze data and return results.

        This is the core method that subclasses must implement.
        It defines the analysis strategy for transforming raw
        experimental data into insights.

        Args:
            data: Raw experimental data as list of dictionaries.
                 Each dict typically contains trial results with
                 metrics, rankings, and metadata.

        Returns:
            AnalysisResult with computed metrics and insights

        Raises:
            ValueError: If data format is invalid or insufficient
            AnalysisError: If analysis computation fails

        Example:
            >>> data = [
            ...     {"metrics": {"success": 1.0, "position": 1}},
            ...     {"metrics": {"success": 0.0, "position": 3}}
            ... ]
            >>> result = analyzer.analyze(data)
        """
        pass

    def _validate_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Validate input data format and content.

        Performs basic validation to ensure data is suitable for analysis.
        Subclasses can override to add specific validation logic.

        Args:
            data: Raw data to validate

        Raises:
            ValueError: If data is invalid
        """
        if not data:
            raise ValueError("Cannot analyze empty data")

        if not isinstance(data, list):
            raise ValueError("Data must be a list of dictionaries")

        if not all(isinstance(item, dict) for item in data):
            raise ValueError("All data items must be dictionaries")
