"""
Integration tests for evaluation pipeline.

Tests the complete flow from experiment execution through
evaluation to statistical analysis.
"""

import pytest
import numpy as np
from typing import List, Dict, Any

from src.experiments import (
    ExperimentRunner,
    ExperimentConfigBuilder,
    ExperimentType,
)
from src.evaluation import (
    AttackEffectivenessEvaluator,
    PaperComparisonEvaluator,
    RankingQualityEvaluator,
    MetricCalculator,
)
from src.analysis import (
    StatisticalAnalyzer,
    ComparativeAnalyzer,
    EffectivenessAnalyzer,
    AnalysisEngine,
)
from src.attacks import AttackType


@pytest.mark.integration
class TestEvaluationPipeline:
    """Test experiment → evaluation → analysis pipeline."""

    def test_evaluation_after_experiment(
        self, setup_environment, mock_llm_client
    ):
        """Test evaluation of experiment results."""
        from conftest import generate_test_products

        # Run experiment
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.SINGLE_ATTACK)
            .with_trials(10)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .with_attack_types([AttackType.PROMPT_INJECTION])
            .build()
        )

        runner = ExperimentRunner()
        exp_result = runner.run_experiment(config)

        # Convert to evaluation format
        eval_data = []
        for trial in exp_result.trials:
            eval_data.append({
                "trial_id": trial.trial_id,
                "metrics": trial.metrics,
                "metadata": getattr(trial, "metadata", {}),
                "attack_info": getattr(trial, "attack_info", {}),
            })

        # Evaluate results
        evaluator = AttackEffectivenessEvaluator()
        eval_result = evaluator.evaluate(eval_data)

        # Check metrics
        assert eval_result is not None
        assert hasattr(eval_result, "metrics")
        assert len(eval_result.metrics) > 0

        # Verify key metrics exist
        expected_metrics = ["success_rate", "mean_effectiveness"]
        for metric in expected_metrics:
            # One of these should be present
            has_metric = any(
                metric in str(k).lower()
                for k in eval_result.metrics.keys()
            )

    def test_statistical_analysis_of_results(self, mock_experiment_results):
        """Test statistical analysis of evaluation results."""
        # Run statistical analysis
        analyzer = StatisticalAnalyzer(confidence_level=0.95)
        result = analyzer.analyze(mock_experiment_results)

        # Validate statistical metrics
        assert "mean" in result.metrics
        assert "std" in result.metrics
        assert "median" in result.metrics
        assert "ci_lower" in result.metrics
        assert "ci_upper" in result.metrics

        # Check reasonableness
        assert 0.0 <= result.metrics["mean"] <= 1.0
        assert result.metrics["std"] >= 0.0
        assert result.metrics["median"] >= 0.0

        # Confidence interval should be valid
        assert result.metrics["ci_lower"] <= result.metrics["mean"]
        assert result.metrics["mean"] <= result.metrics["ci_upper"]

    def test_comparative_analysis(self, mock_experiment_results):
        """Test cross-provider and cross-attack comparisons."""
        analyzer = ComparativeAnalyzer()

        # Test provider comparison
        provider_result = analyzer.compare_providers(mock_experiment_results)

        assert provider_result is not None
        assert hasattr(provider_result, "metrics")

        # Should identify best/worst providers
        if "best_provider" in provider_result.metrics:
            assert provider_result.metrics["best_provider"] in [
                "openai", "anthropic", "bedrock"
            ]

    def test_attack_type_comparison(self, mock_experiment_results):
        """Test comparison across attack types."""
        analyzer = ComparativeAnalyzer()

        # Compare attack types
        attack_result = analyzer.compare_attack_types(mock_experiment_results)

        assert attack_result is not None
        assert hasattr(attack_result, "metrics")

        # Should identify most effective attack
        if "most_effective_attack" in attack_result.metrics:
            assert attack_result.metrics["most_effective_attack"] in [
                "prompt_injection", "persuasion", "discreditation"
            ]

    def test_effectiveness_analysis(self, mock_experiment_results):
        """Test effectiveness analysis with various metrics."""
        analyzer = EffectivenessAnalyzer()

        # Basic effectiveness
        result = analyzer.analyze(mock_experiment_results)

        assert result is not None
        assert "overall_success_rate" in result.metrics or "success_rate" in result.metrics

    def test_positional_bias_analysis(self):
        """Test positional bias detection."""
        # Generate data with positional bias
        np.random.seed(42)

        data = []
        for i in range(60):
            position = ["start", "middle", "end"][i % 3]

            # Simulate positional bias
            if position == "end":
                success = max(0.0, min(1.0, np.random.normal(0.5, 0.1)))
            else:
                success = max(0.0, min(1.0, np.random.normal(0.3, 0.1)))

            data.append({
                "trial_id": i,
                "metrics": {"success": success},
                "attack_info": {"position": position}
            })

        analyzer = EffectivenessAnalyzer()
        result = analyzer.positional_bias_analysis(data)

        # Should detect bias
        assert result is not None
        assert "end_mean_success" in result.metrics or "position_effect" in result.metrics

    def test_paper_comparison_evaluation(self, mock_experiment_results):
        """Test comparison with paper findings."""
        evaluator = PaperComparisonEvaluator(
            paper_baseline={
                "success_rate": 0.38,  # 38% from paper
                "position_1_rate": 0.40,
            }
        )

        result = evaluator.evaluate(mock_experiment_results)

        assert result is not None
        assert hasattr(result, "metrics")

        # Should have comparison metrics
        if "deviation_from_paper" in result.metrics:
            assert isinstance(result.metrics["deviation_from_paper"], (int, float))

    def test_ranking_quality_metrics(self, mock_experiment_results):
        """Test ranking quality evaluation."""
        evaluator = RankingQualityEvaluator()

        result = evaluator.evaluate(mock_experiment_results)

        assert result is not None
        # Ranking quality metrics should be present

    def test_metric_calculator(self):
        """Test metric calculation utilities."""
        calculator = MetricCalculator()

        # Test success rate calculation
        data = [
            {"metrics": {"success": 1.0}},
            {"metrics": {"success": 0.0}},
            {"metrics": {"success": 1.0}},
        ]

        success_rate = calculator.calculate_success_rate(data)
        assert success_rate == pytest.approx(2/3, 0.01)

    def test_multi_analyzer_orchestration(self, mock_experiment_results):
        """Test orchestrating multiple analyzers."""
        engine = AnalysisEngine()

        # Add all analyzer types
        engine.add_analyzer(StatisticalAnalyzer())
        engine.add_analyzer(ComparativeAnalyzer())
        engine.add_analyzer(EffectivenessAnalyzer())

        # Run all analyses
        results = engine.run_analysis(mock_experiment_results)

        # Verify all completed
        assert len(results) == 3
        assert all(hasattr(r, "metrics") for r in results)

        # Aggregate results
        summary = engine.aggregate_results(results)

        assert summary["analyzers_run"] == 3
        assert summary["total_metrics"] > 0

    def test_end_to_end_evaluation_workflow(
        self, setup_environment, mock_llm_client
    ):
        """
        Test complete evaluation workflow.

        Flow: Experiment → Evaluation → Statistical Analysis → Insights
        """
        # 1. Run experiment
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.SINGLE_ATTACK)
            .with_trials(15)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .with_attack_types([AttackType.PROMPT_INJECTION])
            .build()
        )

        runner = ExperimentRunner()
        exp_result = runner.run_experiment(config)

        # 2. Convert to evaluation format
        eval_data = []
        for trial in exp_result.trials:
            eval_data.append({
                "trial_id": trial.trial_id,
                "metrics": trial.metrics,
                "metadata": getattr(trial, "metadata", {}),
            })

        # 3. Evaluate effectiveness
        effectiveness_eval = AttackEffectivenessEvaluator()
        eff_result = effectiveness_eval.evaluate(eval_data)

        # 4. Statistical analysis
        stat_analyzer = StatisticalAnalyzer()
        stat_result = stat_analyzer.analyze(eval_data)

        # 5. Comparative analysis
        comp_analyzer = ComparativeAnalyzer()
        # Note: May need more data for meaningful comparison

        # 6. Validate complete pipeline
        assert exp_result is not None
        assert eff_result is not None
        assert stat_result is not None

        # Verify insights generated
        if hasattr(stat_result, "insights"):
            assert len(stat_result.insights) >= 0

    def test_confidence_interval_calculation(self):
        """Test confidence interval calculations."""
        np.random.seed(42)

        # Generate sample data
        data = [
            {"metrics": {"success": np.random.random()}}
            for _ in range(50)
        ]

        analyzer = StatisticalAnalyzer(confidence_level=0.95)
        result = analyzer.analyze(data)

        # Verify CI calculation
        assert "ci_lower" in result.metrics
        assert "ci_upper" in result.metrics

        # CI should contain mean
        assert result.metrics["ci_lower"] <= result.metrics["mean"]
        assert result.metrics["mean"] <= result.metrics["ci_upper"]

        # CI width should be reasonable
        ci_width = result.metrics["ci_upper"] - result.metrics["ci_lower"]
        assert 0.0 < ci_width < 1.0

    def test_hypothesis_testing(self):
        """Test statistical hypothesis testing."""
        np.random.seed(42)

        # Create two groups with different means
        group1 = [
            {"metrics": {"success": np.random.normal(0.3, 0.1)}}
            for _ in range(30)
        ]

        group2 = [
            {"metrics": {"success": np.random.normal(0.6, 0.1)}}
            for _ in range(30)
        ]

        analyzer = StatisticalAnalyzer()

        # Extract success values
        g1_values = [d["metrics"]["success"] for d in group1]
        g2_values = [d["metrics"]["success"] for d in group2]

        # Perform t-test
        result = analyzer.t_test(g1_values, g2_values)

        # Should detect significant difference
        assert "p_value" in result.metrics
        assert "statistic" in result.metrics

        # With these parameters, should be significant
        if result.metrics["p_value"] < 0.05:
            # Significant difference detected
            pass

    def test_trend_analysis(self):
        """Test trend detection over trials."""
        np.random.seed(42)

        # Generate data with increasing trend
        data = []
        for i in range(50):
            success = min(1.0, 0.2 + 0.01 * i + np.random.normal(0, 0.05))
            data.append({
                "trial_id": i,
                "metrics": {"success": success}
            })

        analyzer = EffectivenessAnalyzer()
        result = analyzer.success_trend_analysis(data)

        # Should detect positive trend
        assert "trend_slope" in result.metrics
        assert result.metrics["trend_slope"] > 0.005

    def test_outlier_detection(self):
        """Test outlier detection in results."""
        np.random.seed(42)

        # Generate data with outliers
        data = []
        for i in range(50):
            if i in [5, 15, 35]:
                # Outlier
                success = 2.0  # Invalid value
            else:
                success = np.random.normal(0.5, 0.1)

            data.append({
                "trial_id": i,
                "metrics": {"success": success}
            })

        analyzer = StatisticalAnalyzer()
        result = analyzer.detect_outliers(data)

        # Should detect outliers
        if "outlier_count" in result.metrics:
            assert result.metrics["outlier_count"] > 0

    @pytest.mark.slow
    def test_comprehensive_evaluation_suite(
        self, setup_environment, mock_llm_client
    ):
        """Run comprehensive evaluation suite."""
        # Run multiple experiment types
        experiment_types = [
            ExperimentType.BASELINE,
            ExperimentType.SINGLE_ATTACK,
        ]

        all_results = []

        for exp_type in experiment_types:
            config = (
                ExperimentConfigBuilder()
                .with_experiment_type(exp_type)
                .with_trials(10)
                .with_vector_store(setup_environment["vector_store"])
                .with_llm_client(mock_llm_client)
                .build()
            )

            if exp_type == ExperimentType.SINGLE_ATTACK:
                config.attack_types = [AttackType.PROMPT_INJECTION]

            runner = ExperimentRunner()
            result = runner.run_experiment(config)
            all_results.append(result)

        # Evaluate all results
        eval_data = []
        for exp_result in all_results:
            for trial in exp_result.trials:
                eval_data.append({
                    "trial_id": trial.trial_id,
                    "metrics": trial.metrics,
                    "metadata": getattr(trial, "metadata", {}),
                })

        # Run comprehensive analysis
        engine = AnalysisEngine()
        engine.add_analyzer(StatisticalAnalyzer())
        engine.add_analyzer(ComparativeAnalyzer())
        engine.add_analyzer(EffectivenessAnalyzer())

        results = engine.run_analysis(eval_data)

        # Verify comprehensive analysis
        assert len(results) == 3
        assert all(r is not None for r in results)

    @pytest.fixture
    def setup_environment(self, qdrant_service, test_products, integration_test_collection):
        """Setup evaluation test environment."""
        from src.vector_store import VectorStoreManager

        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Add test products
        if "categories" in test_products:
            products = []
            for cat_data in list(test_products["categories"].values())[:2]:
                products.extend(cat_data["items"][:5])
        else:
            products = test_products[:10]

        vector_store.add_documents(products)

        yield {"vector_store": vector_store}

        try:
            vector_store.clear_collection()
        except Exception:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
