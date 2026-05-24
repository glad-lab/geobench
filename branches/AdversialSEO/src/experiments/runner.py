"""
ExperimentRunner orchestration with pipeline management.

This module provides orchestration capabilities for running single or multiple
experiments with progress tracking, error handling, and result aggregation.

Design Patterns:
    - Builder Pattern: with_progress_tracking() for configuration
    - Observer Pattern: Progress callbacks for monitoring
    - Template Method: Inherited from BaseExperiment workflow
"""

from typing import List, Optional, Callable, Dict, Any
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging
import time
from datetime import datetime

from .base import BaseExperiment, ExperimentResult, ExperimentConfig, ExperimentType
from .factory import ExperimentFactory

logger = logging.getLogger(__name__)


class ExperimentRunner:
    """
    Orchestrates experiment execution with pipeline management.

    This runner manages single or multiple experiments, providing progress
    tracking, parallel execution, and comprehensive error handling.

    Features:
        - Sequential and parallel experiment execution
        - Progress tracking with Observer pattern
        - Result aggregation and persistence
        - Error handling and recovery
        - Resource management

    Design Patterns:
        - Builder Pattern: Method chaining for configuration
        - Observer Pattern: Progress callbacks for monitoring
        - Template Method: Uses BaseExperiment.run() workflow

    Example:
        >>> from experiments import ExperimentRunner, ExperimentFactory
        >>> from experiments.base import ExperimentConfig, ExperimentType
        >>>
        >>> config = ExperimentConfig(
        ...     experiment_type=ExperimentType.SINGLE_ATTACK,
        ...     num_trials=50
        ... )
        >>> experiment = ExperimentFactory().create(config.experiment_type, config)
        >>>
        >>> runner = (ExperimentRunner()
        ...     .add_experiment(experiment)
        ...     .with_progress_tracking(lambda name, pct: print(f"{name}: {pct:.0%}"))
        ... )
        >>> results = runner.run_all()
    """

    def __init__(self):
        """Initialize empty experiment runner."""
        self.experiments: List[BaseExperiment] = []
        self.results: List[ExperimentResult] = []
        self.progress_callback: Optional[Callable[[str, float], None]] = None
        self._factory = ExperimentFactory()

    def add_experiment(self, experiment: BaseExperiment) -> 'ExperimentRunner':
        """
        Add experiment to the runner (Builder pattern).

        Args:
            experiment: Configured experiment instance

        Returns:
            Self for method chaining

        Example:
            >>> runner = ExperimentRunner()
            >>> runner.add_experiment(experiment1).add_experiment(experiment2)
        """
        self.experiments.append(experiment)
        logger.info(f"Added experiment: {experiment.config.experiment_type.value}")
        return self

    def with_progress_tracking(
        self, callback: Callable[[str, float], None]
    ) -> 'ExperimentRunner':
        """
        Enable progress tracking (Builder + Observer pattern).

        The callback receives experiment name and completion percentage.

        Args:
            callback: Function(experiment_name: str, progress_pct: float) -> None

        Returns:
            Self for method chaining

        Example:
            >>> def track_progress(name, pct):
            ...     print(f"{name}: {pct:.1%} complete")
            >>> runner.with_progress_tracking(track_progress)
        """
        self.progress_callback = callback
        logger.info("Progress tracking enabled")
        return self

    def run_all(self, parallel: bool = False, max_workers: int = 4) -> List[ExperimentResult]:
        """
        Run all experiments sequentially or in parallel.

        Args:
            parallel: If True, use multiprocessing for parallel execution
            max_workers: Maximum number of parallel workers (if parallel=True)

        Returns:
            List of ExperimentResult objects, one per experiment

        Raises:
            Exception: If any experiment fails and cannot recover

        Example:
            >>> results = runner.run_all(parallel=True, max_workers=4)
            >>> for result in results:
            ...     print(f"{result.config.experiment_type}: {result.aggregate_metrics}")
        """
        if not self.experiments:
            logger.warning("No experiments to run")
            return []

        logger.info(f"Starting {len(self.experiments)} experiments (parallel={parallel})")
        start_time = time.time()

        if parallel:
            results = self._run_parallel(max_workers)
        else:
            results = self._run_sequential()

        duration = time.time() - start_time
        logger.info(
            f"Completed {len(results)}/{len(self.experiments)} experiments "
            f"in {duration:.1f}s"
        )

        self.results = results
        return results

    def _run_sequential(self) -> List[ExperimentResult]:
        """Run experiments sequentially with progress tracking."""
        results = []
        total = len(self.experiments)

        for idx, experiment in enumerate(self.experiments):
            try:
                exp_name = experiment.config.experiment_type.value
                logger.info(f"Running experiment {idx + 1}/{total}: {exp_name}")

                # Notify progress: starting
                if self.progress_callback:
                    self.progress_callback(exp_name, idx / total)

                # Run experiment
                result = experiment.run()
                results.append(result)

                # Notify progress: completed
                if self.progress_callback:
                    self.progress_callback(exp_name, (idx + 1) / total)

                logger.info(
                    f"Completed {exp_name}: "
                    f"{len(result.trials)} trials, "
                    f"metrics={result.aggregate_metrics}"
                )

            except Exception as e:
                logger.error(
                    f"Experiment {experiment.config.experiment_type.value} failed: {e}",
                    exc_info=True
                )
                # Continue with next experiment
                continue

        return results

    def _run_parallel(self, max_workers: int) -> List[ExperimentResult]:
        """
        Run experiments in parallel using ProcessPoolExecutor.

        Args:
            max_workers: Maximum number of parallel processes

        Returns:
            List of ExperimentResult objects
        """
        results = []

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all experiments
            future_to_exp = {
                executor.submit(self._run_experiment_safe, exp): exp
                for exp in self.experiments
            }

            # Collect results as they complete
            total = len(future_to_exp)
            for idx, future in enumerate(as_completed(future_to_exp)):
                experiment = future_to_exp[future]
                exp_name = experiment.config.experiment_type.value

                try:
                    result = future.result()
                    if result:
                        results.append(result)

                    # Notify progress
                    if self.progress_callback:
                        self.progress_callback(exp_name, (idx + 1) / total)

                    logger.info(f"Completed {exp_name}")

                except Exception as e:
                    logger.error(f"Parallel execution failed for {exp_name}: {e}")
                    continue

        return results

    @staticmethod
    def _run_experiment_safe(experiment: BaseExperiment) -> Optional[ExperimentResult]:
        """
        Safely run experiment with error handling.

        Used for parallel execution to ensure one failure doesn't crash all.

        Args:
            experiment: Experiment to run

        Returns:
            ExperimentResult if successful, None if failed
        """
        try:
            return experiment.run()
        except Exception as e:
            logger.error(
                f"Experiment {experiment.config.experiment_type.value} failed: {e}",
                exc_info=True
            )
            return None

    def run_single(self, experiment_name: str) -> Optional[ExperimentResult]:
        """
        Run single experiment by name.

        Args:
            experiment_name: Name matching ExperimentType.value

        Returns:
            ExperimentResult if found and executed, None otherwise

        Example:
            >>> runner.add_experiment(baseline_exp)
            >>> result = runner.run_single("baseline")
        """
        for experiment in self.experiments:
            if experiment.config.experiment_type.value == experiment_name:
                logger.info(f"Running single experiment: {experiment_name}")

                try:
                    result = experiment.run()
                    self.results.append(result)
                    return result
                except Exception as e:
                    logger.error(f"Experiment {experiment_name} failed: {e}", exc_info=True)
                    return None

        logger.warning(f"Experiment '{experiment_name}' not found")
        return None

    @classmethod
    def from_configs(
        cls, configs: List[ExperimentConfig]
    ) -> 'ExperimentRunner':
        """
        Create ExperimentRunner from list of configurations (Factory method).

        This automatically creates the appropriate experiment instances
        based on the configurations.

        Args:
            configs: List of experiment configurations

        Returns:
            Configured ExperimentRunner with all experiments added

        Example:
            >>> configs = [
            ...     ExperimentConfig(experiment_type=ExperimentType.BASELINE),
            ...     ExperimentConfig(experiment_type=ExperimentType.SINGLE_ATTACK)
            ... ]
            >>> runner = ExperimentRunner.from_configs(configs)
            >>> results = runner.run_all()
        """
        runner = cls()
        factory = ExperimentFactory()

        for config in configs:
            try:
                experiment = factory.create(config.experiment_type, config)
                runner.add_experiment(experiment)
            except Exception as e:
                logger.error(
                    f"Failed to create experiment {config.experiment_type.value}: {e}"
                )
                continue

        logger.info(f"Created runner with {len(runner.experiments)} experiments")
        return runner

    @classmethod
    def from_config(cls, config: ExperimentConfig) -> 'ExperimentRunner':
        """
        Create ExperimentRunner from single configuration.

        Args:
            config: Experiment configuration

        Returns:
            ExperimentRunner with single experiment

        Example:
            >>> config = ExperimentConfig(experiment_type=ExperimentType.BASELINE)
            >>> runner = ExperimentRunner.from_config(config)
            >>> result = runner.run_all()[0]
        """
        return cls.from_configs([config])

    def get_results(self) -> List[ExperimentResult]:
        """
        Get all experiment results collected so far.

        Returns:
            List of ExperimentResult objects
        """
        return self.results

    def clear_results(self) -> 'ExperimentRunner':
        """
        Clear all stored results.

        Returns:
            Self for method chaining
        """
        self.results = []
        logger.info("Cleared experiment results")
        return self

    def save_results(self, output_dir: str) -> None:
        """
        Save all results to disk.

        Args:
            output_dir: Directory to save results

        Example:
            >>> runner.run_all()
            >>> runner.save_results("data/results")
        """
        import json
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for idx, result in enumerate(self.results):
            exp_type = result.config.experiment_type.value
            filename = f"{exp_type}_{timestamp}_{idx}.json"
            filepath = output_path / filename

            # Convert to serializable dict
            result_dict = {
                "config": {
                    "experiment_type": result.config.experiment_type.value,
                    "num_trials": result.config.num_trials,
                    "num_products": result.config.num_products,
                    "query": result.config.query,
                    "model": result.config.model,
                    "provider": result.config.provider,
                },
                "aggregate_metrics": result.aggregate_metrics,
                "metadata": result.metadata,
                "timestamp": result.timestamp,
                "num_trials": len(result.trials),
            }

            with open(filepath, 'w') as f:
                json.dump(result_dict, f, indent=2)

            logger.info(f"Saved result to {filepath}")
