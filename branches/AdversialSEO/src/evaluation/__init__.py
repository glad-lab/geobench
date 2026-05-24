"""Evaluation package for measuring experiment effectiveness.

This package provides evaluators and metrics for assessing attack
effectiveness, comparing results to paper findings, and computing
various ranking quality metrics.

Example:
    >>> from src.evaluation import AttackEffectivenessEvaluator
    >>> evaluator = AttackEffectivenessEvaluator()
    >>> result = evaluator.evaluate(experiment_results)
    >>> print(f"Success rate: {result.metrics['success_rate']}")
"""

from .base import BaseEvaluator, EvaluationResult
from .metrics import MetricCalculator
from .evaluators import (
    AttackEffectivenessEvaluator,
    PaperComparisonEvaluator,
    RankingQualityEvaluator,
)
from .aggregators import ResultAggregator, MetricAggregator

# Backward compatibility aliases (deprecated)
EvaluationMetrics = MetricCalculator
MetricResult = EvaluationResult

__all__ = [
    # Package API
    'BaseEvaluator',
    'EvaluationResult',
    'MetricCalculator',
    'AttackEffectivenessEvaluator',
    'PaperComparisonEvaluator',
    'RankingQualityEvaluator',
    'ResultAggregator',
    'MetricAggregator',
    # Backward compatibility (deprecated)
    'EvaluationMetrics',
    'MetricResult',
]
