"""
Demonstration of the evaluation package.

This script shows how to use all evaluators to measure attack effectiveness,
compare results to paper findings, and assess ranking quality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.evaluation import (
    AttackEffectivenessEvaluator,
    PaperComparisonEvaluator,
    RankingQualityEvaluator,
    ResultAggregator,
    MetricAggregator,
)


def create_sample_data():
    """Create sample experimental data for demonstration."""
    # Baseline results (no attacks)
    baseline = [
        {
            "has_attack": False,
            "attacked_product": "book-1",
            "ranked_products": [
                {"id": "book-3", "score": 0.92},
                {"id": "book-2", "score": 0.88},
                {"id": "book-1", "score": 0.85},  # Target at position 3
                {"id": "book-4", "score": 0.82},
                {"id": "book-5", "score": 0.78},
            ]
        }
        for _ in range(10)
    ]

    # Attack results (with attacks)
    attack_results = []

    # Successful attacks (60% success rate)
    for i in range(6):
        attack_results.append({
            "has_attack": True,
            "attacked_product": "book-1",
            "attack_type": "prompt_injection" if i < 3 else "persuasion",
            "attack_position": "end" if i < 4 else "middle",
            "ranked_products": [
                {"id": "book-1", "score": 0.96},  # Target at position 1
                {"id": "book-2", "score": 0.90},
                {"id": "book-3", "score": 0.86},
                {"id": "book-4", "score": 0.82},
                {"id": "book-5", "score": 0.78},
            ],
            "top_k_ids": ["book-1", "book-2", "book-3", "book-4", "book-5"]
        })

    # Failed attacks (40% fail rate)
    for i in range(4):
        attack_results.append({
            "has_attack": True,
            "attacked_product": "book-1",
            "attack_type": "discreditation",
            "attack_position": "middle",
            "ranked_products": [
                {"id": "book-2", "score": 0.91},
                {"id": "book-3", "score": 0.88},
                {"id": "book-1", "score": 0.86},  # Target at position 3
                {"id": "book-4", "score": 0.81},
                {"id": "book-5", "score": 0.77},
            ],
            "top_k_ids": ["book-2", "book-3", "book-1", "book-4", "book-5"]
        })

    return baseline + attack_results


def main():
    """Demonstrate evaluation package usage."""
    print("=" * 70)
    print("EVALUATION PACKAGE DEMONSTRATION")
    print("=" * 70)
    print()

    # Create sample data
    data = create_sample_data()
    print(f"Created sample data: {len([d for d in data if not d.get('has_attack')])} baseline trials, "
          f"{len([d for d in data if d.get('has_attack')])} attack trials")
    print()

    # 1. Attack Effectiveness Evaluation
    print("-" * 70)
    print("1. ATTACK EFFECTIVENESS EVALUATION")
    print("-" * 70)
    effectiveness_eval = AttackEffectivenessEvaluator(top_k=5)
    effectiveness_result = effectiveness_eval.evaluate(data)

    print(f"Evaluator: {effectiveness_result.evaluator_name}")
    print(f"Status: {'PASSED' if effectiveness_result.passed else 'FAILED'}")
    print(f"\nKey Metrics:")
    print(f"  Success Rate (top-5): {effectiveness_result.metrics['success_rate']:.1%}")
    print(f"  Position-1 Rate: {effectiveness_result.metrics['position_1_rate']:.1%}")
    print(f"  Mean Rank (baseline): {effectiveness_result.metrics['mean_rank_baseline']:.2f}")
    print(f"  Mean Rank (attack): {effectiveness_result.metrics['mean_rank_attack']:.2f}")
    print(f"  Rank Improvement: {effectiveness_result.metrics['rank_improvement']:.2f} positions")

    # Show attack type breakdown
    print(f"\nAttack Type Breakdown:")
    for key, value in effectiveness_result.metrics.items():
        if key.startswith("success_rate_") and key != "success_rate":
            attack_type = key.replace("success_rate_", "")
            print(f"  {attack_type}: {value:.1%}")

    # Show positional bias
    print(f"\nPositional Bias:")
    for key, value in effectiveness_result.metrics.items():
        if key.startswith("position_"):
            print(f"  {key}: {value:.1%}")

    if effectiveness_result.warnings:
        print(f"\nWarnings:")
        for warning in effectiveness_result.warnings:
            print(f"  - {warning}")
    print()

    # 2. Paper Comparison Evaluation
    print("-" * 70)
    print("2. PAPER COMPARISON EVALUATION")
    print("-" * 70)
    paper_eval = PaperComparisonEvaluator(tolerance=0.10)
    paper_result = paper_eval.evaluate(data)

    print(f"Evaluator: {paper_result.evaluator_name}")
    print(f"Status: {'PASSED' if paper_result.passed else 'FAILED'}")
    print(f"\nComparison with Nestaas et al., 2024:")
    print(f"  Our Position-1 Rate: {paper_result.metrics['our_position_1_rate']:.1%}")
    print(f"  Paper Position-1 Avg: {paper_result.metrics['paper_position_1_avg']:.1%}")
    print(f"  Deviation: {paper_result.metrics['position_1_deviation']:.1%}")
    print(f"  Within Tolerance: {'YES' if paper_result.metrics['within_tolerance'] else 'NO'}")
    print(f"\n  Paper Success Range: {paper_result.metrics['paper_success_rate_min']:.0%}-{paper_result.metrics['paper_success_rate_max']:.0%}")
    print(f"  Our Success Rate: {paper_result.metrics['our_success_rate']:.1%}")
    print(f"  Within Paper Range: {'YES' if paper_result.metrics['within_paper_range'] else 'NO'}")

    if paper_result.warnings:
        print(f"\nWarnings:")
        for warning in paper_result.warnings:
            print(f"  - {warning}")
    print()

    # 3. Ranking Quality Evaluation
    print("-" * 70)
    print("3. RANKING QUALITY EVALUATION")
    print("-" * 70)
    quality_eval = RankingQualityEvaluator(top_k=5)
    quality_result = quality_eval.evaluate(data)

    print(f"Evaluator: {quality_result.evaluator_name}")
    print(f"Status: {'PASSED' if quality_result.passed else 'FAILED'}")
    print(f"\nQuality Metrics:")
    print(f"  Overall Diversity: {quality_result.metrics['ranking_diversity']:.3f}")
    print(f"  Overall Consistency: {quality_result.metrics['ranking_consistency']:.3f}")

    if "diversity_baseline" in quality_result.metrics:
        print(f"\n  Baseline Diversity: {quality_result.metrics['diversity_baseline']:.3f}")
        print(f"  Attack Diversity: {quality_result.metrics['diversity_attack']:.3f}")
        print(f"  Diversity Change: {quality_result.metrics['diversity_change']:+.3f}")
        print(f"\n  Baseline Consistency: {quality_result.metrics['consistency_baseline']:.3f}")
        print(f"  Attack Consistency: {quality_result.metrics['consistency_attack']:.3f}")
        print(f"  Consistency Change: {quality_result.metrics['consistency_change']:+.3f}")

    if quality_result.warnings:
        print(f"\nWarnings:")
        for warning in quality_result.warnings:
            print(f"  - {warning}")
    print()

    # 4. Result Aggregation
    print("-" * 70)
    print("4. RESULT AGGREGATION")
    print("-" * 70)
    all_results = [effectiveness_result, paper_result, quality_result]

    # Aggregate results
    aggregated = ResultAggregator.aggregate(all_results)
    print(f"Aggregated Results from {aggregated['total_results']} evaluators:")
    print(f"  Passed: {aggregated['passed_count']}/{aggregated['total_results']} ({aggregated['pass_rate']:.1%})")
    print(f"  Total Errors: {aggregated['total_errors']}")
    print(f"  Total Warnings: {aggregated['total_warnings']}")
    print()

    # By evaluator
    by_evaluator = ResultAggregator.combine_by_evaluator(all_results)
    print("Results by Evaluator:")
    for evaluator_name, metrics in by_evaluator.items():
        print(f"\n  {evaluator_name}:")
        print(f"    Pass Rate: {metrics['pass_rate']:.1%}")
        print(f"    Errors: {metrics['total_errors']}")
        print(f"    Warnings: {metrics['total_warnings']}")
    print()

    # 5. Summary Report
    print("-" * 70)
    print("5. SUMMARY REPORT")
    print("-" * 70)
    summary = ResultAggregator.summary_report(all_results)
    print(summary)
    print()

    # 6. Metric Aggregation (Statistical Analysis)
    print("-" * 70)
    print("6. STATISTICAL ANALYSIS")
    print("-" * 70)

    # Extract success rates for analysis
    success_rates = [0.6, 0.58, 0.62, 0.55, 0.61, 0.59]  # Example rates from multiple runs
    stats = MetricAggregator.compute_statistics(success_rates)

    print("Success Rate Statistics (across multiple runs):")
    print(f"  Mean: {stats['mean']:.1%}")
    print(f"  Std Dev: {stats['std']:.3f}")
    print(f"  Median: {stats['median']:.1%}")
    print(f"  Range: {stats['min']:.1%} - {stats['max']:.1%}")
    print(f"  IQR: {stats['iqr']:.3f}")
    print()

    # Confidence interval
    ci = MetricAggregator.confidence_interval(success_rates, confidence=0.95)
    print("95% Confidence Interval:")
    print(f"  Mean: {ci['mean']:.1%}")
    print(f"  CI: [{ci['ci_lower']:.1%}, {ci['ci_upper']:.1%}]")
    print()

    # Compare distributions
    baseline_ranks = [3.2, 3.0, 3.1, 2.9, 3.3]
    attack_ranks = [1.5, 1.3, 1.6, 1.4, 1.7]
    comparison = MetricAggregator.compare_distributions(baseline_ranks, attack_ranks)

    print("Rank Distribution Comparison:")
    print(f"  Baseline Mean Rank: {comparison['baseline_mean']:.2f}")
    print(f"  Attack Mean Rank: {comparison['treatment_mean']:.2f}")
    print(f"  Difference: {comparison['difference']:.2f}")
    print(f"  Cohen's d (effect size): {comparison['cohens_d']:.3f}")
    print(f"  t-test p-value: {comparison['t_pvalue']:.4f}")
    print(f"  Significant at α=0.05: {'YES' if comparison['significant_at_05'] else 'NO'}")
    print(f"  Significant at α=0.01: {'YES' if comparison['significant_at_01'] else 'NO'}")
    print()

    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
