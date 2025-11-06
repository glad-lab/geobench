"""
Unit tests for analysis package.

Tests all analyzers, engine, and factory with comprehensive coverage.
"""

import pytest
import numpy as np
from typing import List, Dict, Any

from src.analysis import (
    BaseAnalyzer,
    AnalysisResult,
    StatisticalAnalyzer,
    ComparativeAnalyzer,
    EffectivenessAnalyzer,
    AnalysisEngine,
    AnalyzerFactory,
)


# Test Fixtures


@pytest.fixture
def sample_trial_data() -> List[Dict[str, Any]]:
    """Sample trial data for testing."""
    return [
        {
            "trial_id": 0,
            "metrics": {"success": 1.0, "position_change": 3, "final_position": 1},
            "metadata": {"provider": "openai", "query_type": "recommendation"},
            "attack_info": {"attack_type": "prompt_injection", "position": "start"}
        },
        {
            "trial_id": 1,
            "metrics": {"success": 0.0, "position_change": 0, "final_position": 3},
            "metadata": {"provider": "anthropic", "query_type": "recommendation"},
            "attack_info": {"attack_type": "persuasion", "position": "end"}
        },
        {
            "trial_id": 2,
            "metrics": {"success": 1.0, "position_change": 2, "final_position": 1},
            "metadata": {"provider": "openai", "query_type": "comparison"},
            "attack_info": {"attack_type": "prompt_injection", "position": "end"}
        },
        {
            "trial_id": 3,
            "metrics": {"success": 0.0, "position_change": 1, "final_position": 2},
            "metadata": {"provider": "bedrock", "query_type": "recommendation"},
            "attack_info": {"attack_type": "discreditation", "position": "middle"}
        },
    ]


# Test BaseAnalyzer and AnalysisResult


def test_analysis_result_creation():
    """Test AnalysisResult dataclass creation."""
    result = AnalysisResult(
        analyzer_name="TestAnalyzer",
        metrics={"mean": 0.5, "std": 0.1},
        insights=["Test insight"],
        confidence=0.95
    )

    assert result.analyzer_name == "TestAnalyzer"
    assert result.metrics["mean"] == 0.5
    assert len(result.insights) == 1
    assert result.confidence == 0.95


def test_base_analyzer_validation():
    """Test BaseAnalyzer data validation."""
    class TestAnalyzer(BaseAnalyzer):
        def analyze(self, data):
            self._validate_data(data)
            return AnalysisResult(
                analyzer_name=self.name,
                metrics={},
                insights=[]
            )

    analyzer = TestAnalyzer()

    # Should raise on empty data
    with pytest.raises(ValueError, match="Cannot analyze empty data"):
        analyzer.analyze([])

    # Should raise on non-list data
    with pytest.raises(ValueError, match="must be a list"):
        analyzer.analyze({"key": "value"})

    # Should raise on non-dict items
    with pytest.raises(ValueError, match="must be dictionaries"):
        analyzer.analyze([1, 2, 3])

    # Should succeed on valid data
    result = analyzer.analyze([{"key": "value"}])
    assert isinstance(result, AnalysisResult)


# Test StatisticalAnalyzer


def test_statistical_analyzer_basic_analysis(sample_trial_data):
    """Test basic statistical analysis."""
    analyzer = StatisticalAnalyzer(confidence_level=0.95)
    result = analyzer.analyze(sample_trial_data)

    assert isinstance(result, AnalysisResult)
    assert "mean" in result.metrics
    assert "std" in result.metrics
    assert "ci_lower" in result.metrics
    assert "ci_upper" in result.metrics
    assert result.metrics["mean"] == 0.5  # 2 successes out of 4
    assert len(result.insights) > 0


def test_statistical_analyzer_t_test():
    """Test t-test functionality."""
    analyzer = StatisticalAnalyzer()

    baseline = [0.2, 0.25, 0.22, 0.28, 0.24]
    treatment = [0.5, 0.55, 0.52, 0.58, 0.54]

    result = analyzer.t_test(baseline, treatment)

    assert "t_statistic" in result.metrics
    assert "p_value" in result.metrics
    assert "cohens_d" in result.metrics
    assert "group1_mean" in result.metrics
    assert "group2_mean" in result.metrics
    assert result.metrics["significant"] == True  # Should be significant
    assert result.metrics["group2_mean"] > result.metrics["group1_mean"]


def test_statistical_analyzer_t_test_paired():
    """Test paired t-test."""
    analyzer = StatisticalAnalyzer()

    group1 = [0.2, 0.3, 0.25, 0.28]
    group2 = [0.5, 0.6, 0.55, 0.58]

    result = analyzer.t_test(group1, group2, paired=True)

    assert "t_statistic" in result.metrics
    assert "paired t-test" in result.analyzer_name.lower()


