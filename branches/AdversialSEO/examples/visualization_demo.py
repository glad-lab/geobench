#!/usr/bin/env python3
"""
Demonstration of unified visualization package.

Shows how to use the refactored visualization system for creating
publication-quality charts and comprehensive reports.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.visualization import (
    AttackVisualizer,
    ComparisonVisualizer,
    ReportGenerator,
    VisualizationConfig
)


def demo_attack_visualizations():
    """Demonstrate attack visualization capabilities."""
    print("\n" + "="*60)
    print("ATTACK VISUALIZATIONS DEMO")
    print("="*60)

    # Initialize visualizer
    config = VisualizationConfig(figsize=(12, 8), dpi=150)
    viz = AttackVisualizer(config)

    # Example 1: Success rates by attack type
    print("\n1. Creating success rates chart...")
    success_rates = {
        'prompt_injection': 0.45,
        'discreditation': 0.32,
        'persuasion': 0.38
    }

    fig = viz.plot_success_rates(
        success_rates,
        title="Attack Success Rates by Type",
        save_path="outputs/success_rates.png"
    )
    print("   ✓ Saved to outputs/success_rates.png")

    # Example 2: Positional bias
    print("\n2. Creating positional bias chart...")
    positional_data = {1: 0.25, 5: 0.38, 10: 0.52}

    fig = viz.plot_positional_bias(
        positional_data,
        title="Attack Effectiveness by Position",
        save_path="outputs/positional_bias.png"
    )
    print("   ✓ Saved to outputs/positional_bias.png")

    # Example 3: Rank distribution
    print("\n3. Creating rank distribution...")
    ranks = [1, 1, 2, 3, 1, 2, 4, 5, 2, 1, 3, 2, 1, 6, 4]

    fig = viz.plot_rank_distribution(
        ranks,
        title="Target Product Rank Distribution",
        save_path="outputs/rank_distribution.png"
    )
    print("   ✓ Saved to outputs/rank_distribution.png")

    # Example 4: Prisoner's dilemma
    print("\n4. Creating prisoner's dilemma chart...")
    collective_perf = {0: 1.0, 1: 0.85, 2: 0.68, 3: 0.52, 4: 0.41}

    fig = viz.plot_prisoners_dilemma(
        collective_perf,
        save_path="outputs/prisoners_dilemma.png"
    )
    print("   ✓ Saved to outputs/prisoners_dilemma.png")


def demo_comparison_visualizations():
    """Demonstrate cross-provider comparison visualizations."""
    print("\n" + "="*60)
    print("CROSS-PROVIDER COMPARISON DEMO")
    print("="*60)

    # Initialize visualizer
    viz = ComparisonVisualizer()

    # Example 1: Provider comparison
    print("\n1. Creating provider performance comparison...")
    provider_results = {
        'openai': {
            'success_rate': 0.45,
            'avg_response_time': 1.2,
            'error_rate': 0.05,
            'avg_position_change': 2.3,
            'attack_type_breakdown': {
                'prompt_injection': {'success_rate': 0.50},
                'discreditation': {'success_rate': 0.35},
                'persuasion': {'success_rate': 0.40}
            }
        },
        'anthropic': {
            'success_rate': 0.52,
            'avg_response_time': 0.8,
            'error_rate': 0.03,
            'avg_position_change': 2.8,
            'attack_type_breakdown': {
                'prompt_injection': {'success_rate': 0.55},
                'discreditation': {'success_rate': 0.45},
                'persuasion': {'success_rate': 0.48}
            }
        },
        'bedrock': {
            'success_rate': 0.38,
            'avg_response_time': 1.5,
            'error_rate': 0.08,
            'avg_position_change': 1.9,
            'attack_type_breakdown': {
                'prompt_injection': {'success_rate': 0.42},
                'discreditation': {'success_rate': 0.30},
                'persuasion': {'success_rate': 0.35}
            }
        }
    }

    fig = viz.plot_provider_comparison(
        provider_results,
        save_path="outputs/provider_comparison.png"
    )
    print("   ✓ Saved to outputs/provider_comparison.png")

    # Example 2: Transferability heatmap
    print("\n2. Creating transferability heatmap...")
    transferability = {
        'openai': {'prompt_injection': 0.50, 'discreditation': 0.35, 'persuasion': 0.40},
        'anthropic': {'prompt_injection': 0.55, 'discreditation': 0.45, 'persuasion': 0.48},
        'bedrock': {'prompt_injection': 0.42, 'discreditation': 0.30, 'persuasion': 0.35}
    }

    fig = viz.plot_transferability_heatmap(
        transferability,
        save_path="outputs/transferability_heatmap.png"
    )
    print("   ✓ Saved to outputs/transferability_heatmap.png")

    # Example 3: Attack type effectiveness
    print("\n3. Creating attack type effectiveness comparison...")
    fig = viz.plot_attack_type_effectiveness(
        provider_results,
        save_path="outputs/attack_type_effectiveness.png"
    )
    print("   ✓ Saved to outputs/attack_type_effectiveness.png")


def demo_report_generation():
    """Demonstrate automated report generation."""
    print("\n" + "="*60)
    print("AUTOMATED REPORT GENERATION DEMO")
    print("="*60)

    # Initialize generator
    generator = ReportGenerator(output_dir="outputs/reports")

    # Example 1: Attack effectiveness report
    print("\n1. Generating attack effectiveness report...")
    attack_results = [
        {
            'query': 'best laptop for students',
            'attack_type': 'prompt_injection',
            'attack_docs_retrieved': 2,
            'total_docs': 5,
            'true_effectiveness': 0.45,
            'final_rank': 1
        },
        {
            'query': 'affordable smartphones',
            'attack_type': 'discreditation',
            'attack_docs_retrieved': 1,
            'total_docs': 5,
            'true_effectiveness': 0.32,
            'final_rank': 2
        },
        {
            'query': 'wireless earbuds review',
            'attack_type': 'persuasion',
            'attack_docs_retrieved': 3,
            'total_docs': 5,
            'true_effectiveness': 0.38,
            'final_rank': 1
        }
    ]

    saved_paths = generator.generate_attack_report(
        attack_results,
        report_name="demo_attack_report",
        formats=['png']
    )
    print(f"   ✓ Generated {len(saved_paths)} figures")
    print("   ✓ Report directory: outputs/reports/demo_attack_report")

    # Example 2: Comparison report
    print("\n2. Generating comparison report...")
    provider_results = {
        'openai': {
            'success_rate': 0.45,
            'avg_response_time': 1.2,
            'error_rate': 0.05,
            'avg_position_change': 2.3,
            'attack_type_breakdown': {
                'prompt_injection': {'success_rate': 0.50}
            }
        },
        'anthropic': {
            'success_rate': 0.52,
            'avg_response_time': 0.8,
            'error_rate': 0.03,
            'avg_position_change': 2.8,
            'attack_type_breakdown': {
                'prompt_injection': {'success_rate': 0.55}
            }
        }
    }

    saved_paths = generator.generate_comparison_report(
        provider_results,
        report_name="demo_comparison_report",
        formats=['png']
    )
    print(f"   ✓ Generated {len(saved_paths)} figures")
    print("   ✓ Report directory: outputs/reports/demo_comparison_report")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " " * 10 + "UNIFIED VISUALIZATION PACKAGE DEMO" + " " * 13 + "║")
    print("╚" + "="*58 + "╝")

    # Create output directory
    Path("outputs").mkdir(exist_ok=True)

    try:
        # Run demos
        demo_attack_visualizations()
        demo_comparison_visualizations()
        demo_report_generation()

        print("\n" + "="*60)
        print("✓ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nGenerated files:")
        print("  - Individual charts: outputs/*.png")
        print("  - Reports: outputs/reports/")
        print("\nView reports by opening: outputs/reports/*/index.html")
        print()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
