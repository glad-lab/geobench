"""
Example demonstrating the analysis package workflow.

This example shows how to use the analysis package to perform
comprehensive statistical and comparative analysis of experimental results.
"""

import numpy as np
from src.analysis import (
    StatisticalAnalyzer,
    ComparativeAnalyzer,
    EffectivenessAnalyzer,
    AnalysisEngine,
    AnalyzerFactory,
)


def generate_sample_data():
    """Generate sample experimental data for demonstration."""
    np.random.seed(42)

    data = []
    providers = ["openai", "anthropic", "bedrock"]
    attack_types = ["prompt_injection", "persuasion", "discreditation"]
    positions = ["start", "middle", "end"]

    for trial_id in range(50):
        # Simulate varying success rates
        provider = np.random.choice(providers)
        attack_type = np.random.choice(attack_types)
        position = np.random.choice(positions)

        # Different success rates for different conditions
        base_success = 0.3
        if attack_type == "prompt_injection":
            base_success = 0.5
        elif attack_type == "persuasion":
            base_success = 0.4

        if position == "end":
            base_success *= 1.3  # Positional bias

        success = min(1.0, max(0.0, base_success + np.random.normal(0, 0.1)))

        data.append({
            "trial_id": trial_id,
            "metrics": {
                "success": success,
                "position_change": int(success * 3),
                "final_position": 1 if success > 0.7 else (2 if success > 0.4 else 3)
            },
            "metadata": {
                "provider": provider,
                "query_type": "recommendation"
            },
            "attack_info": {
                "attack_type": attack_type,
                "position": position
            }
        })

    return data


def example_statistical_analysis():
    """Demonstrate statistical analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Statistical Analysis")
    print("=" * 70)

    # Generate baseline and treatment data
    np.random.seed(42)
    baseline = [float(np.random.normal(0.3, 0.1)) for _ in range(30)]
    treatment = [float(np.random.normal(0.6, 0.1)) for _ in range(30)]

    # Create analyzer
    analyzer = StatisticalAnalyzer(confidence_level=0.95)

    # Perform t-test
    result = analyzer.t_test(baseline, treatment)

    print(f"\nT-Test Results:")
    print(f"  Baseline mean: {result.metrics['group1_mean']:.3f}")
    print(f"  Treatment mean: {result.metrics['group2_mean']:.3f}")
    print(f"  t-statistic: {result.metrics['t_statistic']:.3f}")
    print(f"  p-value: {result.metrics['p_value']:.4f}")
    print(f"  Cohen's d: {result.metrics['cohens_d']:.3f}")
    print(f"  Significant: {result.metrics['significant']}")

    print(f"\nInsights:")
    for insight in result.insights:
        print(f"  - {insight}")


def example_comparative_analysis():
    """Demonstrate comparative analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Comparative Analysis")
    print("=" * 70)

    # Generate sample data
    data = generate_sample_data()

    # Create analyzer
    analyzer = ComparativeAnalyzer()

    # Compare providers
    print("\n--- Provider Comparison ---")
    result = analyzer.compare_providers(data)

    print(f"\nProvider Metrics:")
    print(f"  Best provider: {result.metrics['best_provider']}")
    print(f"  Worst provider: {result.metrics['worst_provider']}")
    print(f"  Performance range: {result.metrics['provider_range']:.3f}")

    print(f"\nInsights:")
    for insight in result.insights:
        print(f"  - {insight}")

    # Compare attack types
    print("\n--- Attack Type Comparison ---")
    result = analyzer.compare_attack_types(data)

    print(f"\nAttack Type Metrics:")
    print(f"  Most effective: {result.metrics['most_effective_attack']}")
    print(f"  Least effective: {result.metrics['least_effective_attack']}")
    print(f"  Effectiveness range: {result.metrics['attack_effectiveness_range']:.3f}")

    print(f"\nInsights:")
    for insight in result.insights:
        print(f"  - {insight}")


def example_effectiveness_analysis():
    """Demonstrate effectiveness analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Effectiveness Analysis")
    print("=" * 70)

    # Generate sample data
    data = generate_sample_data()

    # Create analyzer
    analyzer = EffectivenessAnalyzer()

    # Positional bias analysis
    print("\n--- Positional Bias Analysis ---")
    result = analyzer.positional_bias_analysis(data)

    print(f"\nPosition Metrics:")
    for position in ["start", "middle", "end"]:
        if f"{position}_mean_success" in result.metrics:
            print(f"  {position.capitalize()}: {result.metrics[f'{position}_mean_success']:.3f}")

    if "end_relative_effectiveness" in result.metrics:
        print(f"  End relative effectiveness: {result.metrics['end_relative_effectiveness']:.2f}x")

    print(f"\nInsights:")
    for insight in result.insights:
        print(f"  - {insight}")


def example_multi_analyzer_workflow():
    """Demonstrate multi-analyzer workflow using AnalysisEngine."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Multi-Analyzer Workflow")
    print("=" * 70)

    # Generate sample data
    data = generate_sample_data()

    # Create engine and add analyzers
    engine = AnalysisEngine()
    engine.add_analyzer(StatisticalAnalyzer(confidence_level=0.95))
    engine.add_analyzer(ComparativeAnalyzer())
    engine.add_analyzer(EffectivenessAnalyzer())

    print(f"\nRunning {len(engine)} analyzers...")

    # Run all analyzers
    results = engine.run_analysis(data)

    print(f"\nCompleted {len(results)} analyses")

    # Aggregate results
    summary = engine.aggregate_results(results)

    print(f"\nSummary:")
    print(f"  Total analyzers run: {summary['analyzers_run']}")
    print(f"  Total metrics computed: {summary['total_metrics']}")
    print(f"  Total insights generated: {summary['total_insights']}")

    print(f"\nAll Insights:")
    for insight in summary['insights'][:10]:  # Show first 10
        print(f"  - {insight}")


def example_factory_pattern():
    """Demonstrate analyzer factory pattern."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Factory Pattern")
    print("=" * 70)

    # Create analyzers using factory
    print("\n--- Creating analyzers from factory ---")

    # Create specific analyzer
    statistical = AnalyzerFactory.create("statistical", confidence_level=0.99)
    print(f"Created: {statistical.name} (confidence: {statistical.confidence_level})")

    # Create all analyzers
    analyzers = AnalyzerFactory.create_all()
    print(f"\nCreated {len(analyzers)} analyzers:")
    for analyzer in analyzers:
        print(f"  - {analyzer.name}")

    # Create from configuration
    config = {
        "statistical": {"confidence_level": 0.99},
        "comparative": {},
        "effectiveness": {"name": "CustomEffectivenessAnalyzer"}
    }
    custom_analyzers = AnalyzerFactory.create_from_config(config)
    print(f"\nCreated {len(custom_analyzers)} custom analyzers from config")

    # List available types
    types = AnalyzerFactory.list_types()
    print(f"\nAvailable analyzer types: {', '.join(types)}")


def main():
    """Run all examples."""
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + "  Analysis Package Examples".center(68) + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)

    # Run examples
    example_statistical_analysis()
    example_comparative_analysis()
    example_effectiveness_analysis()
    example_multi_analyzer_workflow()
    example_factory_pattern()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
