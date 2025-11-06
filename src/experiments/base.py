"""
Base classes and data structures for experiment orchestration.

This module defines the abstract base class for experiments and core data structures
used throughout the experiment package.

Design Patterns:
    - Template Method: BaseExperiment.run() defines algorithm skeleton
    - Data Class: Immutable configuration and result objects
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime


class ExperimentType(Enum):
    """Types of experiments available in the framework."""

    BASELINE = "baseline"
    SINGLE_ATTACK = "single_attack"
    PRISONERS_DILEMMA = "prisoners_dilemma"
    EXTERNAL_ATTACK = "external_attack"
    POSITIONAL_BIAS = "positional_bias"


@dataclass
class ExperimentConfig:
    """
    Configuration for experiment execution.

    This immutable configuration object captures all parameters needed
    to run a reproducible experiment.

    Attributes:
        experiment_type: Type of experiment to run
        num_trials: Number of trials to execute
        num_products: Number of products in test catalog
        attack_types: List of attack types to test
        num_attackers: Number of attackers (for multi-attacker scenarios)
        query: Search query to use
        save_results: Whether to persist results to disk
        output_dir: Directory for result files
        random_seed: Random seed for reproducibility
        use_rag: Whether to use RAG-based ranking
        model: LLM model identifier
        provider: LLM provider name
        rate_limit_delay: Delay between API calls (seconds)
        batch_size: Number of trials to batch together

    Example:
        >>> config = ExperimentConfig(
        ...     experiment_type=ExperimentType.SINGLE_ATTACK,
        ...     num_trials=50,
        ...     random_seed=42
        ... )
    """

    experiment_type: ExperimentType
    num_trials: int = 50
    num_products: int = 4
    attack_types: List[Any] = field(default_factory=list)  # AttackType from attacks package
    num_attackers: int = 0
    query: str = "best camera for photography"
    save_results: bool = True
    output_dir: str = "data/results"
    random_seed: Optional[int] = None
    use_rag: bool = True
    model: Optional[str] = None
    provider: Optional[str] = None
    rate_limit_delay: float = 1.0
    batch_size: int = 10


@dataclass
class TrialResult:
    """
    Result from a single experimental trial.

    Captures all data from one trial execution including rankings,
    attack information, and computed metrics.

    Attributes:
        trial_id: Unique identifier for this trial
        experiment_type: Type of experiment this trial belongs to
        baseline_ranking: Ranking without attack (if applicable)
        attacked_ranking: Ranking with attack applied
        attack_info: Metadata about the attack used
        metrics: Computed evaluation metrics
        timestamp: ISO format timestamp
        duration: Trial execution time in seconds

    Example:
        >>> trial = TrialResult(
        ...     trial_id=0,
        ...     experiment_type=ExperimentType.SINGLE_ATTACK,
        ...     baseline_ranking=baseline,
        ...     attacked_ranking=attacked,
        ...     attack_info={"type": "prompt_injection"},
        ...     metrics={"success": 1.0},
        ...     timestamp=datetime.now().isoformat(),
        ...     duration=2.5
        ... )
    """

    trial_id: int
    experiment_type: ExperimentType
    baseline_ranking: Optional[Any]  # RankingResult from ranking package
    attacked_ranking: Any  # RankingResult from ranking package
    attack_info: Optional[Dict[str, Any]]
    metrics: Dict[str, float]
    timestamp: str
    duration: float


@dataclass
class ExperimentResult:
    """
    Complete result from an experiment execution.

    Aggregates all trial results and computed aggregate metrics.

    Attributes:
        config: Configuration used for this experiment
        trials: List of individual trial results
        aggregate_metrics: Aggregated statistics across all trials
        metadata: Additional experiment metadata
        timestamp: ISO format timestamp

    Example:
        >>> result = ExperimentResult(
        ...     config=config,
        ...     trials=trials,
        ...     aggregate_metrics={"success_mean": 0.38},
        ...     metadata={"duration": 125.3},
        ...     timestamp=datetime.now().isoformat()
        ... )
    """

    config: ExperimentConfig
    trials: List[TrialResult]
    aggregate_metrics: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str


class BaseExperiment(ABC):
    """
    Abstract base class for all experiment types.

    Implements the Template Method pattern where run() defines the
    algorithm skeleton and subclasses implement specific steps.

    The standard experiment workflow is:
        1. setup() - Initialize resources
        2. execute() - Run trials and collect results
        3. analyze() - Compute metrics from results
        4. finalize() - Package results
        5. cleanup() - Release resources

    Subclasses must implement setup(), execute(), and analyze().
    The run() method orchestrates the workflow.

    Attributes:
        config: Experiment configuration

    Example:
        >>> class MyExperiment(BaseExperiment):
        ...     def setup(self):
        ...         self.products = generate_products()
        ...
        ...     def execute(self):
        ...         return [run_trial() for _ in range(self.config.num_trials)]
        ...
        ...     def analyze(self, results):
        ...         return {"success_rate": compute_success(results)}
        >>>
        >>> experiment = MyExperiment(config)
        >>> result = experiment.run()
    """

    def __init__(self, config: ExperimentConfig):
        """
        Initialize the experiment with configuration.

        Args:
            config: Experiment configuration object
        """
        self.config = config

    def run(self) -> ExperimentResult:
        """
        Execute the complete experiment workflow.

        This is the Template Method that defines the algorithm skeleton.
        It ensures proper resource management via try/finally.

        Returns:
            ExperimentResult containing all trial data and metrics

        Raises:
            Exception: Any exception from setup/execute/analyze phases
        """
        self.setup()
        try:
            results = self.execute()
            metrics = self.analyze(results)
            return self.finalize(results, metrics)
        finally:
            self.cleanup()

    @abstractmethod
    def setup(self) -> None:
        """
        Setup experiment resources.

        This method is called before execution begins. Use it to:
            - Initialize ranking systems
            - Generate test products
            - Configure attack generators
            - Prepare vector databases

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def execute(self) -> List[TrialResult]:
        """
        Execute experiment trials and collect results.

        This is the core experiment logic that runs multiple trials
        and collects their results.

        Returns:
            List of TrialResult objects, one per trial

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def analyze(self, results: List[TrialResult]) -> Dict[str, float]:
        """
        Analyze trial results and compute aggregate metrics.

        Takes the raw trial results and computes summary statistics
        and aggregate metrics for the experiment.

        Args:
            results: List of trial results from execute()

        Returns:
            Dictionary of aggregate metrics (means, stds, etc.)

        Must be implemented by subclasses.
        """
        pass

    def finalize(
        self, results: List[TrialResult], metrics: Dict[str, float]
    ) -> ExperimentResult:
        """
        Package results into final ExperimentResult object.

        This default implementation creates a standard ExperimentResult.
        Subclasses can override to add custom metadata.

        Args:
            results: Trial results from execute()
            metrics: Aggregate metrics from analyze()

        Returns:
            Complete ExperimentResult object
        """
        return ExperimentResult(
            config=self.config,
            trials=results,
            aggregate_metrics=metrics,
            metadata={
                "num_trials": len(results),
                "model": self.config.model,
                "provider": self.config.provider,
            },
            timestamp=datetime.now().isoformat(),
        )

    def cleanup(self) -> None:
        """
        Clean up experiment resources.

        This method is guaranteed to be called even if execute() or
        analyze() raises an exception. Use it to:
            - Close database connections
            - Clear temporary data
            - Release system resources

        Default implementation does nothing. Override if needed.
        """
        pass