def test_statistical_analyzer_anova():
    """Test ANOVA functionality."""
    analyzer = StatisticalAnalyzer()

    groups = [
        [0.2, 0.3, 0.25],  # Baseline
        [0.5, 0.6, 0.55],  # Attack 1
        [0.4, 0.5, 0.45]   # Attack 2
    ]
    group_names = ["baseline", "attack1", "attack2"]

    result = analyzer.anova(groups, group_names)

    assert "f_statistic" in result.metrics
    assert "p_value" in result.metrics
    assert "num_groups" in result.metrics
    assert result.metrics["num_groups"] == 3
    assert "baseline_mean" in result.metrics
    assert "attack1_mean" in result.metrics


def test_statistical_analyzer_chi_square():
    """Test chi-square goodness of fit."""
    analyzer = StatisticalAnalyzer()

    observed = [30, 45, 25]  # Observed frequencies
    expected = [33, 33, 34]  # Expected frequencies

    result = analyzer.chi_square(observed, expected)

    assert "chi2_statistic" in result.metrics
    assert "p_value" in result.metrics
    assert "degrees_of_freedom" in result.metrics
    assert result.metrics["degrees_of_freedom"] == 2


def test_statistical_analyzer_correlation():
    """Test Pearson correlation."""
    analyzer = StatisticalAnalyzer()

    # Strong negative correlation
    x = [1, 2, 3, 4, 5]
    y = [5, 4, 3, 2, 1]

    result = analyzer.pearson_correlation(x, y)

    assert "correlation" in result.metrics
    assert "p_value" in result.metrics
    assert "r_squared" in result.metrics
    assert result.metrics["correlation"] < -0.9  # Strong negative
    assert result.metrics["significant"] == True


def test_statistical_analyzer_edge_cases():
    """Test edge cases for statistical analyzer."""
    analyzer = StatisticalAnalyzer()

    # Empty groups
    with pytest.raises(ValueError):
        analyzer.t_test([], [1, 2, 3])

    # Mismatched paired test
    with pytest.raises(ValueError):
        analyzer.t_test([1, 2, 3], [1, 2], paired=True)

    # Single group for ANOVA
    with pytest.raises(ValueError):
        analyzer.anova([[1, 2, 3]])

    # Too few points for correlation
    with pytest.raises(ValueError):
        analyzer.pearson_correlation([1], [2])


# Test ComparativeAnalyzer


def test_comparative_analyzer_providers(sample_trial_data):
    """Test provider comparison."""
    analyzer = ComparativeAnalyzer()
    result = analyzer.compare_providers(sample_trial_data)

    assert isinstance(result, AnalysisResult)
    assert "best_provider" in result.metrics
    assert "worst_provider" in result.metrics
    assert "provider_range" in result.metrics
    assert "openai_mean" in result.metrics or "anthropic_mean" in result.metrics
    assert len(result.insights) > 0


def test_comparative_analyzer_attack_types(sample_trial_data):
    """Test attack type comparison."""
    analyzer = ComparativeAnalyzer()
    result = analyzer.compare_attack_types(sample_trial_data)

    assert isinstance(result, AnalysisResult)
    assert "most_effective_attack" in result.metrics
    assert "least_effective_attack" in result.metrics
    assert "attack_effectiveness_range" in result.metrics
    assert len(result.insights) > 0


def test_comparative_analyzer_ranking():
    """Test ranking by effectiveness."""
    analyzer = ComparativeAnalyzer()

    data = [
        {"metadata": {"provider": "openai"}, "metrics": {"success": 0.6}},
        {"metadata": {"provider": "openai"}, "metrics": {"success": 0.7}},
        {"metadata": {"provider": "anthropic"}, "metrics": {"success": 0.4}},
        {"metadata": {"provider": "anthropic"}, "metrics": {"success": 0.5}},
    ]

    result = analyzer.rank_by_effectiveness(data, dimension="provider")

    assert "top_entity" in result.metrics
    assert "bottom_entity" in result.metrics
    assert result.metadata["rankings"][0][0] == "openai"  # Best provider


def test_comparative_analyzer_no_data():
    """Test comparative analyzer with missing data."""
    analyzer = ComparativeAnalyzer()

    # No provider info - analyze() should still work but compare_providers should fail
    data = [{"metrics": {"success": 0.5}, "metadata": {}, "attack_info": {}}]

    with pytest.raises(ValueError, match="No provider information"):
        analyzer.compare_providers(data)

    # No attack type info
    with pytest.raises(ValueError, match="No attack type information"):
        analyzer.compare_attack_types(data)


# Test EffectivenessAnalyzer


