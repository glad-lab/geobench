"""
Example usage of the experiments package.

This demonstrates the key features and design patterns:
- Builder pattern for configuration
- Factory pattern for experiment creation
- Observer pattern for progress tracking
- Command pattern for different experiment types
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")

from src.experiments import (
    ExperimentRunner,
    ExperimentFactory,
    ExperimentConfigBuilder,
    ExperimentType,
    ResultAggregator,
    ResultComparator,
    create_preset_config,
)
from src.attacks import AttackType


def example_1_basic_usage():
    """Example 1: Basic experiment execution."""
    print("=" * 60)
    print("Example 1: Basic Single Attack Experiment")
    print("=" * 60)

    # Build configuration using Builder pattern
    config = (ExperimentConfigBuilder()
        .with_experiment_type(ExperimentType.SINGLE_ATTACK)
        .with_trials(10)
        .with_products(4)
        .with_attack_types([AttackType.PROMPT_INJECTION])
        .with_query("best camera for photography")
        .with_model("openai", "gpt-3.5-turbo")
        .with_random_seed(42)
        .with_rate_limit(0.5)
        .build()
    )

    # Create experiment using Factory pattern
    factory = ExperimentFactory()
    experiment = factory.create(config.experiment_type, config)

    # Run experiment
    result = experiment.run()

    # Display results
    print(f"\nExperiment: {result.config.experiment_type.value}")
    print(f"Trials: {len(result.trials)}")
    print(f"Metrics: {result.aggregate_metrics}")


def example_2_progress_tracking():
    """Example 2: Progress tracking with Observer pattern."""
    print("\n" + "=" * 60)
    print("Example 2: Progress Tracking")
    print("=" * 60)

    def progress_callback(name, pct):
        """Observer callback for progress updates."""
        print(f"Progress: {name} - {pct:.0%} complete")

    # Create configuration
    config = create_preset_config("single_attack")

    # Create experiment
    factory = ExperimentFactory()
    experiment = factory.create(config.experiment_type, config)

    # Run with progress tracking
    runner = (ExperimentRunner()
        .add_experiment(experiment)
        .with_progress_tracking(progress_callback)
    )

    results = runner.run_all()
    print(f"\nCompleted {len(results)} experiments")


def example_3_multiple_experiments():
    """Example 3: Running multiple experiments."""
    print("\n" + "=" * 60)
    print("Example 3: Multiple Experiments")
    print("=" * 60)

    # Create configs for different experiment types
    configs = [
        ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.BASELINE)
            .with_trials(5)
            .build(),

        ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.SINGLE_ATTACK)
            .with_trials(5)
            .with_attack_types([AttackType.PROMPT_INJECTION])
            .build(),

        ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.POSITIONAL_BIAS)
            .with_trials(6)  # 2 per position
            .build(),
    ]

    # Create runner from configs
    runner = ExperimentRunner.from_configs(configs)

    # Run all experiments sequentially
    results = runner.run_all(parallel=False)

    print(f"\nCompleted {len(results)} experiments:")
    for result in results:
        print(f"  - {result.config.experiment_type.value}: "
              f"{len(result.trials)} trials")


def example_4_result_aggregation():
    """Example 4: Aggregating and comparing results."""
    print("\n" + "=" * 60)
    print("Example 4: Result Aggregation")
    print("=" * 60)

    # Create and run experiments
    configs = [
        ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.BASELINE)
            .with_trials(5)
            .build(),

        ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.SINGLE_ATTACK)
            .with_trials(5)
            .with_attack_types([AttackType.PROMPT_INJECTION])
            .build(),
    ]

    runner = ExperimentRunner.from_configs(configs)
    results = runner.run_all()

    # Aggregate results
    aggregator = ResultAggregator()
    aggregator.add_results(results)

    # Get aggregate metrics
    metrics = aggregator.aggregate_metrics()
    print("\nAggregate Metrics:")
    for exp_type, exp_metrics in metrics.items():
        if exp_type != "overall":
            print(f"\n{exp_type}:")
            for key, value in exp_metrics.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")

    # Save results
    aggregator.to_json("data/results/aggregated_results.json")
    print("\nResults saved to data/results/aggregated_results.json")


def example_5_result_comparison():
    """Example 5: Comparing experiment results."""
    print("\n" + "=" * 60)
    print("Example 5: Result Comparison")
    print("=" * 60)

    # Create baseline and attack experiments
    baseline_config = create_preset_config("baseline")
    attack_config = create_preset_config("single_attack")

    factory = ExperimentFactory()

    baseline_exp = factory.create(baseline_config.experiment_type, baseline_config)
    attack_exp = factory.create(attack_config.experiment_type, attack_config)

    # Run experiments
    baseline_result = baseline_exp.run()
    attack_result = attack_exp.run()

    # Compare results
    comparison = ResultComparator.compare(baseline_result, attack_result)

    print("\nComparison:")
    for key, value in comparison.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")


def example_6_custom_experiment():
    """Example 6: Registering custom experiment type."""
    print("\n" + "=" * 60)
    print("Example 6: Custom Experiment")
    print("=" * 60)

    from src.experiments.base import BaseExperiment
    import numpy as np

    class CustomExperiment(BaseExperiment):
        """Custom experiment implementation."""

        def setup(self):
            print("Setting up custom experiment...")

        def execute(self):
            from src.experiments.base import TrialResult
            from datetime import datetime

            print("Executing custom logic...")
            trials = []

            for i in range(self.config.num_trials):
                trial = TrialResult(
                    trial_id=i,
                    experiment_type=self.config.experiment_type,
                    baseline_ranking=None,
                    attacked_ranking=None,
                    attack_info={"custom": True},
                    metrics={"custom_metric": np.random.random()},
                    timestamp=datetime.now().isoformat(),
                    duration=0.1
                )
                trials.append(trial)

            return trials

        def analyze(self, results):
            metrics = [r.metrics["custom_metric"] for r in results]
            return {
                "custom_mean": np.mean(metrics),
                "custom_std": np.std(metrics),
            }

    # Register custom experiment
    ExperimentFactory.register(
        ExperimentType.BASELINE,  # Using existing enum for demo
        CustomExperiment
    )

    # Create and run custom experiment
    config = ExperimentConfigBuilder().with_trials(5).build()
    factory = ExperimentFactory()
    experiment = factory.create(ExperimentType.BASELINE, config)

    result = experiment.run()

    print(f"\nCustom experiment completed:")
    print(f"  Trials: {len(result.trials)}")
    print(f"  Metrics: {result.aggregate_metrics}")


def example_7_preset_configs():
    """Example 7: Using preset configurations."""
    print("\n" + "=" * 60)
    print("Example 7: Preset Configurations")
    print("=" * 60)

    presets = [
        "baseline",
        "single_attack",
        "prisoners_dilemma",
        "positional_bias",
        "quick_test"
    ]

    print("Available presets:")
    for preset_name in presets:
        config = create_preset_config(preset_name)
        if config:
            print(f"  - {preset_name}: {config.num_trials} trials, "
                  f"{config.num_products} products")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("EXPERIMENTS PACKAGE USAGE EXAMPLES")
    print("=" * 60)

    examples = [
        example_1_basic_usage,
        example_2_progress_tracking,
        example_3_multiple_experiments,
        example_4_result_aggregation,
        example_5_result_comparison,
        example_6_custom_experiment,
        example_7_preset_configs,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nExample failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
