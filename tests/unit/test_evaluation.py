"""Comprehensive tests for evaluation package."""

import pytest
import numpy as np
from datetime import datetime
from src.evaluation import (
    BaseEvaluator,
    EvaluationResult,
    MetricCalculator,
    AttackEffectivenessEvaluator,
    PaperComparisonEvaluator,
    RankingQualityEvaluator,
    ResultAggregator,
    MetricAggregator,
)


# Test fixtures
@pytest.fixture
def sample_baseline_results():
    """Sample baseline ranking results without attacks."""
    return [
        {
            "has_attack": False,
            "attacked_product": "prod-1",
            "ranked_products": [
                {"id": "prod-2", "score": 0.95},
                {"id": "prod-3", "score": 0.90},
                {"id": "prod-1", "score": 0.85},
                {"id": "prod-4", "score": 0.80},
                {"id": "prod-5", "score": 0.75},
            ]
        },
        {
            "has_attack": False,
            "attacked_product": "prod-1",
            "ranked_products": [
                {"id": "prod-3", "score": 0.92},
                {"id": "prod-2", "score": 0.91},
                {"id": "prod-1", "score": 0.88},
                {"id": "prod-4", "score": 0.82},
                {"id": "prod-5", "score": 0.78},
            ]
        },
    ]


@pytest.fixture
def sample_attack_results():
    """Sample attack ranking results with successful attacks."""
    return [
        {
            "has_attack": True,
            "attacked_product": "prod-1",
            "attack_type": "prompt_injection",
            "attack_position": "end",
            "ranked_products": [
                {"id": "prod-1", "score": 0.98},
                {"id": "prod-2", "score": 0.92},
                {"id": "prod-3", "score": 0.88},
                {"id": "prod-4", "score": 0.82},
                {"id": "prod-5", "score": 0.78},
            ],
            "top_k_ids": ["prod-1", "prod-2", "prod-3", "prod-4", "prod-5"]
        },
        {
            "has_attack": True,
            "attacked_product": "prod-1",
            "attack_type": "discreditation",
            "attack_position": "middle",
            "ranked_products": [
                {"id": "prod-2", "score": 0.93},
                {"id": "prod-1", "score": 0.91},
                {"id": "prod-3", "score": 0.87},
                {"id": "prod-4", "score": 0.81},
                {"id": "prod-5", "score": 0.76},
            ],
            "top_k_ids": ["prod-2", "prod-1", "prod-3", "prod-4", "prod-5"]
        },
        {
            "has_attack": True,
            "attacked_product": "prod-1",
            "attack_type": "persuasion",
            "attack_position": "end",
            "ranked_products": [
                {"id": "prod-1", "score": 0.96},
                {"id": "prod-3", "score": 0.90},
                {"id": "prod-2", "score": 0.89},
                {"id": "prod-4", "score": 0.83},
                {"id": "prod-5", "score": 0.77},
            ],
            "top_k_ids": ["prod-1", "prod-3", "prod-2", "prod-4", "prod-5"]
        },
    ]


# Test EvaluationResult
class TestEvaluationResult:
    def test_initialization(self):
        result = EvaluationResult(
            evaluator_name="TestEvaluator",
            metrics={"accuracy": 0.95}
        )
        assert result.evaluator_name == "TestEvaluator"
        assert result.metrics["accuracy"] == 0.95
        assert result.passed is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_add_error(self):
        result = EvaluationResult(
            evaluator_name="TestEvaluator",
            metrics={}
        )
        result.add_error("Test error")
        assert len(result.errors) == 1
        assert result.errors[0] == "Test error"
        assert result.passed is False

    def test_add_warning(self):
        result = EvaluationResult(
            evaluator_name="TestEvaluator",
            metrics={}
        )
        result.add_warning("Test warning")
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Test warning"
        assert result.passed is True  # Warnings don't fail

    def test_to_dict(self):
        result = EvaluationResult(
            evaluator_name="TestEvaluator",
            metrics={"accuracy": 0.95}
        )
        result_dict = result.to_dict()
        assert result_dict["evaluator_name"] == "TestEvaluator"
        assert result_dict["metrics"]["accuracy"] == 0.95
        assert "timestamp" in result_dict


