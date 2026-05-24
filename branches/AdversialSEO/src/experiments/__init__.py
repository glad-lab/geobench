"""
Experiment orchestration package for adversarial SEO research.

This package provides a modular framework for running controlled experiments
on LLM-powered ranking systems, implementing the methodology from
Nestaas et al., 2024.

Design Patterns:
    - Command Pattern: Different experiment types as command objects
    - Template Method: BaseExperiment with customizable steps
    - Factory Pattern: Experiment creation and configuration
    - Builder Pattern: ExperimentConfig construction
    - Observer Pattern: Progress tracking and notifications

Example:
    >>> from experiments import ExperimentRunner, ExperimentConfig, ExperimentType
    >>>
    >>> config = ExperimentConfig(
    ...     experiment_type=ExperimentType.SINGLE_ATTACK,
    ...     num_trials=50,
    ...     attack_types=[AttackType.PROMPT_INJECTION]
    ... )
    >>>
    >>> result = ExperimentRunner.run_experiment(config)
    >>> print(f"Success rate: {result.aggregate_metrics['success_mean']:.2%}")
"""

from .base import (
    BaseExperiment,
    ExperimentConfig,
    ExperimentResult,
    TrialResult,
    ExperimentType,
)
from .runner import ExperimentRunner
from .commands import (
    BaselineExperiment,
    SingleAttackExperiment,
    PrisonersDilemmaExperiment,
    ExternalAttackExperiment,
    PositionalBiasExperiment,
)
from .factory import ExperimentFactory
from .configs import ExperimentConfigBuilder, create_preset_config
from .results import ResultAggregator, ResultComparator

# Backward compatibility - export everything from old module
__all__ = [
    # Core classes
    "BaseExperiment",
    "ExperimentRunner",
    "ExperimentFactory",

    # Data classes
    "ExperimentConfig",
    "ExperimentResult",
    "TrialResult",
    "ExperimentType",

    # Command implementations
    "BaselineExperiment",
    "SingleAttackExperiment",
    "PrisonersDilemmaExperiment",
    "ExternalAttackExperiment",
    "PositionalBiasExperiment",

    # Builders and configuration
    "ExperimentConfigBuilder",
    "create_preset_config",

    # Results
    "ResultAggregator",
    "ResultComparator",
]
