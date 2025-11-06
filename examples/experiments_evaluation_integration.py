"""
Integration example: Using evaluation package with experiments package.

This demonstrates the complete workflow from experiment execution to
comprehensive evaluation and reporting.
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


def simulate_experiment_results():
    """
    Simulate results from an experiment run.

    In practice, this would come from:
        from src.experiments import ExperimentRunner, ExperimentConfig
        result = ExperimentRunner.run_experiment(config)
        return result.trials
    """
    import random
    random.seed(42)

    results = []

    # Baseline trials (no attacks)
    print("Simulating baseline trials...")
    for trial in range(20):
        results.append({
            "trial_id": f"baseline_{trial}",
            "has_attack": False,
            "attacked_product": "laptop-42",
            "ranked_products": [
                {"id": "laptop-10", "score": 0.92},
                {"id": "laptop-15", "score": 0.88},
                {"id": "laptop-42", "score": 0.85},  # Target at position 3
                {"id": "laptop-03", "score": 0.82},
                {"id": "laptop-07", "score": 0.78},
            ]
        })

    # Attack trials with varying success
    print("Simulating attack trials...")
    attack_types = ["prompt_injection", "discreditation", "persuasion"]
    positions = ["beginning", "middle", "end"]

    for trial in range(50):
        attack_type = attack_types[trial % 3]
        position = positions[trial % 3]

        # Simulate position-dependent effectiveness (end position more effective)
        success_prob = 0.7 if position == "end" else (0.5 if position == "middle" else 0.3)
        is_successful = random.random() < success_prob

        if is_successful:
            # Target reaches top position
            ranked = [
                {"id": "laptop-42", "score": 0.96},  # Target promoted
                {"id": "laptop-10", "score": 0.91},
                {"id": "laptop-15", "score": 0.87},
                {"id": "laptop-03", "score": 0.81},
                {"id": "laptop-07", "score": 0.77},
            ]
        else:
            # Target stays at lower position
            ranked = [
                {"id": "laptop-10", "score": 0.93},
                {"id": "laptop-15", "score": 0.89},
                {"id": "laptop-03", "score": 0.86},
                {"id": "laptop-42", "score": 0.84},  # Target at position 4
                {"id": "laptop-07", "score": 0.79},
            ]

        results.append({
            "trial_id": f"attack_{trial}",
            "has_attack": True,
            "attacked_product": "laptop-42",
            "attack_type": attack_type,
            "attack_position": position,
            "ranked_products": ranked,
            "top_k_ids": [p["id"] for p in ranked[:5]]
        })

    return results


def main():
    """Demonstrate complete experiment-evaluation workflow."""

    print("=" * 80)
    print("EXPERIMENT-EVALUATION INTEGRATION DEMONSTRATION")
    print("=" * 80)
    print()

    # Step 1: Run experiment (simulated)
    print("Step 1: Running experiment...")
    print("-" * 80)
    experiment_results = simulate_experiment_results()

    baseline_count = sum(1 for r in experiment_results if not r.get("has_attack"))
    attack_count = sum(1 for r in experiment_results if r.get("has_attack"))

    print(f"Experiment completed:")
    print(f"  - Baseline trials: {baseline_count}")
    print(f"  - Attack trials: {attack_count}")
    print(f"  - Total trials: {len(experiment_results)}")
    print()

    # Step 2: Evaluate attack effectiveness
    print("Step 2: Evaluating attack effectiveness...")
    print("-" * 80)
    effectiveness_eval = AttackEffectivenessEvaluator(top_k=5)
    effectiveness_result = effectiveness_eval.evaluate(experiment_results)

    print(f"Attack Effectiveness Results:")
    print(f"  - Success Rate (top-5): {effectiveness_result.metrics['success_rate']:.1%}")
    print(f"  - Position-1 Rate: {effectiveness_result.metrics['position_1_rate']:.1%}")
    print(f"  - Mean Rank (baseline): {effectiveness_result.metrics['mean_rank_baseline']:.2f}")
    print(f"  - Mean Rank (attack): {effectiveness_result.metrics['mean_rank_attack']:.2f}")
    print(f"  - Rank Improvement: {effectiveness_result.metrics['rank_improvement']:.2f} positions")

    print(f"\nAttack Type Breakdown:")
    for attack_type in ["prompt_injection", "discreditation", "persuasion"]:
        key = f"success_rate_{attack_type}"
        if key in effectiveness_result.metrics:
            print(f"  - {attack_type}: {effectiveness_result.metrics[key]:.1%}")

    print(f"\nPositional Bias Analysis:")
    for position in ["beginning", "middle", "end"]:
        key = f"position_{position}"
        if key in effectiveness_result.metrics:
            print(f"  - {position}: {effectiveness_result.metrics[key]:.1%}")
    print()

    # Step 3: Compare to paper findings
    print("Step 3: Comparing to paper findings...")
    print("-" * 80)
    paper_eval = PaperComparisonEvaluator(tolerance=0.10)
    paper_result = paper_eval.evaluate(experiment_results)

    print(f"Paper Comparison Results:")
    print(f"  - Our Success Rate: {paper_result.metrics['our_success_rate']:.1%}")
    print(f"  - Paper Range: {paper_result.metrics['paper_success_rate_min']:.0%}-{paper_result.metrics['paper_success_rate_max']:.0%}")
    print(f"  - Within Range: {'YES' if paper_result.metrics['within_paper_range'] else 'NO'}")
    print()
    print(f"  - Our Position-1 Rate: {paper_result.metrics['our_position_1_rate']:.1%}")
    print(f"  - Paper Average: {paper_result.metrics['paper_position_1_avg']:.1%}")
    print(f"  - Deviation: {paper_result.metrics['position_1_deviation']:.1%}")
    print(f"  - Within Tolerance: {'YES' if paper_result.metrics['within_tolerance'] else 'NO'}")

    if paper_result.warnings:
        print(f"\nWarnings:")
        for warning in paper_result.warnings:
            print(f"  - {warning}")
    print()

    # Step 4: Assess ranking quality
    print("Step 4: Assessing ranking quality...")
    print("-" * 80)
    quality_eval = RankingQualityEvaluator(top_k=5)
    quality_result = quality_eval.evaluate(experiment_results)

    print(f"Ranking Quality Results:")
    print(f"  - Overall Diversity: {quality_result.metrics['ranking_diversity']:.3f}")
    print(f"  - Overall Consistency: {quality_result.metrics['ranking_consistency']:.3f}")

    if "diversity_change" in quality_result.metrics:
        print(f"\nBaseline vs. Attack Comparison:")
        print(f"  - Diversity Change: {quality_result.metrics['diversity_change']:+.3f}")
        print(f"  - Consistency Change: {quality_result.metrics['consistency_change']:+.3f}")
    print()

    # Step 5: Aggregate all results
    print("Step 5: Aggregating evaluation results...")
    print("-" * 80)
    all_results = [effectiveness_result, paper_result, quality_result]
    aggregated = ResultAggregator.aggregate(all_results)

    print(f"Aggregate Summary:")
    print(f"  - Total Evaluators: {aggregated['total_results']}")
    print(f"  - Pass Rate: {aggregated['pass_rate']:.1%}")
    print(f"  - Total Warnings: {aggregated['total_warnings']}")
    print(f"  - Total Errors: {aggregated['total_errors']}")
    print()

    # Step 6: Generate comprehensive report
    print("Step 6: Generating comprehensive report...")
    print("-" * 80)
    report = ResultAggregator.summary_report(all_results)
    print(report)
    print()

    # Step 7: Statistical analysis across multiple runs (simulated)
    print("Step 7: Statistical analysis across multiple runs...")
    print("-" * 80)

    # Simulate multiple experiment runs
    print("Simulating 5 experiment runs...")
    run_results = []
    for run_id in range(5):
        # In practice: run_results.append(ExperimentRunner.run_experiment(config))
        run_data = simulate_experiment_results()
        run_eval = effectiveness_eval.evaluate(run_data)
        run_results.append(run_eval)

    # Aggregate across runs
    multi_run_agg = ResultAggregator.aggregate(run_results)

    print(f"\nCross-Run Statistics:")
    print(f"  - Mean Success Rate: {multi_run_agg['success_rate_mean']:.1%} ± {multi_run_agg['success_rate_std']:.3f}")
    print(f"  - Success Rate Range: {multi_run_agg['success_rate_min']:.1%} - {multi_run_agg['success_rate_max']:.1%}")
    print(f"  - Mean Position-1 Rate: {multi_run_agg['position_1_rate_mean']:.1%} ± {multi_run_agg['position_1_rate_std']:.3f}")
    print(f"  - Mean Rank Improvement: {multi_run_agg['rank_improvement_mean']:.2f} ± {multi_run_agg['rank_improvement_std']:.2f}")

    # Extract values for detailed statistical analysis
    success_rates = [r.metrics['success_rate'] for r in run_results]
    position_1_rates = [r.metrics['position_1_rate'] for r in run_results]

    # Compute confidence intervals
    success_ci = MetricAggregator.confidence_interval(success_rates, confidence=0.95)
    position1_ci = MetricAggregator.confidence_interval(position_1_rates, confidence=0.95)

    print(f"\n95% Confidence Intervals:")
    print(f"  - Success Rate: [{success_ci['ci_lower']:.1%}, {success_ci['ci_upper']:.1%}]")
    print(f"  - Position-1 Rate: [{position1_ci['ci_lower']:.1%}, {position1_ci['ci_upper']:.1%}]")
    print()

    # Step 8: Export results (demonstration)
    print("Step 8: Exporting results...")
    print("-" * 80)

    # Convert to dictionary format for export
    export_data = {
        "experiment_metadata": {
            "total_trials": len(experiment_results),
            "baseline_trials": baseline_count,
            "attack_trials": attack_count,
        },
        "effectiveness_metrics": effectiveness_result.metrics,
        "paper_comparison": paper_result.metrics,
        "quality_metrics": quality_result.metrics,
        "multi_run_statistics": {
            "runs": len(run_results),
            "success_rate_mean": multi_run_agg['success_rate_mean'],
            "success_rate_ci": [success_ci['ci_lower'], success_ci['ci_upper']],
            "position_1_rate_mean": multi_run_agg['position_1_rate_mean'],
            "position_1_ci": [position1_ci['ci_lower'], position1_ci['ci_upper']],
        }
    }

    print(f"Results ready for export:")
    print(f"  - Format: JSON/CSV/XLSX")
    print(f"  - Sections: 4 (metadata, effectiveness, paper comparison, quality)")
    print(f"  - Multi-run statistics included")
    print()

    # Example: Save to JSON (commented out to avoid file creation)
    # import json
    # with open('experiment_evaluation_results.json', 'w') as f:
    #     json.dump(export_data, f, indent=2)
    # print("  - Saved to: experiment_evaluation_results.json")

    print("=" * 80)
    print("INTEGRATION DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("Key Takeaways:")
    print("  1. Evaluation package integrates seamlessly with experiments")
    print("  2. Multiple evaluators provide comprehensive assessment")
    print("  3. Results can be aggregated across trials and runs")
    print("  4. Statistical analysis supports research validity")
    print("  5. Export-ready format for reporting and visualization")
    print()


if __name__ == "__main__":
    main()