# Test MetricCalculator
class TestMetricCalculator:
    def test_success_rate_all_successful(self, sample_attack_results):
        # All 3 attacks have target in top-5
        rate = MetricCalculator.success_rate(sample_attack_results, top_k=5)
        assert rate == 1.0

    def test_success_rate_partial(self, sample_attack_results):
        # Only 2 attacks have target at position 1
        rate = MetricCalculator.success_rate(sample_attack_results, top_k=1)
        assert rate == pytest.approx(2/3, abs=0.01)

    def test_success_rate_empty(self):
        rate = MetricCalculator.success_rate([])
        assert rate == 0.0

    def test_position_1_rate(self, sample_attack_results):
        # 2 out of 3 have prod-1 at position 1
        rate = MetricCalculator.position_1_rate(sample_attack_results)
        assert rate == pytest.approx(2/3, abs=0.01)

    def test_mean_rank(self, sample_attack_results):
        # Ranks: 1, 2, 1 -> mean = 1.33
        rank = MetricCalculator.mean_rank(sample_attack_results)
        assert rank == pytest.approx(1.33, abs=0.01)

    def test_mean_rank_empty(self):
        rank = MetricCalculator.mean_rank([])
        assert rank == float('inf')

    def test_median_rank(self, sample_attack_results):
        # Ranks: 1, 2, 1 -> median = 1
        rank = MetricCalculator.median_rank(sample_attack_results)
        assert rank == 1.0

    def test_rank_improvement(self, sample_baseline_results, sample_attack_results):
        # Baseline mean rank: 3, Attack mean rank: 1.33
        # Improvement: 3 - 1.33 = 1.67
        improvement = MetricCalculator.rank_improvement(
            sample_baseline_results,
            sample_attack_results
        )
        assert improvement > 0  # Attack improved ranking
        assert improvement == pytest.approx(1.67, abs=0.01)

    def test_attack_type_effectiveness(self, sample_attack_results):
        effectiveness = MetricCalculator.attack_type_effectiveness(
            sample_attack_results
        )
        assert "prompt_injection" in effectiveness
        assert "discreditation" in effectiveness
        assert "persuasion" in effectiveness
        assert effectiveness["prompt_injection"] == 1.0  # Success in top-5
        assert effectiveness["persuasion"] == 1.0

    def test_ranking_diversity(self, sample_attack_results):
        diversity = MetricCalculator.ranking_diversity(sample_attack_results, top_k=5)
        assert 0 <= diversity <= 1

    def test_ranking_diversity_empty(self):
        diversity = MetricCalculator.ranking_diversity([])
        assert diversity == 0.0

    def test_ranking_consistency(self, sample_attack_results):
        consistency = MetricCalculator.ranking_consistency(
            sample_attack_results,
            top_k=5
        )
        assert 0 <= consistency <= 1

    def test_positional_bias_score(self, sample_attack_results):
        scores = MetricCalculator.positional_bias_score(sample_attack_results)
        assert "position_end" in scores
        assert "position_middle" in scores
        # 2 at 'end' position, both successful at position-1
        assert scores["position_end"] == 1.0
        # 1 at 'middle' position, not at position-1
        assert scores["position_middle"] == 0.0

    def test_calculate_statistics(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        stats = MetricCalculator.calculate_statistics(values)
        assert stats["mean"] == 3.0
        assert stats["median"] == 3.0
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["count"] == 5

    def test_calculate_statistics_empty(self):
        stats = MetricCalculator.calculate_statistics([])
        assert stats == {}


# Test AttackEffectivenessEvaluator
class TestAttackEffectivenessEvaluator:
    def test_evaluate_with_attacks(
        self,
        sample_baseline_results,
        sample_attack_results
    ):
        evaluator = AttackEffectivenessEvaluator(top_k=5)
        combined = sample_baseline_results + sample_attack_results
        result = evaluator.evaluate(combined)

        assert result.passed is True
        assert "success_rate" in result.metrics
        assert "position_1_rate" in result.metrics
        assert "mean_rank_attack" in result.metrics
        assert "mean_rank_baseline" in result.metrics
        assert "rank_improvement" in result.metrics

        # Check specific values
        assert result.metrics["success_rate"] == 1.0  # All in top-5
        assert result.metrics["position_1_rate"] == pytest.approx(2/3, abs=0.01)

    def test_evaluate_no_attacks(self, sample_baseline_results):
        evaluator = AttackEffectivenessEvaluator()
        result = evaluator.evaluate(sample_baseline_results)

        assert result.passed is False
        assert len(result.errors) > 0
        assert "No attack results" in result.errors[0]

    def test_evaluate_low_success_warning(self):
        # Create results with low success rate
        low_success_results = [
            {
                "has_attack": True,
                "attacked_product": "prod-1",
                "ranked_products": [
                    {"id": "prod-2", "score": 0.95},
                    {"id": "prod-3", "score": 0.90},
                    {"id": "prod-4", "score": 0.85},
                    {"id": "prod-5", "score": 0.80},
                    {"id": "prod-6", "score": 0.75},
                    {"id": "prod-1", "score": 0.70},  # Low rank
                ]
            }
        ] * 5

        evaluator = AttackEffectivenessEvaluator(top_k=5)
        result = evaluator.evaluate(low_success_results)

        assert result.passed is True  # No errors, but warnings
        assert len(result.warnings) > 0
        assert any("success rate" in w.lower() for w in result.warnings)

    def test_attack_type_breakdown(self, sample_attack_results):
        evaluator = AttackEffectivenessEvaluator()
        result = evaluator.evaluate(sample_attack_results)

        assert "success_rate_prompt_injection" in result.metrics
        assert "success_rate_discreditation" in result.metrics
        assert "success_rate_persuasion" in result.metrics


# Test PaperComparisonEvaluator
class TestPaperComparisonEvaluator:
    def test_within_paper_range(self):
        # Create results within paper's 25-60% range
        results = []
        for i in range(100):
            # 40% success rate (within range)
            is_success = i < 40
            results.append({
                "has_attack": True,
                "attacked_product": "prod-1",
                "ranked_products": [
                    {"id": "prod-1" if is_success else "prod-2", "score": 0.95},
                    {"id": "prod-2", "score": 0.90},
                ]
            })

        evaluator = PaperComparisonEvaluator()
        result = evaluator.evaluate(results)

        assert result.passed is True
        assert result.metrics["within_paper_range"] == 1.0
        assert len(result.warnings) == 0

    def test_outside_paper_range_low(self):
        # Create results below paper's range
        results = []
        for i in range(100):
            # 20% success rate (below 25%)
            is_success = i < 20
            results.append({
                "has_attack": True,
                "attacked_product": "prod-1",
                "ranked_products": [
                    {"id": "prod-1" if is_success else "prod-2", "score": 0.95},
                    {"id": "prod-2", "score": 0.90},
                ]
            })

        evaluator = PaperComparisonEvaluator()
        result = evaluator.evaluate(results)

        assert result.metrics["within_paper_range"] == 0.0
        assert len(result.warnings) > 0
        assert any("below paper's range" in w.lower() for w in result.warnings)

    def test_position_1_deviation(self):
        # Create results matching paper's 38% position-1 rate
        results = []
        for i in range(100):
            is_success = i < 38
            results.append({
                "has_attack": True,
                "attacked_product": "prod-1",
                "ranked_products": [
                    {"id": "prod-1" if is_success else "prod-2", "score": 0.95},
                    {"id": "prod-2", "score": 0.90},
                ]
            })

        evaluator = PaperComparisonEvaluator(tolerance=0.05)
        result = evaluator.evaluate(results)

        assert result.metrics["within_tolerance"] == 1.0
        assert result.metrics["position_1_deviation"] == pytest.approx(0.0, abs=0.01)

    def test_no_attacks_error(self, sample_baseline_results):
        evaluator = PaperComparisonEvaluator()
        result = evaluator.evaluate(sample_baseline_results)

        assert result.passed is False
        assert len(result.errors) > 0


# Test RankingQualityEvaluator
class TestRankingQualityEvaluator:
    def test_evaluate_quality(
        self,
        sample_baseline_results,
        sample_attack_results
    ):
        evaluator = RankingQualityEvaluator(top_k=5)
        combined = sample_baseline_results + sample_attack_results
        result = evaluator.evaluate(combined)

        assert result.passed is True
        assert "ranking_diversity" in result.metrics
        assert "ranking_consistency" in result.metrics
        assert "diversity_baseline" in result.metrics
        assert "diversity_attack" in result.metrics

    def test_low_diversity_warning(self):
        # Create results with low diversity (only one unique product in top-K)
        low_diversity_results = [
            {
                "ranked_products": [
                    {"id": "prod-1", "score": 0.95},  # Always the same product
                ]
            }
        ] * 10

        evaluator = RankingQualityEvaluator(top_k=1)
        result = evaluator.evaluate(low_diversity_results)

        assert len(result.warnings) > 0
        assert any("diversity" in w.lower() for w in result.warnings)


# Test ResultAggregator
class TestResultAggregator:
    def test_aggregate_multiple_results(self):
        results = [
            EvaluationResult(
                evaluator_name="Test1",
                metrics={"accuracy": 0.9, "precision": 0.85}
            ),
            EvaluationResult(
                evaluator_name="Test1",
                metrics={"accuracy": 0.95, "precision": 0.90}
            ),
            EvaluationResult(
                evaluator_name="Test1",
                metrics={"accuracy": 0.92, "precision": 0.88}
            ),
        ]

        agg = ResultAggregator.aggregate(results)

        assert "accuracy_mean" in agg
        assert "accuracy_std" in agg
        assert "accuracy_min" in agg
        assert "accuracy_max" in agg
        assert agg["accuracy_mean"] == pytest.approx(0.923, abs=0.01)
        assert agg["total_results"] == 3
        assert agg["pass_rate"] == 1.0

    def test_aggregate_with_failures(self):
        results = [
            EvaluationResult(
                evaluator_name="Test1",
                metrics={"accuracy": 0.9}
            ),
            EvaluationResult(
                evaluator_name="Test1",
                metrics={"accuracy": 0.8},
                passed=False
            ),
        ]
        results[1].add_error("Test error")

        agg = ResultAggregator.aggregate(results)

        assert agg["passed_count"] == 1
        assert agg["failed_count"] == 1
        assert agg["pass_rate"] == 0.5
        assert agg["total_errors"] == 1

    def test_combine_by_evaluator(self):
        results = [
            EvaluationResult(
                evaluator_name="Evaluator1",
                metrics={"accuracy": 0.9}
            ),
            EvaluationResult(
                evaluator_name="Evaluator2",
                metrics={"accuracy": 0.85}
            ),
            EvaluationResult(
                evaluator_name="Evaluator1",
                metrics={"accuracy": 0.95}
            ),
        ]

        by_eval = ResultAggregator.combine_by_evaluator(results)

        assert "Evaluator1" in by_eval
        assert "Evaluator2" in by_eval
        assert by_eval["Evaluator1"]["total_results"] == 2
        assert by_eval["Evaluator2"]["total_results"] == 1

    def test_summary_report(self):
        results = [
            EvaluationResult(
                evaluator_name="Test1",
                metrics={"accuracy": 0.9}
            ),
            EvaluationResult(
                evaluator_name="Test1",
                metrics={"accuracy": 0.95}
            ),
        ]

        report = ResultAggregator.summary_report(results)

        assert "EVALUATION SUMMARY REPORT" in report
        assert "Total Results: 2" in report
        assert "Test1" in report

    def test_empty_results(self):
        agg = ResultAggregator.aggregate([])
        assert agg == {}

        report = ResultAggregator.summary_report([])
        assert "No results" in report


# Test MetricAggregator
class TestMetricAggregator:
    def test_compute_statistics(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        stats = MetricAggregator.compute_statistics(values)

        assert stats["mean"] == 3.0
        assert stats["std"] == pytest.approx(1.414, abs=0.01)
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["median"] == 3.0
        assert stats["q25"] == 2.0
        assert stats["q75"] == 4.0
        assert stats["iqr"] == 2.0

    def test_confidence_interval(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        ci = MetricAggregator.confidence_interval(values, confidence=0.95)

        assert "mean" in ci
        assert "sem" in ci
        assert "ci_lower" in ci
        assert "ci_upper" in ci
        assert ci["ci_lower"] < ci["mean"] < ci["ci_upper"]

    def test_compare_distributions(self):
        baseline = [1.0, 2.0, 3.0, 4.0, 5.0]
        treatment = [3.0, 4.0, 5.0, 6.0, 7.0]  # Higher mean

        comparison = MetricAggregator.compare_distributions(baseline, treatment)

        assert comparison["baseline_mean"] == 3.0
        assert comparison["treatment_mean"] == 5.0
        assert comparison["difference"] == 2.0
        assert "t_statistic" in comparison
        assert "t_pvalue" in comparison
        assert "cohens_d" in comparison
        assert comparison["cohens_d"] > 0  # Treatment has higher mean

    def test_empty_values(self):
        stats = MetricAggregator.compute_statistics([])
        assert stats == {}

        ci = MetricAggregator.confidence_interval([])
        assert ci == {}

        comparison = MetricAggregator.compare_distributions([], [1, 2, 3])
        assert comparison == {}


# Integration tests
class TestEvaluationIntegration:
    def test_full_evaluation_pipeline(
        self,
        sample_baseline_results,
        sample_attack_results
    ):
        """Test complete evaluation pipeline with multiple evaluators."""
        combined = sample_baseline_results + sample_attack_results

        # Run all evaluators
        effectiveness = AttackEffectivenessEvaluator()
        paper_comp = PaperComparisonEvaluator()
        quality = RankingQualityEvaluator()

        results = [
            effectiveness.evaluate(combined),
            paper_comp.evaluate(combined),
            quality.evaluate(combined),
        ]

        # Aggregate results
        aggregated = ResultAggregator.aggregate(results)

        assert aggregated["total_results"] == 3
        assert aggregated["pass_rate"] >= 0.66  # At least 2/3 should pass

        # Generate report
        report = ResultAggregator.summary_report(results)
        assert "AttackEffectivenessEvaluator" in report
        assert "PaperComparisonEvaluator" in report
        assert "RankingQualityEvaluator" in report

    def test_multiple_runs_aggregation(self, sample_attack_results):
        """Test aggregating results from multiple runs."""
        evaluator = AttackEffectivenessEvaluator()

        # Simulate multiple runs
        all_results = []
        for _ in range(5):
            result = evaluator.evaluate(sample_attack_results)
            all_results.append(result)

        # Aggregate
        aggregated = ResultAggregator.aggregate(all_results)

        assert aggregated["total_results"] == 5
        assert "success_rate_mean" in aggregated
        assert "success_rate_std" in aggregated
