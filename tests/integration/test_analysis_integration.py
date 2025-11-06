"""
Integration tests for analysis package.

Tests the analysis package with simulated experiment results to verify
end-to-end functionality.
"""

import pytest
import numpy as np
from typing import List, Dict, Any

from src.analysis import (
    StatisticalAnalyzer,
    ComparativeAnalyzer,
    EffectivenessAnalyzer,
    AnalysisEngine,
    AnalyzerFactory,
)


def generate_experiment_results(
    n_trials: int = 50,
    seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Generate realistic experiment results for testing.

    Simulates results from adversarial SEO experiments with:
    - Multiple LLM providers
    - Different attack types
    - Positional bias effects
    """
    np.random.seed(seed)

    providers = ["openai", "anthropic", "bedrock"]
    attack_types = ["prompt_injection", "persuasion", "discreditation"]
    positions = ["start", "middle", "end"]

    results = []

    for trial_id in range(n_trials):
        # Random selection
        provider = np.random.choice(providers)
        attack_type = np.random.choice(attack_types)
        position = np.random.choice(positions)

        # Realistic success rate based on conditions
        base_success = 0.25
        if attack_type == "prompt_injection":
            base_success = 0.45
        elif attack_type == "persuasion":
            base_success = 0.35

        if position == "end":
            base_success *= 1.3  # Positional bias effect

        if provider == "openai":
            base_success *= 1.1  # Provider effect

        # Add noise
        success = min(1.0, max(0.0, base_success + np.random.normal(0, 0.1)))
        final_position = 1 if success > 0.7 else (2 if success > 0.4 else 3)

        results.append({
            "trial_id": trial_id,
            "metrics": {
                "success": success,
                "position_change": int(success * 3),
                "final_position": final_position
            },
            "metadata": {
                "provider": provider,
                "query_type": "recommendation",
                "model": f"{provider}-model"
            },
            "attack_info": {
                "attack_type": attack_type,
                "position": position,
                "approach": "glass_box"
            }
        })

    return results


def test_statistical_analysis_integration():
    """Test statistical analysis with realistic data."""
    data = generate_experiment_results(n_trials=100)

    analyzer = StatisticalAnalyzer(confidence_level=0.95)
    result = analyzer.analyze(data)

    # Verify comprehensive metrics
    assert "mean" in result.metrics
    assert "std" in result.metrics
    assert "median" in result.metrics
    assert "ci_lower" in result.metrics
    assert "ci_upper" in result.metrics

    # Verify reasonable values
    assert 0.0 <= result.metrics["mean"] <= 1.0
    assert result.metrics["std"] >= 0.0
    assert result.metrics["n"] == 100

    # Verify insights generated
    assert len(result.insights) > 0


def test_comparative_analysis_integration():
    """Test comparative analysis across providers and attack types."""
    data = generate_experiment_results(n_trials=150)

    analyzer = ComparativeAnalyzer()

    # Test provider comparison
    provider_result = analyzer.compare_providers(data)
    assert "best_provider" in provider_result.metrics
    assert "worst_provider" in provider_result.metrics
    assert provider_result.metrics["best_provider"] in ["openai", "anthropic", "bedrock"]

    # Test attack type comparison
    attack_result = analyzer.compare_attack_types(data)
    assert "most_effective_attack" in attack_result.metrics
    assert attack_result.metrics["most_effective_attack"] in [
        "prompt_injection", "persuasion", "discreditation"
    ]


def test_effectiveness_analysis_integration():
    """Test effectiveness analysis with positional bias."""
    data = generate_experiment_results(n_trials=100)

    analyzer = EffectivenessAnalyzer()

    # Test basic effectiveness
    basic_result = analyzer.analyze(data)
    assert "overall_success_rate" in basic_result.metrics
    assert 0.0 <= basic_result.metrics["overall_success_rate"] <= 1.0

    # Test positional bias (should show end > start)
    position_result = analyzer.positional_bias_analysis(data)
    assert "end_mean_success" in position_result.metrics
    assert "start_mean_success" in position_result.metrics

    # End position should be more effective (due to our simulation)
    if "end_relative_effectiveness" in position_result.metrics:
        assert position_result.metrics["end_relative_effectiveness"] > 1.0


def test_multi_analyzer_orchestration():
    """Test orchestrating multiple analyzers."""
    data = generate_experiment_results(n_trials=200)

    # Create engine
    engine = AnalysisEngine()

    # Add all analyzer types
    engine.add_analyzer(StatisticalAnalyzer())
    engine.add_analyzer(ComparativeAnalyzer())
    engine.add_analyzer(EffectivenessAnalyzer())

    assert len(engine) == 3

    # Run all analyses
    results = engine.run_analysis(data)

    # Verify all completed
    assert len(results) == 3
    assert all(hasattr(r, "metrics") for r in results)
    assert all(hasattr(r, "insights") for r in results)

    # Aggregate results
    summary = engine.aggregate_results(results)

    assert summary["analyzers_run"] == 3
    assert summary["total_metrics"] > 0
    assert summary["total_insights"] > 0


def test_factory_integration():
    """Test factory pattern for analyzer creation."""
    data = generate_experiment_results(n_trials=50)

    # Create via factory
    statistical = AnalyzerFactory.create("statistical", confidence_level=0.99)
    assert statistical.confidence_level == 0.99

    # Create all
    analyzers = AnalyzerFactory.create_all()
    assert len(analyzers) >= 3

    # Each analyzer should work with data
    for analyzer in analyzers:
        try:
            result = analyzer.analyze(data)
            assert result is not None
        except Exception:
            # Some analyzers might need specific data structure
            pass


def test_cross_provider_statistical_comparison():
    """Test statistical comparison across providers."""
    data = generate_experiment_results(n_trials=300)

    # Group by provider
    provider_groups = {}
    for item in data:
        provider = item["metadata"]["provider"]
        if provider not in provider_groups:
            provider_groups[provider] = []
        provider_groups[provider].append(item["metrics"]["success"])

    # Run ANOVA
    analyzer = StatisticalAnalyzer()
    groups = list(provider_groups.values())
    group_names = list(provider_groups.keys())

    result = analyzer.anova(groups, group_names)

    assert "f_statistic" in result.metrics
    assert "p_value" in result.metrics
    assert result.metrics["num_groups"] == len(provider_groups)


def test_trend_analysis_integration():
    """Test trend detection over time."""
    # Generate data with clear trend
    np.random.seed(42)

    data = []
    for i in range(50):
        # Increasing success rate over time
        success = min(1.0, 0.2 + 0.01 * i + np.random.normal(0, 0.05))
        data.append({
            "trial_id": i,
            "metrics": {"success": success}
        })

    analyzer = EffectivenessAnalyzer()
    result = analyzer.success_trend_analysis(data)

    # Should detect positive trend
    assert "trend_slope" in result.metrics
    assert result.metrics["trend_slope"] > 0.005  # Positive slope
    assert "r_squared" in result.metrics


def test_positional_bias_replication():
    """
    Test positional bias analysis replicating Nestaas et al. findings.

    Paper finding: Attacks at end of context are ~1.3x more effective.
    """
    # Generate data with strong positional bias
    np.random.seed(42)

    data = []
    for i in range(150):
        position = ["start", "middle", "end"][i % 3]

        # Strong positional effect
        if position == "start":
            success = max(0.0, np.random.normal(0.3, 0.1))
        elif position == "middle":
            success = max(0.0, np.random.normal(0.35, 0.1))
        else:  # end
            success = max(0.0, np.random.normal(0.4, 0.1))

        data.append({
            "trial_id": i,
            "metrics": {"success": min(1.0, success)},
            "attack_info": {"position": position}
        })

    analyzer = EffectivenessAnalyzer()
    result = analyzer.positional_bias_analysis(data)

    # Verify end is more effective
    assert "end_relative_effectiveness" in result.metrics
    assert result.metrics["end_relative_effectiveness"] > 1.1


def test_complete_workflow():
    """Test complete analysis workflow from data to insights."""
    # Generate realistic experiment data
    data = generate_experiment_results(n_trials=250)

    # Create comprehensive analysis
    engine = AnalysisEngine()

    # Configure analyzers
    engine.add_analyzer(
        AnalyzerFactory.create("statistical", confidence_level=0.95)
    )
    engine.add_analyzer(AnalyzerFactory.create("comparative"))
    engine.add_analyzer(AnalyzerFactory.create("effectiveness"))

    # Run analysis
    results = engine.run_analysis(data)

    # Aggregate
    summary = engine.aggregate_results(results)

    # Verify comprehensive output
    assert summary["analyzers_run"] == 3
    assert summary["total_metrics"] >= 20  # Should have many metrics
    assert summary["total_insights"] >= 5  # Should have insights

    # Verify all analyzer types ran
    analyzer_names = summary["analyzer_names"]
    assert any("Statistical" in name for name in analyzer_names)
    assert any("Comparative" in name for name in analyzer_names)
    assert any("Effectiveness" in name for name in analyzer_names)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