def test_effectiveness_analyzer_basic(sample_trial_data):
    """Test basic effectiveness analysis."""
    analyzer = EffectivenessAnalyzer()
    result = analyzer.analyze(sample_trial_data)

    assert isinstance(result, AnalysisResult)
    assert "overall_success_rate" in result.metrics
    assert "position_1_rate" in result.metrics
    assert "mean_final_position" in result.metrics
    assert result.metrics["overall_success_rate"] == 0.5


def test_effectiveness_analyzer_positional_bias(sample_trial_data):
    """Test positional bias analysis."""
    analyzer = EffectivenessAnalyzer()
    result = analyzer.positional_bias_analysis(sample_trial_data)

    assert isinstance(result, AnalysisResult)
    assert "start_mean_success" in result.metrics or "end_mean_success" in result.metrics
    assert len(result.insights) > 0


def test_effectiveness_analyzer_query_type(sample_trial_data):
    """Test query type analysis."""
    analyzer = EffectivenessAnalyzer()
    result = analyzer.success_by_query_type(sample_trial_data)

    assert isinstance(result, AnalysisResult)
    assert "most_effective_query_type" in result.metrics
    assert "least_effective_query_type" in result.metrics


def test_effectiveness_analyzer_trend():
    """Test trend analysis."""
    analyzer = EffectivenessAnalyzer()

    # Create data with clear upward trend
    data = [
        {"trial_id": i, "metrics": {"success": 0.1 + 0.05 * i}}
        for i in range(10)
    ]

    result = analyzer.success_trend_analysis(data)

    assert "trend_slope" in result.metrics
    assert "r_squared" in result.metrics
    assert "early_mean" in result.metrics
    assert "late_mean" in result.metrics
    assert result.metrics["trend_slope"] > 0  # Upward trend


def test_effectiveness_analyzer_insufficient_data():
    """Test effectiveness analyzer with insufficient data."""
    analyzer = EffectivenessAnalyzer()

    # Too few trials for trend
    data = [{"trial_id": 0, "metrics": {"success": 0.5}}]

    with pytest.raises(ValueError, match="at least 3 trials"):
        analyzer.success_trend_analysis(data)


# Test AnalysisEngine


def test_analysis_engine_add_analyzer():
    """Test adding analyzers to engine."""
    engine = AnalysisEngine()

    assert len(engine) == 0

    engine.add_analyzer(StatisticalAnalyzer())
    assert len(engine) == 1

    engine.add_analyzer(ComparativeAnalyzer())
    assert len(engine) == 2


def test_analysis_engine_run_analysis(sample_trial_data):
    """Test running multiple analyzers."""
    engine = AnalysisEngine()
    engine.add_analyzer(StatisticalAnalyzer())
    engine.add_analyzer(ComparativeAnalyzer())
    engine.add_analyzer(EffectivenessAnalyzer())

    results = engine.run_analysis(sample_trial_data)

    assert len(results) == 3
    assert all(isinstance(r, AnalysisResult) for r in results)


def test_analysis_engine_aggregate_results(sample_trial_data):
    """Test result aggregation."""
    engine = AnalysisEngine()
    engine.add_analyzer(StatisticalAnalyzer())
    engine.add_analyzer(ComparativeAnalyzer())

    results = engine.run_analysis(sample_trial_data)
    summary = engine.aggregate_results(results)

    assert "metrics" in summary
    assert "insights" in summary
    assert "analyzers_run" in summary
    assert "total_metrics" in summary
    assert summary["analyzers_run"] == 2
    assert summary["total_metrics"] > 0


def test_analysis_engine_clear_analyzers():
    """Test clearing analyzers."""
    engine = AnalysisEngine()
    engine.add_analyzer(StatisticalAnalyzer())
    engine.add_analyzer(ComparativeAnalyzer())

    assert len(engine) == 2

    engine.clear_analyzers()
    assert len(engine) == 0


def test_analysis_engine_no_analyzers():
    """Test engine with no analyzers."""
    engine = AnalysisEngine()

    with pytest.raises(ValueError, match="No analyzers registered"):
        engine.run_analysis([{"key": "value"}])


def test_analysis_engine_empty_data():
    """Test engine with empty data."""
    engine = AnalysisEngine()
    engine.add_analyzer(StatisticalAnalyzer())

    with pytest.raises(ValueError, match="Cannot analyze empty data"):
        engine.run_analysis([])


def test_analysis_engine_method_chaining():
    """Test fluent interface."""
    engine = AnalysisEngine()

    # Method chaining should work
    result = engine.add_analyzer(StatisticalAnalyzer()) \
                   .add_analyzer(ComparativeAnalyzer())

    assert result is engine
    assert len(engine) == 2


