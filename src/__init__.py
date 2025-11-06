"""
Adversarial SEO for LLMs Research Project
Reproduction study of Nestaas et al., 2024
"""

__version__ = "0.1.0"
__author__ = "Freddy Song"

from .attacks import AttackFactory, AttackGenerator, AttackType, Attack
from .ranking import LLMRanker, SimpleRAG
from .vector_store import VectorStoreManager
from .experiments import ExperimentRunner
from .evaluation import MetricCalculator, AttackEffectivenessEvaluator

# Backward compatibility alias
EvaluationMetrics = MetricCalculator

__all__ = [
    "AttackFactory",
    "AttackGenerator",
    "AttackType",
    "Attack",
    "LLMRanker",
    "SimpleRAG",
    "VectorStoreManager",
    "ExperimentRunner",
    "MetricCalculator",
    "AttackEffectivenessEvaluator",
    "EvaluationMetrics",  # Deprecated, use MetricCalculator
]