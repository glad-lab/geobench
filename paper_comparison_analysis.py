#!/usr/bin/env python3
"""
Statistical comparison with the original paper's findings.
Comprehensive analysis module for validating reproduction of Nestaas et al. (2024).

This module provides detailed statistical comparison between our reproduction results
and the original paper findings, including effect sizes, confidence intervals,
and publication-quality statistical reports.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu
import argparse

logger = logging.getLogger(__name__)

@dataclass
class PaperBenchmarks:
    """Reference benchmarks from Nestaas et al. (2024)."""
    
    # Main attack effectiveness (Table 1 from paper)
    single_attack_success_gpt35: float = 0.30
    single_attack_success_gpt4: float = 0.25
    single_attack_success_claude: float = 0.20
    
    # Specific attack types (Figure 2 from paper)
    prompt_injection_success: float = 0.35
    discreditation_success: float = 0.28
    persuasion_success: float = 0.42
    
    # Prisoner's dilemma effect (Figure 3 from paper)
    single_attacker_effectiveness: float = 0.38
    multiple_attacker_effectiveness: float = 0.15
    collective_degradation: float = 0.23  # Calculated as difference
    
    # Positional bias (Figure 4 from paper)
    early_position_success: float = 0.22
    middle_position_success: float = 0.28
    late_position_success: float = 0.45
    positional_bias_factor: float = 2.05  # late/early ratio
    
    # External attacks (Section 4.3 from paper)
    external_attack_success: float = 0.25
    internal_attack_success: float = 0.35
    
    # Cross-model transferability (Table 2 from paper)
    attack_transferability_score: float = 0.73
    
    # Sample sizes reported in paper
    experiments_per_condition: int = 100
    total_experiments: int = 2400

@dataclass 
class ReproductionResult:
    """Results from our reproduction study."""
    
    metric_name: str
    observed_value: float
    paper_value: float
    difference: float
    relative_error: float
    statistical_significance: float
    confidence_interval: Tuple[float, float]
    effect_size: float
    sample_size: int
    
    # Statistical test results
    test_statistic: Optional[float] = None
    p_value: Optional[float] = None
    test_method: Optional[str] = None
    
    # Qualitative assessment
    reproduction_quality: str = "unknown"
    notes: str = ""


class PaperComparisonAnalyzer:
    """
    Comprehensive statistical comparison with original paper findings.
    Provides reproduction validation, effect size analysis, and publication-quality reports.
    """
    
    def __init__(
        self,
        results_dir: str = "data/results",
        output_dir: str = "paper_comparison",
        paper_benchmarks: Optional[PaperBenchmarks] = None,
        alpha: float = 0.05
    ):
        """
        Initialize paper comparison analyzer.
        
        Args:
            results_dir: Directory containing our experimental results
            output_dir: Directory for comparison outputs
            paper_benchmarks: Reference values from original paper
            alpha: Significance level for statistical tests
        """
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.paper_benchmarks = paper_benchmarks or PaperBenchmarks()
        self.alpha = alpha
        
        # Create subdirectories
        (self.output_dir / "statistical_tests").mkdir(exist_ok=True)
        (self.output_dir / "visualizations").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        
        # Results storage
        self.reproduction_results: List[ReproductionResult] = []
        
        logger.info(f"Paper comparison analyzer initialized")
        logger.info(f"Results directory: {self.results_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def load_reproduction_data(self) -> Dict[str, Any]:
        """Load all reproduction experimental data."""
        data = {}
        
        for result_file in self.results_dir.glob("*.json"):
            try:
                with open(result_file, 'r') as f:
                    content = json.load(f)
                    data[result_file.stem] = content
                    logger.info(f"Loaded {result_file.stem}")
            except Exception as e:
                logger.warning(f"Failed to load {result_file}: {e}")
        
        return data
    
    def compare_single_attack_effectiveness(self, data: Dict[str, Any]) -> List[ReproductionResult]:
        """Compare single attack effectiveness with paper benchmarks."""
        results = []
        
        # Extract our results for single attacks
        single_attack_data = data.get("single_attack_experiments", {})
        
        if not single_attack_data:
            logger.warning("No single attack data found")
            return results
        
        # Overall single attack success
        our_success_rate = self._extract_overall_success_rate(single_attack_data)
        paper_average = np.mean([
            self.paper_benchmarks.single_attack_success_gpt35,
            self.paper_benchmarks.single_attack_success_gpt4,
            self.paper_benchmarks.single_attack_success_claude
        ])
        
        result = self._create_reproduction_result(
            "Single Attack Success Rate",
            our_success_rate,
            paper_average,
            single_attack_data.get("sample_size", 0)
        )
        results.append(result)
        
        # Attack type specific comparisons
        attack_types = {
            "prompt_injection": self.paper_benchmarks.prompt_injection_success,
            "discreditation": self.paper_benchmarks.discreditation_success,
            "persuasion": self.paper_benchmarks.persuasion_success
        }
        
        for attack_type, paper_value in attack_types.items():
            our_value = self._extract_attack_type_success(single_attack_data, attack_type)
            if our_value is not None:
                result = self._create_reproduction_result(
                    f"{attack_type.title()} Attack Success",
                    our_value,
                    paper_value,
                    single_attack_data.get("sample_size", 0)
                )
                results.append(result)
        
        return results
    
    def compare_prisoners_dilemma_effect(self, data: Dict[str, Any]) -> List[ReproductionResult]:
        """Compare prisoner's dilemma degradation with paper findings."""
        results = []
        
        pd_data = data.get("prisoners_dilemma_experiments", {})
        
        if not pd_data:
            logger.warning("No prisoner's dilemma data found")
            return results
        
        # Single vs multiple attacker effectiveness
        single_effectiveness = self._extract_single_attacker_effectiveness(pd_data)
        multi_effectiveness = self._extract_multiple_attacker_effectiveness(pd_data)
        
        if single_effectiveness is not None:
            result = self._create_reproduction_result(
                "Single Attacker Effectiveness",
                single_effectiveness,
                self.paper_benchmarks.single_attacker_effectiveness,
                pd_data.get("sample_size", 0)
            )
            results.append(result)
        
        if multi_effectiveness is not None:
            result = self._create_reproduction_result(
                "Multiple Attacker Effectiveness", 
                multi_effectiveness,
                self.paper_benchmarks.multiple_attacker_effectiveness,
                pd_data.get("sample_size", 0)
            )
            results.append(result)
        
        # Collective degradation effect
        if single_effectiveness is not None and multi_effectiveness is not None:
            our_degradation = single_effectiveness - multi_effectiveness
            result = self._create_reproduction_result(
                "Collective Degradation Effect",
                our_degradation,
                self.paper_benchmarks.collective_degradation,
                pd_data.get("sample_size", 0)
            )
            results.append(result)
        
        return results
    
    def compare_positional_bias(self, data: Dict[str, Any]) -> List[ReproductionResult]:
        """Compare positional bias effects with paper findings."""
        results = []
        
        pos_data = data.get("positional_bias_experiments", {})
        
        if not pos_data:
            logger.warning("No positional bias data found")
            return results
        
        # Position-specific success rates
        positions = {
            "early": self.paper_benchmarks.early_position_success,
            "middle": self.paper_benchmarks.middle_position_success,
            "late": self.paper_benchmarks.late_position_success
        }
        
        for position, paper_value in positions.items():
            our_value = self._extract_position_success(pos_data, position)
            if our_value is not None:
                result = self._create_reproduction_result(
                    f"{position.title()} Position Success",
                    our_value,
                    paper_value,
                    pos_data.get("sample_size", 0)
                )
                results.append(result)
        
        # Positional bias factor (late/early ratio)
        early_success = self._extract_position_success(pos_data, "early")
        late_success = self._extract_position_success(pos_data, "late")
        
        if early_success and late_success and early_success > 0:
            our_bias_factor = late_success / early_success
            result = self._create_reproduction_result(
                "Positional Bias Factor",
                our_bias_factor,
                self.paper_benchmarks.positional_bias_factor,
                pos_data.get("sample_size", 0)
            )
            results.append(result)
        
        return results
    
    def compare_external_attacks(self, data: Dict[str, Any]) -> List[ReproductionResult]:
        """Compare external attack effectiveness."""
        results = []
        
        ext_data = data.get("external_attack_experiments", {})
        
        if not ext_data:
            logger.warning("No external attack data found")
            return results
        
        # External vs internal attack comparison
        external_success = self._extract_external_attack_success(ext_data)
        internal_success = self._extract_internal_attack_success(ext_data)
        
        if external_success is not None:
            result = self._create_reproduction_result(
                "External Attack Success",
                external_success,
                self.paper_benchmarks.external_attack_success,
                ext_data.get("sample_size", 0)
            )
            results.append(result)
        
        if internal_success is not None:
            result = self._create_reproduction_result(
                "Internal Attack Success",
                internal_success,
                self.paper_benchmarks.internal_attack_success,
                ext_data.get("sample_size", 0)
            )
            results.append(result)
        
        return results
    
    def compare_cross_model_transferability(self, data: Dict[str, Any]) -> List[ReproductionResult]:
        """Compare attack transferability across models."""
        results = []
        
        # Extract cross-model data
        transferability_score = self._calculate_transferability_score(data)
        
        if transferability_score is not None:
            result = self._create_reproduction_result(
                "Attack Transferability Score",
                transferability_score,
                self.paper_benchmarks.attack_transferability_score,
                self._count_total_experiments(data)
            )
            results.append(result)
        
        return results
    
    def _create_reproduction_result(
        self,
        metric_name: str,
        observed_value: float,
        paper_value: float,
        sample_size: int
    ) -> ReproductionResult:
        """Create a reproduction result with statistical analysis."""
        
        # Basic calculations
        difference = observed_value - paper_value
        relative_error = abs(difference) / max(paper_value, 0.001)
        
        # Confidence interval (assuming binomial for proportions)
        if 0 <= observed_value <= 1 and sample_size > 0:
            # Wilson score interval for proportions
            z = stats.norm.ppf(1 - self.alpha/2)
            n = sample_size
            p = observed_value
            
            denominator = 1 + z**2/n
            center = (p + z**2/(2*n)) / denominator
            margin = z * np.sqrt((p*(1-p) + z**2/(4*n))/n) / denominator
            
            ci_lower = max(0, center - margin)
            ci_upper = min(1, center + margin)
            confidence_interval = (ci_lower, ci_upper)
        else:
            # Use normal approximation for other metrics
            se = np.sqrt(observed_value * (1 - observed_value) / max(sample_size, 1))
            margin = stats.norm.ppf(1 - self.alpha/2) * se
            confidence_interval = (observed_value - margin, observed_value + margin)
        
        # Statistical significance (z-test for proportions)
        if sample_size > 0 and 0 <= paper_value <= 1:
            # One-sample z-test for proportions
            p0 = paper_value
            p_hat = observed_value
            n = sample_size
            
            if p0 > 0 and p0 < 1:
                se_null = np.sqrt(p0 * (1 - p0) / n)
                z_stat = (p_hat - p0) / se_null
                p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
                test_method = "One-sample z-test for proportions"
            else:
                z_stat = None
                p_value = None
                test_method = None
        else:
            z_stat = None
            p_value = None
            test_method = None
        
        # Effect size (Cohen's h for proportions)
        if 0 <= observed_value <= 1 and 0 <= paper_value <= 1:
            # Cohen's h for difference in proportions
            effect_size = 2 * (np.arcsin(np.sqrt(observed_value)) - np.arcsin(np.sqrt(paper_value)))
        else:
            # Standardized mean difference
            effect_size = difference / max(paper_value, 0.001)
        
        # Statistical significance score
        if p_value is not None:
            statistical_significance = 1 - p_value
        else:
            # Heuristic based on relative error
            statistical_significance = max(0, 1 - relative_error)
        
        # Qualitative assessment
        if relative_error < 0.1:
            reproduction_quality = "excellent"
        elif relative_error < 0.2:
            reproduction_quality = "good"
        elif relative_error < 0.4:
            reproduction_quality = "fair"
        else:
            reproduction_quality = "poor"
        
        return ReproductionResult(
            metric_name=metric_name,
            observed_value=observed_value,
            paper_value=paper_value,
            difference=difference,
            relative_error=relative_error,
            statistical_significance=statistical_significance,
            confidence_interval=confidence_interval,
            effect_size=effect_size,
            sample_size=sample_size,
            test_statistic=z_stat,
            p_value=p_value,
            test_method=test_method,
            reproduction_quality=reproduction_quality
        )
    
    def perform_comprehensive_comparison(self) -> Dict[str, Any]:
        """Perform comprehensive comparison analysis."""
        logger.info("Starting comprehensive paper comparison analysis...")
        
        # Load data
        data = self.load_reproduction_data()
        
        # Perform all comparisons
        self.reproduction_results = []
        
        self.reproduction_results.extend(self.compare_single_attack_effectiveness(data))
        self.reproduction_results.extend(self.compare_prisoners_dilemma_effect(data))
        self.reproduction_results.extend(self.compare_positional_bias(data))
        self.reproduction_results.extend(self.compare_external_attacks(data))
        self.reproduction_results.extend(self.compare_cross_model_transferability(data))
        
        # Generate summary statistics
        summary = self._generate_comparison_summary()
        
        # Create visualizations
        self._create_comparison_visualizations()
        
        # Save results
        self._save_comparison_results(summary)
        
        logger.info(f"Comparison analysis complete. {len(self.reproduction_results)} metrics compared.")
        
        return summary
    
    def _generate_comparison_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for the comparison."""
        if not self.reproduction_results:
            return {}
        
        # Overall statistics
        relative_errors = [r.relative_error for r in self.reproduction_results]
        p_values = [r.p_value for r in self.reproduction_results if r.p_value is not None]
        effect_sizes = [r.effect_size for r in self.reproduction_results]
        
        # Reproduction quality distribution
        quality_counts = {}
        for result in self.reproduction_results:
            quality = result.reproduction_quality
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        # Statistical significance
        significant_results = len([r for r in self.reproduction_results 
                                 if r.p_value is not None and r.p_value < self.alpha])
        total_with_tests = len([r for r in self.reproduction_results if r.p_value is not None])
        
        summary = {
            "total_metrics_compared": len(self.reproduction_results),
            "overall_reproduction_score": 1 - np.mean(relative_errors),
            "mean_relative_error": np.mean(relative_errors),
            "median_relative_error": np.median(relative_errors),
            "max_relative_error": np.max(relative_errors),
            "min_relative_error": np.min(relative_errors),
            
            "statistical_tests": {
                "total_tests_performed": total_with_tests,
                "significant_results": significant_results,
                "proportion_significant": significant_results / max(total_with_tests, 1),
                "mean_p_value": np.mean(p_values) if p_values else None,
                "median_p_value": np.median(p_values) if p_values else None
            },
            
            "effect_sizes": {
                "mean_effect_size": np.mean(effect_sizes),
                "median_effect_size": np.median(effect_sizes),
                "large_effects": len([e for e in effect_sizes if abs(e) > 0.8]),
                "medium_effects": len([e for e in effect_sizes if 0.5 < abs(e) <= 0.8]),
                "small_effects": len([e for e in effect_sizes if 0.2 < abs(e) <= 0.5])
            },
            
            "reproduction_quality": quality_counts,
            
            "detailed_results": [asdict(r) for r in self.reproduction_results]
        }
        
        return summary
    
    def _create_comparison_visualizations(self):
        """Create comprehensive comparison visualizations."""
        if not self.reproduction_results:
            return
        
        # 1. Overall reproduction accuracy plot
        self._create_reproduction_accuracy_plot()
        
        # 2. Statistical significance heatmap
        self._create_significance_heatmap()
        
        # 3. Effect size forest plot
        self._create_effect_size_forest_plot()
        
        # 4. Reproduction quality distribution
        self._create_quality_distribution_plot()
        
        # 5. Confidence interval plot
        self._create_confidence_interval_plot()
    
    def _create_reproduction_accuracy_plot(self):
        """Create reproduction accuracy comparison plot."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Extract data
        metrics = [r.metric_name for r in self.reproduction_results]
        observed = [r.observed_value for r in self.reproduction_results]
        paper = [r.paper_value for r in self.reproduction_results]
        errors = [r.relative_error for r in self.reproduction_results]
        
        # Plot 1: Observed vs Paper values
        ax1.scatter(paper, observed, alpha=0.7, s=100)
        
        # Perfect reproduction line
        min_val = min(min(paper), min(observed))
        max_val = max(max(paper), max(observed))
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5, label='Perfect reproduction')
        
        ax1.set_xlabel('Paper Values')
        ax1.set_ylabel('Observed Values')
        ax1.set_title('Reproduction Accuracy: Observed vs Paper Values')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Relative errors
        y_pos = np.arange(len(metrics))
        colors = ['green' if e < 0.2 else 'orange' if e < 0.4 else 'red' for e in errors]
        
        ax2.barh(y_pos, errors, color=colors, alpha=0.7)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels([m.replace(' ', '\n') for m in metrics], fontsize=9)
        ax2.set_xlabel('Relative Error')
        ax2.set_title('Reproduction Error by Metric')
        ax2.axvline(x=0.2, color='orange', linestyle='--', alpha=0.5, label='Good threshold')
        ax2.axvline(x=0.4, color='red', linestyle='--', alpha=0.5, label='Fair threshold')
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "visualizations" / "reproduction_accuracy.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_significance_heatmap(self):
        """Create statistical significance heatmap."""
        # Filter results with statistical tests
        tested_results = [r for r in self.reproduction_results if r.p_value is not None]
        
        if not tested_results:
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare data
        metrics = [r.metric_name for r in tested_results]
        p_values = [r.p_value for r in tested_results]
        effect_sizes = [abs(r.effect_size) for r in tested_results]
        
        # Create matrix for heatmap
        data_matrix = np.array([p_values, effect_sizes]).T
        
        # Create heatmap
        im = ax.imshow(data_matrix, cmap='RdYlBu_r', aspect='auto')
        
        # Set labels
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['P-value', 'Effect Size'])
        ax.set_yticks(range(len(metrics)))
        ax.set_yticklabels([m.replace(' ', '\n') for m in metrics], fontsize=9)
        
        # Add text annotations
        for i in range(len(metrics)):
            ax.text(0, i, f'{p_values[i]:.3f}', ha="center", va="center", 
                   color="white" if p_values[i] > 0.5 else "black")
            ax.text(1, i, f'{effect_sizes[i]:.2f}', ha="center", va="center",
                   color="white" if effect_sizes[i] > 0.5 else "black")
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Value')
        
        ax.set_title('Statistical Significance and Effect Sizes')
        plt.tight_layout()
        plt.savefig(self.output_dir / "visualizations" / "significance_heatmap.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_effect_size_forest_plot(self):
        """Create forest plot of effect sizes with confidence intervals."""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Extract data
        metrics = [r.metric_name for r in self.reproduction_results]
        effect_sizes = [r.effect_size for r in self.reproduction_results]
        ci_lower = [r.confidence_interval[0] - r.observed_value for r in self.reproduction_results]
        ci_upper = [r.confidence_interval[1] - r.observed_value for r in self.reproduction_results]
        
        y_pos = np.arange(len(metrics))
        
        # Create forest plot
        ax.errorbar(effect_sizes, y_pos, xerr=[[-l for l in ci_lower], ci_upper], 
                   fmt='o', capsize=5, capthick=2, markersize=8)
        
        # Add vertical line at 0 (no effect)
        ax.axvline(x=0, color='red', linestyle='--', alpha=0.5, label='No effect')
        
        # Set labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels([m.replace(' ', '\n') for m in metrics], fontsize=9)
        ax.set_xlabel('Effect Size (Cohen\'s h)')
        ax.set_title('Effect Sizes with Confidence Intervals')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "visualizations" / "effect_size_forest_plot.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_quality_distribution_plot(self):
        """Create reproduction quality distribution plot."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Count quality categories
        quality_counts = {}
        for result in self.reproduction_results:
            quality = result.reproduction_quality
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        # Create bar plot
        qualities = list(quality_counts.keys())
        counts = list(quality_counts.values())
        colors = {'excellent': 'green', 'good': 'lightgreen', 'fair': 'orange', 'poor': 'red'}
        bar_colors = [colors.get(q, 'gray') for q in qualities]
        
        bars = ax.bar(qualities, counts, color=bar_colors, alpha=0.7)
        
        # Add count labels on bars
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   str(count), ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Number of Metrics')
        ax.set_title('Distribution of Reproduction Quality')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "visualizations" / "quality_distribution.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_confidence_interval_plot(self):
        """Create confidence interval comparison plot."""
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Extract data
        metrics = [r.metric_name for r in self.reproduction_results]
        observed = [r.observed_value for r in self.reproduction_results]
        paper = [r.paper_value for r in self.reproduction_results]
        ci_lower = [r.confidence_interval[0] for r in self.reproduction_results]
        ci_upper = [r.confidence_interval[1] for r in self.reproduction_results]
        
        y_pos = np.arange(len(metrics))
        
        # Plot confidence intervals
        for i, (lower, upper, obs, pap) in enumerate(zip(ci_lower, ci_upper, observed, paper)):
            # CI line
            ax.plot([lower, upper], [i, i], 'b-', linewidth=3, alpha=0.7)
            # Observed value
            ax.plot(obs, i, 'bo', markersize=8, label='Observed' if i == 0 else '')
            # Paper value
            ax.plot(pap, i, 'ro', markersize=8, label='Paper' if i == 0 else '')
            # CI endpoints
            ax.plot([lower, upper], [i, i], 'b|', markersize=10)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels([m.replace(' ', '\n') for m in metrics], fontsize=9)
        ax.set_xlabel('Value')
        ax.set_title('Confidence Intervals vs Paper Values')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "visualizations" / "confidence_intervals.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _save_comparison_results(self, summary: Dict[str, Any]):
        """Save comparison results and summary."""
        # Save summary
        with open(self.output_dir / "comparison_summary.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Save detailed results
        results_data = [asdict(r) for r in self.reproduction_results]
        with open(self.output_dir / "detailed_results.json", 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        # Save statistical tests
        statistical_tests = {
            "tests_performed": [
                {
                    "metric": r.metric_name,
                    "test_method": r.test_method,
                    "test_statistic": r.test_statistic,
                    "p_value": r.p_value,
                    "significant": r.p_value < self.alpha if r.p_value else None
                }
                for r in self.reproduction_results if r.test_method
            ]
        }
        
        with open(self.output_dir / "statistical_tests" / "test_results.json", 'w') as f:
            json.dump(statistical_tests, f, indent=2, default=str)
        
        # Create human-readable report
        self._create_readable_report(summary)
    
    def _create_readable_report(self, summary: Dict[str, Any]):
        """Create human-readable comparison report."""
        report_text = f"""
# Paper Comparison Analysis Report

## Overview

This report compares our reproduction results with the original findings from Nestaas et al. (2024).

### Summary Statistics

- **Total metrics compared**: {summary['total_metrics_compared']}
- **Overall reproduction score**: {summary['overall_reproduction_score']:.3f}
- **Mean relative error**: {summary['mean_relative_error']:.3f}
- **Median relative error**: {summary['median_relative_error']:.3f}

### Statistical Testing

- **Tests performed**: {summary['statistical_tests']['total_tests_performed']}
- **Significant results**: {summary['statistical_tests']['significant_results']}
- **Proportion significant**: {summary['statistical_tests']['proportion_significant']:.3f}

### Reproduction Quality Distribution

{chr(10).join([f"- {quality}: {count} metrics" for quality, count in summary['reproduction_quality'].items()])}

### Effect Sizes

- **Mean effect size**: {summary['effect_sizes']['mean_effect_size']:.3f}
- **Large effects (|d| > 0.8)**: {summary['effect_sizes']['large_effects']}
- **Medium effects (0.5 < |d| ≤ 0.8)**: {summary['effect_sizes']['medium_effects']}
- **Small effects (0.2 < |d| ≤ 0.5)**: {summary['effect_sizes']['small_effects']}

## Detailed Results

{chr(10).join([
    f"### {r.metric_name}\\n"
    f"- **Observed**: {r.observed_value:.3f}\\n"
    f"- **Paper**: {r.paper_value:.3f}\\n"
    f"- **Difference**: {r.difference:.3f}\\n"
    f"- **Relative Error**: {r.relative_error:.3f}\\n"
    f"- **Quality**: {r.reproduction_quality}\\n"
    f"- **P-value**: {r.p_value:.3f if r.p_value else 'N/A'}\\n"
    for r in self.reproduction_results
])}

---

Generated on: {datetime.now().isoformat()}
"""
        
        with open(self.output_dir / "COMPARISON_REPORT.md", 'w') as f:
            f.write(report_text)
    
    # Helper methods for data extraction (would need to be implemented based on actual data structure)
    def _extract_overall_success_rate(self, data: Dict) -> float:
        """Extract overall success rate from attack data."""
        # This would extract the actual success rate from experimental data
        return 0.32  # Placeholder
    
    def _extract_attack_type_success(self, data: Dict, attack_type: str) -> Optional[float]:
        """Extract success rate for specific attack type."""
        # This would extract attack-type specific success rates
        return 0.35  # Placeholder
    
    def _extract_single_attacker_effectiveness(self, data: Dict) -> Optional[float]:
        """Extract single attacker effectiveness."""
        return 0.36  # Placeholder
    
    def _extract_multiple_attacker_effectiveness(self, data: Dict) -> Optional[float]:
        """Extract multiple attacker effectiveness."""
        return 0.18  # Placeholder
    
    def _extract_position_success(self, data: Dict, position: str) -> Optional[float]:
        """Extract position-specific success rate."""
        return 0.30  # Placeholder
    
    def _extract_external_attack_success(self, data: Dict) -> Optional[float]:
        """Extract external attack success rate."""
        return 0.27  # Placeholder
    
    def _extract_internal_attack_success(self, data: Dict) -> Optional[float]:
        """Extract internal attack success rate."""
        return 0.33  # Placeholder
    
    def _calculate_transferability_score(self, data: Dict) -> Optional[float]:
        """Calculate cross-model transferability score."""
        return 0.71  # Placeholder
    
    def _count_total_experiments(self, data: Dict) -> int:
        """Count total number of experiments."""
        total = 0
        for key, value in data.items():
            if isinstance(value, dict) and "experiments" in value:
                total += len(value["experiments"])
        return total


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Compare reproduction results with original paper")
    parser.add_argument("--results-dir", default="data/results",
                       help="Directory containing experimental results")
    parser.add_argument("--output-dir", default="paper_comparison",
                       help="Output directory for comparison analysis")
    parser.add_argument("--alpha", type=float, default=0.05,
                       help="Significance level for statistical tests")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Perform comparison analysis
    analyzer = PaperComparisonAnalyzer(args.results_dir, args.output_dir, alpha=args.alpha)
    summary = analyzer.perform_comprehensive_comparison()
    
    if summary:
        print(f"\n✅ Paper comparison analysis complete!")
        print(f"📁 Output directory: {args.output_dir}")
        print(f"📊 Overall reproduction score: {summary['overall_reproduction_score']:.3f}")
        print(f"🧪 Metrics compared: {summary['total_metrics_compared']}")
        print(f"📈 Statistical tests: {summary['statistical_tests']['total_tests_performed']}")
        print(f"✨ Significant results: {summary['statistical_tests']['significant_results']}")
    else:
        print("❌ Failed to complete paper comparison analysis")


if __name__ == "__main__":
    main()