"""
Analysis package for adversarial SEO research.

This package provides comprehensive statistical and comparative analysis
of experimental results, including:
    - Statistical testing (t-tests, ANOVA, chi-square, correlation)
    - Cross-provider and cross-attack-type comparisons
    - Attack effectiveness analysis (positional bias, trends)
    - Multi-analyzer orchestration

Design Patterns:
    - Strategy Pattern: Interchangeable analyzers
    - Composite Pattern: AnalysisEngine orchestrates multiple analyzers
    - Factory Pattern: Centralized analyzer creation
    - Builder Pattern: Fluent interface for engine configuration

Example - Basic Analysis:
    >>> from analysis import StatisticalAnalyzer
    >>>
    >>> # Create analyzer
    >>> analyzer = StatisticalAnalyzer(confidence_level=0.95)
    >>>
    >>> # Analyze experimental data
    >>> result = analyzer.analyze(experiment_data)
    >>> print(f"Mean success: {result.metrics['mean']}")
    >>> for insight in result.insights:
    ...     print(insight)

Example - Statistical Testing:
    >>> from analysis import StatisticalAnalyzer
    >>>
    >>> analyzer = StatisticalAnalyzer()
    >>> baseline = [0.2, 0.3, 0.25, 0.28]
    >>> treatment = [0.5, 0.6, 0.55, 0.58]
    >>>
    >>> # Perform t-test
    >>> result = analyzer.t_test(baseline, treatment)
    >>> if result.metrics['significant']:
    ...     print(f"Significant difference found (p={result.metrics['p_value']})")
    ...     print(f"Effect size: {result.metrics['cohens_d']}")

Example - Comparative Analysis:
    >>> from analysis import ComparativeAnalyzer
    >>>
    >>> analyzer = ComparativeAnalyzer()
    >>>
    >>> # Compare across LLM providers
    >>> result = analyzer.compare_providers(data)
    >>> print(f"Best provider: {result.metrics['best_provider']}")
    >>>
    >>> # Compare across attack types
    >>> result = analyzer.compare_attack_types(data)
    >>> print(f"Most effective: {result.metrics['most_effective_attack']}")

Example - Multi-Analyzer Workflow:
    >>> from analysis import AnalysisEngine, AnalyzerFactory
    >>>
    >>> # Create engine with multiple analyzers
    >>> engine = AnalysisEngine()
    >>> engine.add_analyzer(AnalyzerFactory.create("statistical", confidence_level=0.95))
    >>> engine.add_analyzer(AnalyzerFactory.create("comparative"))
    >>> engine.add_analyzer(AnalyzerFactory.create("effectiveness"))
    >>>
    >>> # Run all analyzers
    >>> results = engine.run_analysis(experiment_data)
    >>>
    >>> # Aggregate results
    >>> summary = engine.aggregate_results(results)
    >>> print(f"Total insights: {summary['total_insights']}")
    >>> for insight in summary['insights']:
    ...     print(insight)

Example - Factory Pattern:
    >>> from analysis import AnalyzerFactory
    >>>
    >>> # Create specific analyzer
    >>> analyzer = AnalyzerFactory.create("statistical", confidence_level=0.99)
    >>>
    >>> # Create all analyzers at once
    >>> analyzers = AnalyzerFactory.create_all(confidence_level=0.95)
    >>>
    >>> # Create from configuration
    >>> config = {
    ...     "statistical": {"confidence_level": 0.99},
    ...     "comparative": {},
    ...     "effectiveness": {}
    ... }
    >>> analyzers = AnalyzerFactory.create_from_config(config)

Example - Effectiveness Analysis:
    >>> from analysis import EffectivenessAnalyzer
    >>>
    >>> analyzer = EffectivenessAnalyzer()
    >>>
    >>> # Positional bias analysis
    >>> result = analyzer.positional_bias_analysis(data)
    >>> print(f"End relative effectiveness: {result.metrics['end_relative_effectiveness']}")
    >>>
    >>> # Query type analysis
    >>> result = analyzer.success_by_query_type(data)
    >>> print(f"Most effective query type: {result.metrics['most_effective_query_type']}")
    >>>
    >>> # Trend analysis
    >>> result = analyzer.success_trend_analysis(data)
    >>> print(f"Trend slope: {result.metrics['trend_slope']}")

Classes:
    BaseAnalyzer: Abstract base for all analyzers
    AnalysisResult: Immutable result container
    StatisticalAnalyzer: Statistical tests and descriptive statistics
    ComparativeAnalyzer: Cross-provider and cross-attack comparisons
    EffectivenessAnalyzer: Position-based and trend analysis
    AnalysisEngine: Multi-analyzer orchestration
    AnalyzerFactory: Analyzer instance creation
"""

from .base import BaseAnalyzer, AnalysisResult
from .statistical import StatisticalAnalyzer
from .comparative import ComparativeAnalyzer
from .effectiveness import EffectivenessAnalyzer
from .engine import AnalysisEngine
from .factory import AnalyzerFactory

__all__ = [
    # Base classes
    "BaseAnalyzer",
    "AnalysisResult",
    # Analyzers
    "StatisticalAnalyzer",
    "ComparativeAnalyzer",
    "EffectivenessAnalyzer",
    # Orchestration
    "AnalysisEngine",
    "AnalyzerFactory",
]

__version__ = "1.0.0"
