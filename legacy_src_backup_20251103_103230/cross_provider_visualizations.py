#!/usr/bin/env python3
"""
Visualization tools for cross-provider comparison analysis.
Creates publication-quality charts and graphs for multi-provider adversarial SEO research.

This module provides specialized visualizations for comparing attack effectiveness,
transferability, and performance metrics across different LLM providers.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from scipy import stats
import argparse

# Set up matplotlib and seaborn styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10

logger = logging.getLogger(__name__)

@dataclass
class VisualizationConfig:
    """Configuration for cross-provider visualizations."""
    
    figsize: Tuple[int, int] = (12, 8)
    dpi: int = 300
    style: str = "whitegrid"
    color_palette: str = "husl"
    save_format: str = "png"
    
    # Provider-specific colors
    provider_colors: Dict[str, str] = None
    
    # Attack type colors
    attack_colors: Dict[str, str] = None
    
    def __post_init__(self):
        if self.provider_colors is None:
            self.provider_colors = {
                'openai': '#1f77b4',
                'anthropic': '#ff7f0e', 
                'bedrock': '#2ca02c',
                'gpt-3.5-turbo': '#1f77b4',
                'gpt-4': '#0d47a1',
                'claude-3-haiku': '#ff7f0e',
                'claude-3-sonnet': '#e65100',
                'meta.llama3-8b-instruct-v1:0': '#2ca02c',
                'meta.llama3-70b-instruct-v1:0': '#1b5e20'
            }
        
        if self.attack_colors is None:
            self.attack_colors = {
                'prompt_injection': '#e74c3c',
                'discreditation': '#e67e22',
                'persuasion': '#f39c12'
            }


class CrossProviderVisualizer:
    """
    Creates publication-quality visualizations for cross-provider adversarial SEO analysis.
    Specializes in multi-provider comparisons, transferability analysis, and performance metrics.
    """
    
    def __init__(
        self,
        output_dir: str = "visualizations/cross_provider",
        config: Optional[VisualizationConfig] = None
    ):
        """
        Initialize cross-provider visualizer.
        
        Args:
            output_dir: Directory for saving visualizations
            config: Visualization configuration
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = config or VisualizationConfig()
        
        # Set up plotting style
        sns.set_style(self.config.style)
        sns.set_palette(self.config.color_palette)
        plt.rcParams['figure.figsize'] = self.config.figsize
        plt.rcParams['figure.dpi'] = self.config.dpi
        
        logger.info(f"Cross-provider visualizer initialized")
        logger.info(f"Output directory: {self.output_dir}")
    
    def create_provider_performance_comparison(
        self,
        provider_results: Dict[str, Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> str:
        """Create comprehensive provider performance comparison chart."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Cross-Provider Performance Comparison', fontsize=16, fontweight='bold')
        
        providers = list(provider_results.keys())
        
        # 1. Success rates comparison
        success_rates = [provider_results[p]['success_rate'] for p in providers]
        colors = [self.config.provider_colors.get(p, '#333333') for p in providers]
        
        bars1 = axes[0, 0].bar(providers, success_rates, color=colors, alpha=0.7)
        axes[0, 0].set_title('Attack Success Rates by Provider')
        axes[0, 0].set_ylabel('Success Rate')
        axes[0, 0].set_ylim(0, 1.0)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, rate in zip(bars1, success_rates):
            axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                           f'{rate:.2%}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Response times comparison
        response_times = [provider_results[p]['avg_response_time'] for p in providers]
        
        bars2 = axes[0, 1].bar(providers, response_times, color=colors, alpha=0.7)
        axes[0, 1].set_title('Average Response Times')
        axes[0, 1].set_ylabel('Response Time (seconds)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        for bar, time in zip(bars2, response_times):
            axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                           f'{time:.2f}s', ha='center', va='bottom', fontweight='bold')
        
        # 3. Error rates comparison
        error_rates = [provider_results[p]['error_rate'] for p in providers]
        
        bars3 = axes[1, 0].bar(providers, error_rates, color=colors, alpha=0.7)
        axes[1, 0].set_title('Error Rates by Provider')
        axes[1, 0].set_ylabel('Error Rate')
        axes[1, 0].set_ylim(0, max(error_rates) * 1.2 if error_rates else 0.1)
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        for bar, rate in zip(bars3, error_rates):
            axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                           f'{rate:.2%}', ha='center', va='bottom', fontweight='bold')
        
        # 4. Position change effectiveness
        position_changes = [provider_results[p]['avg_position_change'] for p in providers]
        
        bars4 = axes[1, 1].bar(providers, position_changes, color=colors, alpha=0.7)
        axes[1, 1].set_title('Average Position Change')
        axes[1, 1].set_ylabel('Position Change')
        axes[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        for bar, change in zip(bars4, position_changes):
            axes[1, 1].text(bar.get_x() + bar.get_width()/2, 
                           bar.get_height() + (0.2 if change >= 0 else -0.4),
                           f'{change:.1f}', ha='center', va='bottom' if change >= 0 else 'top',
                           fontweight='bold')
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            save_path = self.output_dir / f"provider_performance_comparison.{self.config.save_format}"
        
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Provider performance comparison saved to {save_path}")
        return str(save_path)
    
    def create_transferability_heatmap(
        self,
        transferability_matrix: Dict[str, Dict[str, float]],
        save_path: Optional[str] = None
    ) -> str:
        """Create attack transferability heatmap across providers."""
        if not transferability_matrix:
            logger.warning("No transferability data provided")
            return ""
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(transferability_matrix).T
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create heatmap
        im = sns.heatmap(
            df,
            annot=True,
            fmt='.2%',
            cmap='Reds',
            cbar_kws={'label': 'Attack Success Rate'},
            square=True,
            linewidths=0.5,
            ax=ax
        )
        
        ax.set_title('Attack Transferability Across Providers', fontsize=14, fontweight='bold')
        ax.set_xlabel('Attack Type')
        ax.set_ylabel('Provider')
        
        # Rotate labels for better readability
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            save_path = self.output_dir / f"transferability_heatmap.{self.config.save_format}"
        
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Transferability heatmap saved to {save_path}")
        return str(save_path)
    
    def create_attack_type_effectiveness(
        self,
        provider_results: Dict[str, Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> str:
        """Create attack type effectiveness comparison across providers."""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Extract attack type data
        attack_types = []
        providers = []
        success_rates = []
        
        for provider, data in provider_results.items():
            if 'attack_type_breakdown' in data:
                for attack_type, metrics in data['attack_type_breakdown'].items():
                    attack_types.append(attack_type)
                    providers.append(provider)
                    success_rates.append(metrics['success_rate'])
        
        if not attack_types:
            logger.warning("No attack type breakdown data found")
            return ""
        
        # Create DataFrame
        df = pd.DataFrame({
            'Provider': providers,
            'Attack_Type': attack_types,
            'Success_Rate': success_rates
        })
        
        # Create grouped bar plot
        unique_attacks = df['Attack_Type'].unique()
        unique_providers = df['Provider'].unique()
        
        x = np.arange(len(unique_attacks))
        width = 0.8 / len(unique_providers)
        
        for i, provider in enumerate(unique_providers):
            provider_data = df[df['Provider'] == provider]
            rates = []
            for attack in unique_attacks:
                attack_data = provider_data[provider_data['Attack_Type'] == attack]
                rates.append(attack_data['Success_Rate'].iloc[0] if len(attack_data) > 0 else 0)
            
            color = self.config.provider_colors.get(provider, '#333333')
            bars = ax.bar(x + i * width, rates, width, label=provider, 
                         color=color, alpha=0.7)
            
            # Add value labels
            for bar, rate in zip(bars, rates):
                if rate > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                           f'{rate:.1%}', ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('Attack Type')
        ax.set_ylabel('Success Rate')
        ax.set_title('Attack Type Effectiveness by Provider')
        ax.set_xticks(x + width * (len(unique_providers) - 1) / 2)
        ax.set_xticklabels([attack.replace('_', ' ').title() for attack in unique_attacks])
        ax.legend()
        ax.set_ylim(0, 1.0)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            save_path = self.output_dir / f"attack_type_effectiveness.{self.config.save_format}"
        
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Attack type effectiveness chart saved to {save_path}")
        return str(save_path)
    
    def create_response_time_distribution(
        self,
        cross_provider_results: List[Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> str:
        """Create response time distribution comparison."""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Extract response time data by provider
        provider_times = {}
        for result in cross_provider_results:
            provider = result.get('provider', 'unknown')
            response_time = result.get('response_time', 0)
            
            if provider not in provider_times:
                provider_times[provider] = []
            provider_times[provider].append(response_time)
        
        if not provider_times:
            logger.warning("No response time data found")
            return ""
        
        # 1. Box plot of response times
        providers = list(provider_times.keys())
        times_data = [provider_times[p] for p in providers]
        colors = [self.config.provider_colors.get(p, '#333333') for p in providers]
        
        box_plot = axes[0].boxplot(times_data, labels=providers, patch_artist=True)
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        axes[0].set_title('Response Time Distribution by Provider')
        axes[0].set_ylabel('Response Time (seconds)')
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3)
        
        # 2. Histogram overlay
        for provider, times in provider_times.items():
            color = self.config.provider_colors.get(provider, '#333333')
            axes[1].hist(times, alpha=0.6, label=provider, color=color, bins=20)
        
        axes[1].set_title('Response Time Histogram Overlay')
        axes[1].set_xlabel('Response Time (seconds)')
        axes[1].set_ylabel('Frequency')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            save_path = self.output_dir / f"response_time_distribution.{self.config.save_format}"
        
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Response time distribution chart saved to {save_path}")
        return str(save_path)
    
    def create_vulnerability_radar_chart(
        self,
        provider_vulnerabilities: Dict[str, List[str]],
        save_path: Optional[str] = None
    ) -> str:
        """Create radar chart showing provider-specific vulnerabilities."""
        if not provider_vulnerabilities:
            logger.warning("No vulnerability data provided")
            return ""
        
        # Get all unique vulnerability types
        all_vulnerabilities = set()
        for vuln_list in provider_vulnerabilities.values():
            all_vulnerabilities.update(vuln_list)
        
        all_vulnerabilities = sorted(list(all_vulnerabilities))
        
        if not all_vulnerabilities:
            logger.warning("No vulnerabilities found in data")
            return ""
        
        # Set up radar chart
        angles = np.linspace(0, 2 * np.pi, len(all_vulnerabilities), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Plot data for each provider
        for provider, vulnerabilities in provider_vulnerabilities.items():
            # Create vulnerability scores (1 if vulnerable, 0 if not)
            scores = [1 if vuln in vulnerabilities else 0 for vuln in all_vulnerabilities]
            scores += scores[:1]  # Complete the circle
            
            color = self.config.provider_colors.get(provider, '#333333')
            ax.plot(angles, scores, 'o-', linewidth=2, label=provider, color=color)
            ax.fill(angles, scores, alpha=0.25, color=color)
        
        # Customize chart
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([vuln.replace('_', ' ').title() for vuln in all_vulnerabilities])
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Not Vulnerable', 'Vulnerable'])
        ax.grid(True)
        
        plt.title('Provider Vulnerability Profile', size=14, fontweight='bold', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        # Save plot
        if save_path is None:
            save_path = self.output_dir / f"vulnerability_radar_chart.{self.config.save_format}"
        
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Vulnerability radar chart saved to {save_path}")
        return str(save_path)
    
    def create_cost_benefit_analysis(
        self,
        cost_analysis: Dict[str, float],
        provider_results: Dict[str, Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> str:
        """Create cost-benefit analysis scatter plot."""
        if not cost_analysis or not provider_results:
            logger.warning("Insufficient data for cost-benefit analysis")
            return ""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract data
        providers = []
        costs = []
        success_rates = []
        
        for provider in cost_analysis.keys():
            if provider in provider_results:
                providers.append(provider)
                costs.append(cost_analysis[provider])
                success_rates.append(provider_results[provider]['success_rate'])
        
        if not providers:
            logger.warning("No matching cost and performance data")
            return ""
        
        # Create scatter plot
        colors = [self.config.provider_colors.get(p, '#333333') for p in providers]
        scatter = ax.scatter(costs, success_rates, s=200, c=colors, alpha=0.7)
        
        # Add labels for each point
        for i, provider in enumerate(providers):
            ax.annotate(provider, (costs[i], success_rates[i]), 
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=10, ha='left')
        
        ax.set_xlabel('Estimated Cost ($)')
        ax.set_ylabel('Attack Success Rate')
        ax.set_title('Cost vs. Attack Effectiveness by Provider')
        ax.grid(True, alpha=0.3)
        
        # Add efficiency frontier line (connect efficient providers)
        # Sort by cost and draw line
        sorted_data = sorted(zip(costs, success_rates, providers))
        sorted_costs = [item[0] for item in sorted_data]
        sorted_rates = [item[1] for item in sorted_data]
        
        ax.plot(sorted_costs, sorted_rates, '--', alpha=0.5, color='gray', 
               label='Cost-Effectiveness Trend')
        ax.legend()
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            save_path = self.output_dir / f"cost_benefit_analysis.{self.config.save_format}"
        
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Cost-benefit analysis chart saved to {save_path}")
        return str(save_path)
    
    def create_statistical_significance_plot(
        self,
        statistical_tests: Dict[str, Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> str:
        """Create statistical significance visualization."""
        if not statistical_tests.get('p_values'):
            logger.warning("No statistical test data provided")
            return ""
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Extract data
        comparisons = list(statistical_tests['p_values'].keys())
        p_values = list(statistical_tests['p_values'].values())
        effect_sizes = [statistical_tests.get('effect_sizes', {}).get(comp, 0) 
                       for comp in comparisons]
        
        # 1. P-value plot
        colors = ['green' if p < 0.05 else 'orange' if p < 0.1 else 'red' for p in p_values]
        bars = axes[0].bar(range(len(comparisons)), p_values, color=colors, alpha=0.7)
        
        axes[0].axhline(y=0.05, color='red', linestyle='--', alpha=0.7, label='α = 0.05')
        axes[0].axhline(y=0.01, color='darkred', linestyle='--', alpha=0.7, label='α = 0.01')
        
        axes[0].set_title('Statistical Significance of Provider Differences')
        axes[0].set_ylabel('P-value')
        axes[0].set_yscale('log')
        axes[0].set_xticks(range(len(comparisons)))
        axes[0].set_xticklabels([comp.replace('_', ' ').title() for comp in comparisons], 
                               rotation=45, ha='right')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Add p-value labels
        for bar, p_val in zip(bars, p_values):
            axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.1,
                        f'{p_val:.3f}', ha='center', va='bottom', fontsize=9)
        
        # 2. Effect size plot
        effect_bars = axes[1].bar(range(len(comparisons)), effect_sizes, 
                                 color='steelblue', alpha=0.7)
        
        axes[1].axhline(y=0.2, color='orange', linestyle='--', alpha=0.7, label='Small effect')
        axes[1].axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='Medium effect')
        axes[1].axhline(y=0.8, color='darkred', linestyle='--', alpha=0.7, label='Large effect')
        
        axes[1].set_title('Effect Sizes of Provider Differences')
        axes[1].set_ylabel('Effect Size (Cohen\'s d)')
        axes[1].set_xticks(range(len(comparisons)))
        axes[1].set_xticklabels([comp.replace('_', ' ').title() for comp in comparisons], 
                               rotation=45, ha='right')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Add effect size labels
        for bar, effect in zip(effect_bars, effect_sizes):
            axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                        f'{effect:.2f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            save_path = self.output_dir / f"statistical_significance.{self.config.save_format}"
        
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Statistical significance plot saved to {save_path}")
        return str(save_path)
    
    def create_comprehensive_dashboard(
        self,
        provider_results: Dict[str, Dict[str, Any]],
        transferability_matrix: Dict[str, Dict[str, float]],
        cost_analysis: Dict[str, float],
        cross_provider_results: List[Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> str:
        """Create comprehensive dashboard with all key metrics."""
        fig = plt.figure(figsize=(20, 16))
        
        # Create a complex subplot layout
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # 1. Provider performance overview (top-left, 2x2)
        ax1 = fig.add_subplot(gs[0:2, 0:2])
        providers = list(provider_results.keys())
        success_rates = [provider_results[p]['success_rate'] for p in providers]
        colors = [self.config.provider_colors.get(p, '#333333') for p in providers]
        
        bars = ax1.bar(providers, success_rates, color=colors, alpha=0.7)
        ax1.set_title('Provider Success Rates', fontweight='bold')
        ax1.set_ylabel('Success Rate')
        ax1.set_ylim(0, 1.0)
        for bar, rate in zip(bars, success_rates):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{rate:.1%}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Transferability heatmap (top-right, 2x2)
        ax2 = fig.add_subplot(gs[0:2, 2:4])
        if transferability_matrix:
            df = pd.DataFrame(transferability_matrix).T
            sns.heatmap(df, annot=True, fmt='.1%', cmap='Reds', ax=ax2, cbar=False)
            ax2.set_title('Attack Transferability', fontweight='bold')
        
        # 3. Response time comparison (bottom-left)
        ax3 = fig.add_subplot(gs[2, 0:2])
        response_times = [provider_results[p]['avg_response_time'] for p in providers]
        ax3.bar(providers, response_times, color=colors, alpha=0.7)
        ax3.set_title('Response Times', fontweight='bold')
        ax3.set_ylabel('Time (s)')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Cost analysis (bottom-right)
        ax4 = fig.add_subplot(gs[2, 2:4])
        if cost_analysis:
            cost_providers = list(cost_analysis.keys())
            costs = list(cost_analysis.values())
            cost_colors = [self.config.provider_colors.get(p, '#333333') for p in cost_providers]
            ax4.bar(cost_providers, costs, color=cost_colors, alpha=0.7)
            ax4.set_title('Estimated Costs', fontweight='bold')
            ax4.set_ylabel('Cost ($)')
            ax4.tick_params(axis='x', rotation=45)
        
        # 5. Error rates (bottom)
        ax5 = fig.add_subplot(gs[3, :])
        error_rates = [provider_results[p]['error_rate'] for p in providers]
        bars = ax5.bar(providers, error_rates, color=colors, alpha=0.7)
        ax5.set_title('Error Rates by Provider', fontweight='bold')
        ax5.set_ylabel('Error Rate')
        ax5.set_ylim(0, max(error_rates) * 1.2 if error_rates else 0.1)
        for bar, rate in zip(bars, error_rates):
            if rate > 0:
                ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                        f'{rate:.1%}', ha='center', va='bottom', fontweight='bold')
        
        plt.suptitle('Cross-Provider Adversarial SEO Analysis Dashboard', 
                    fontsize=20, fontweight='bold')
        
        # Save plot
        if save_path is None:
            save_path = self.output_dir / f"comprehensive_dashboard.{self.config.save_format}"
        
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Comprehensive dashboard saved to {save_path}")
        return str(save_path)
    
    def generate_all_visualizations(
        self,
        data_file: str,
        output_subdir: Optional[str] = None
    ) -> List[str]:
        """Generate all cross-provider visualizations from a data file."""
        if output_subdir:
            output_dir = self.output_dir / output_subdir
            output_dir.mkdir(exist_ok=True)
        else:
            output_dir = self.output_dir
        
        # Load data
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        generated_plots = []
        
        # Extract relevant data sections
        provider_results = data.get('provider_results', {})
        transferability_matrix = data.get('transferability_matrix', {})
        cost_analysis = data.get('cost_analysis', {})
        cross_provider_results = data.get('detailed_results', [])
        statistical_tests = {
            'p_values': data.get('statistical_significance', {}),
            'effect_sizes': data.get('effect_sizes', {}),
            'confidence_intervals': data.get('confidence_intervals', {})
        }
        provider_vulnerabilities = data.get('provider_specific_vulnerabilities', {})
        
        # Generate all visualizations
        try:
            plot_path = self.create_provider_performance_comparison(
                provider_results, output_dir / f"provider_performance.{self.config.save_format}"
            )
            generated_plots.append(plot_path)
        except Exception as e:
            logger.error(f"Failed to create provider performance comparison: {e}")
        
        try:
            plot_path = self.create_transferability_heatmap(
                transferability_matrix, output_dir / f"transferability_heatmap.{self.config.save_format}"
            )
            generated_plots.append(plot_path)
        except Exception as e:
            logger.error(f"Failed to create transferability heatmap: {e}")
        
        try:
            plot_path = self.create_attack_type_effectiveness(
                provider_results, output_dir / f"attack_effectiveness.{self.config.save_format}"
            )
            generated_plots.append(plot_path)
        except Exception as e:
            logger.error(f"Failed to create attack type effectiveness: {e}")
        
        try:
            plot_path = self.create_response_time_distribution(
                cross_provider_results, output_dir / f"response_times.{self.config.save_format}"
            )
            generated_plots.append(plot_path)
        except Exception as e:
            logger.error(f"Failed to create response time distribution: {e}")
        
        try:
            plot_path = self.create_vulnerability_radar_chart(
                provider_vulnerabilities, output_dir / f"vulnerability_radar.{self.config.save_format}"
            )
            generated_plots.append(plot_path)
        except Exception as e:
            logger.error(f"Failed to create vulnerability radar chart: {e}")
        
        try:
            plot_path = self.create_cost_benefit_analysis(
                cost_analysis, provider_results, output_dir / f"cost_benefit.{self.config.save_format}"
            )
            generated_plots.append(plot_path)
        except Exception as e:
            logger.error(f"Failed to create cost-benefit analysis: {e}")
        
        try:
            plot_path = self.create_statistical_significance_plot(
                statistical_tests, output_dir / f"statistical_significance.{self.config.save_format}"
            )
            generated_plots.append(plot_path)
        except Exception as e:
            logger.error(f"Failed to create statistical significance plot: {e}")
        
        try:
            plot_path = self.create_comprehensive_dashboard(
                provider_results, transferability_matrix, cost_analysis,
                cross_provider_results, output_dir / f"dashboard.{self.config.save_format}"
            )
            generated_plots.append(plot_path)
        except Exception as e:
            logger.error(f"Failed to create comprehensive dashboard: {e}")
        
        logger.info(f"Generated {len(generated_plots)} visualizations")
        return generated_plots


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Generate cross-provider visualizations")
    parser.add_argument("data_file", help="JSON file containing cross-provider results")
    parser.add_argument("--output-dir", default="visualizations/cross_provider",
                       help="Output directory for visualizations")
    parser.add_argument("--output-subdir", 
                       help="Subdirectory within output dir (optional)")
    parser.add_argument("--figsize", nargs=2, type=int, default=[12, 8],
                       help="Figure size (width height)")
    parser.add_argument("--dpi", type=int, default=300,
                       help="DPI for saved figures")
    parser.add_argument("--format", default="png",
                       help="Output format (png, pdf, svg)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Configure visualization
    config = VisualizationConfig(
        figsize=tuple(args.figsize),
        dpi=args.dpi,
        save_format=args.format
    )
    
    # Create visualizer
    visualizer = CrossProviderVisualizer(args.output_dir, config)
    
    # Check if data file exists
    if not Path(args.data_file).exists():
        print(f"❌ Data file not found: {args.data_file}")
        return
    
    # Generate all visualizations
    generated_plots = visualizer.generate_all_visualizations(
        args.data_file, args.output_subdir
    )
    
    if generated_plots:
        print(f"\n✅ Generated {len(generated_plots)} visualizations!")
        print(f"📁 Output directory: {args.output_dir}")
        for plot in generated_plots:
            print(f"📊 {Path(plot).name}")
    else:
        print("❌ Failed to generate visualizations")


if __name__ == "__main__":
    main()