# Test AnalyzerFactory


def test_analyzer_factory_create():
    """Test creating analyzers via factory."""
    # Create statistical analyzer
    analyzer = AnalyzerFactory.create("statistical", confidence_level=0.99)
    assert isinstance(analyzer, StatisticalAnalyzer)
    assert analyzer.confidence_level == 0.99

    # Create comparative analyzer
    analyzer = AnalyzerFactory.create("comparative")
    assert isinstance(analyzer, ComparativeAnalyzer)

    # Create effectiveness analyzer
    analyzer = AnalyzerFactory.create("effectiveness")
    assert isinstance(analyzer, EffectivenessAnalyzer)


def test_analyzer_factory_create_invalid():
    """Test factory with invalid type."""
    with pytest.raises(ValueError, match="Unknown analyzer type"):
        AnalyzerFactory.create("nonexistent")


def test_analyzer_factory_create_all():
    """Test creating all analyzers."""
    analyzers = AnalyzerFactory.create_all(confidence_level=0.95)

    assert len(analyzers) >= 3  # At least 3 built-in analyzers
    assert any(isinstance(a, StatisticalAnalyzer) for a in analyzers)
    assert any(isinstance(a, ComparativeAnalyzer) for a in analyzers)
    assert any(isinstance(a, EffectivenessAnalyzer) for a in analyzers)


def test_analyzer_factory_create_from_config():
    """Test creating analyzers from config."""
    config = {
        "statistical": {"confidence_level": 0.99},
        "comparative": {},
        "effectiveness": {"name": "CustomEffectiveness"}
    }

    analyzers = AnalyzerFactory.create_from_config(config)

    assert len(analyzers) == 3
    assert any(isinstance(a, StatisticalAnalyzer) and a.confidence_level == 0.99
               for a in analyzers)


def test_analyzer_factory_list_types():
    """Test listing analyzer types."""
    types = AnalyzerFactory.list_types()

    assert "statistical" in types
    assert "comparative" in types
    assert "effectiveness" in types


def test_analyzer_factory_is_registered():
    """Test checking registration."""
    assert AnalyzerFactory.is_registered("statistical") is True
    assert AnalyzerFactory.is_registered("nonexistent") is False


def test_analyzer_factory_register_custom():
    """Test registering custom analyzer."""
    class CustomAnalyzer(BaseAnalyzer):
        def analyze(self, data):
            return AnalysisResult(
                analyzer_name=self.name,
                metrics={"custom": 1.0},
                insights=[]
            )

    # Register
    AnalyzerFactory.register("custom", CustomAnalyzer)

    # Should be registered
    assert AnalyzerFactory.is_registered("custom")

    # Should be able to create
    analyzer = AnalyzerFactory.create("custom")
    assert isinstance(analyzer, CustomAnalyzer)


def test_analyzer_factory_register_invalid():
    """Test registering invalid analyzer."""
    class NotAnAnalyzer:
        pass

    with pytest.raises(TypeError, match="must be a subclass of BaseAnalyzer"):
        AnalyzerFactory.register("invalid", NotAnAnalyzer)


# Integration Tests


def test_end_to_end_workflow(sample_trial_data):
    """Test complete analysis workflow."""
    # Create engine
    engine = AnalysisEngine()

    # Add analyzers via factory
    for analyzer_type in ["statistical", "comparative", "effectiveness"]:
        analyzer = AnalyzerFactory.create(analyzer_type)
        engine.add_analyzer(analyzer)

    # Run analysis
    results = engine.run_analysis(sample_trial_data)

    # Verify results
    assert len(results) == 3

    # Aggregate results
    summary = engine.aggregate_results(results)

    assert summary["analyzers_run"] == 3
    assert len(summary["insights"]) > 0
    assert len(summary["metrics"]) > 0


def test_statistical_significance_workflow():
    """Test workflow for statistical significance testing."""
    # Generate data with known difference
    np.random.seed(42)
    baseline_data = [
        {"metrics": {"success": float(np.random.normal(0.3, 0.1))}}
        for _ in range(30)
    ]
    treatment_data = [
        {"metrics": {"success": float(np.random.normal(0.6, 0.1))}}
        for _ in range(30)
    ]

    # Extract values
    baseline_values = [d["metrics"]["success"] for d in baseline_data]
    treatment_values = [d["metrics"]["success"] for d in treatment_data]

    # Run t-test
    analyzer = StatisticalAnalyzer()
    result = analyzer.t_test(baseline_values, treatment_values)

    # Should detect significant difference
    assert result.metrics["significant"] == True
    assert result.metrics["p_value"] < 0.05
    assert abs(result.metrics["cohens_d"]) > 0.5  # Large effect size


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
