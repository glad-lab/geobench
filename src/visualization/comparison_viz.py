#!/usr/bin/env python3
"""
Cross-provider and cross-attack comparison visualizations.

Provides specialized visualizations for comparing attack effectiveness across
different LLM providers, attack types, and experimental conditions.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
import logging
from scipy import stats

from .base import BaseVisualizer, VisualizationConfig
from .charts import ChartFactory
from .formatters import DataFormatter

logger = logging.getLogger(__name__)


class ComparisonVisualizer(BaseVisualizer):
    """
    Visualizations for cross-provider and cross-attack comparisons.

    Provides methods for comparing metrics across LLM providers, attack types,
    and experimental conditions with statistical analysis.
    """

    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize comparison visualizer.

        Args:
            config: Visualization configuration
        """
        super().__init__(config)

    def plot_provider_comparison(
        self,
        provider_results: Dict[str, Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create comprehensive provider performance comparison.

        Args:
            provider_results: Dict mapping providers to their results
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(
            'Cross-Provider Performance Comparison',
            fontsize=16,
            fontweight='bold'
        )

        providers = list(provider_results.keys())
        colors = [
            self.config.provider_colors.get(p, '#333333')
            for p in providers
        ]

        # 1. Success rates comparison
        success_rates = [
            provider_results[p].get('success_rate', 0)
            for p in providers
        ]

        bars1 = axes[0, 0].bar(providers, success_rates, color=colors, alpha=0.7)
        axes[0, 0].set_title('Attack Success Rates by Provider')
        axes[0, 0].set_ylabel('Success Rate')
        axes[0, 0].set_ylim(0, 1.0)
        axes[0, 0].tick_params(axis='x', rotation=45)

        for bar, rate in zip(bars1, success_rates):
            axes[0, 0].text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.01,
                f'{rate:.2%}',
                ha='center',
                va='bottom',
                fontweight='bold'
            )

        # 2. Response times comparison
        response_times = [
            provider_results[p].get('avg_response_time', 0)
            for p in providers
        ]

        bars2 = axes[0, 1].bar(providers, response_times, color=colors, alpha=0.7)
        axes[0, 1].set_title('Average Response Times')
        axes[0, 1].set_ylabel('Response Time (seconds)')
        axes[0, 1].tick_params(axis='x', rotation=45)

        for bar, time in zip(bars2, response_times):
            axes[0, 1].text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.01,
                f'{time:.2f}s',
                ha='center',
                va='bottom',
                fontweight='bold'
            )

        # 3. Error rates comparison
        error_rates = [
            provider_results[p].get('error_rate', 0)
            for p in providers
        ]

        bars3 = axes[1, 0].bar(providers, error_rates, color=colors, alpha=0.7)
        axes[1, 0].set_title('Error Rates by Provider')
        axes[1, 0].set_ylabel('Error Rate')
        axes[1, 0].set_ylim(0, max(error_rates) * 1.2 if error_rates else 0.1)
        axes[1, 0].tick_params(axis='x', rotation=45)

        for bar, rate in zip(bars3, error_rates):
            if rate > 0:
                axes[1, 0].text(
                    bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.002,
                    f'{rate:.2%}',
                    ha='center',
                    va='bottom',
                    fontweight='bold'
                )

        # 4. Position change effectiveness
        position_changes = [
            provider_results[p].get('avg_position_change', 0)
            for p in providers
        ]

        bars4 = axes[1, 1].bar(providers, position_changes, color=colors, alpha=0.7)
        axes[1, 1].set_title('Average Position Change')
        axes[1, 1].set_ylabel('Position Change')
        axes[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[1, 1].tick_params(axis='x', rotation=45)

        for bar, change in zip(bars4, position_changes):
            axes[1, 1].text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + (0.2 if change >= 0 else -0.4),
                f'{change:.1f}',
                ha='center',
                va='bottom' if change >= 0 else 'top',
                fontweight='bold'
            )

        plt.tight_layout()

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot_transferability_heatmap(
        self,
        transferability_matrix: Dict[str, Dict[str, float]],
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create attack transferability heatmap across providers.

        Args:
            transferability_matrix: Nested dict {provider: {attack_type: rate}}
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        if not transferability_matrix:
            logger.warning("No transferability data provided")
            return plt.figure()

        # Convert to DataFrame
        df = pd.DataFrame(transferability_matrix).T

        # Prepare data for heatmap
        data_array, row_labels, col_labels = DataFormatter.prepare_heatmap_data(
            transferability_matrix
        )

        fig = ChartFactory.heatmap(
            data=data_array,
            title='Attack Transferability Across Providers',
            row_labels=row_labels,
            col_labels=col_labels,
            cmap='Reds',
            annot=True,
            fmt='.2%',
            figsize=(12, 8),
            cbar_kws={'label': 'Attack Success Rate'}
        )

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot_attack_type_effectiveness(
        self,
        provider_results: Dict[str, Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create attack type effectiveness comparison across providers.

        Args:
            provider_results: Dict mapping providers to results with attack breakdowns
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        # Extract attack type data
        attack_data = {}

        for provider, data in provider_results.items():
            if 'attack_type_breakdown' in data:
                for attack_type, metrics in data['attack_type_breakdown'].items():
                    if attack_type not in attack_data:
                        attack_data[attack_type] = {}
                    attack_data[attack_type][provider] = metrics.get('success_rate', 0)

        if not attack_data:
            logger.warning("No attack type breakdown data found")
            return plt.figure()

        # Create grouped bar chart
        fig = ChartFactory.grouped_bar_chart(
            data=attack_data,
            title='Attack Type Effectiveness by Provider',
            xlabel='Attack Type',
            ylabel='Success Rate',
            colors=self.config.provider_colors,
            figsize=(14, 8),
            alpha=0.7
        )

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot_response_time_distribution(
        self,
        cross_provider_results: List[Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create response time distribution comparison.

        Args:
            cross_provider_results: List of results across providers
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        # Extract response times by provider
        provider_times = DataFormatter.extract_provider_metrics(
            cross_provider_results,
            'response_time'
        )

        if not provider_times:
            logger.warning("No response time data found")
            return plt.figure()

        # Expand to full data
        provider_time_lists = {}
        for result in cross_provider_results:
            provider = result.get('provider', 'unknown')
            response_time = result.get('response_time', 0)

            if provider not in provider_time_lists:
                provider_time_lists[provider] = []
            provider_time_lists[provider].append(response_time)

        # Create figure with two subplots
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # 1. Box plot
        providers = list(provider_time_lists.keys())
        times_data = [provider_time_lists[p] for p in providers]
        colors = [
            self.config.provider_colors.get(p, '#333333')
            for p in providers
        ]

        fig_box = ChartFactory.box_plot(
            data=provider_time_lists,
            title='Response Time Distribution by Provider',
            xlabel='Provider',
            ylabel='Response Time (seconds)',
            colors=colors
        )

        # 2. Histogram overlay
        for provider, times in provider_time_lists.items():
            color = self.config.provider_colors.get(provider, '#333333')
            axes[1].hist(
                times,
                alpha=0.6,
                label=provider,
                color=color,
                bins=20
            )

        axes[1].set_title('Response Time Histogram Overlay')
        axes[1].set_xlabel('Response Time (seconds)')
        axes[1].set_ylabel('Frequency')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        # Copy box plot to axes[0]
        plt.close(fig_box)
        box_plot = axes[0].boxplot(
            times_data,
            labels=providers,
            patch_artist=True
        )

        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        axes[0].set_title('Response Time Distribution by Provider')
        axes[0].set_ylabel('Response Time (seconds)')
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot_cost_benefit_analysis(
        self,
        cost_analysis: Dict[str, float],
        provider_results: Dict[str, Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create cost-benefit analysis scatter plot.

        Args:
            cost_analysis: Dict mapping providers to costs
            provider_results: Dict mapping providers to performance results
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        if not cost_analysis or not provider_results:
            logger.warning("Insufficient data for cost-benefit analysis")
            return plt.figure()

        # Extract matching data
        providers = []
        costs = []
        success_rates = []

        for provider in cost_analysis.keys():
            if provider in provider_results:
                providers.append(provider)
                costs.append(cost_analysis[provider])
                success_rates.append(provider_results[provider].get('success_rate', 0))

        if not providers:
            logger.warning("No matching cost and performance data")
            return plt.figure()

        colors = [
            self.config.provider_colors.get(p, '#333333')
            for p in providers
        ]

        fig = ChartFactory.scatter_plot(
            x_data=costs,
            y_data=success_rates,
            title='Cost vs. Attack Effectiveness by Provider',
            xlabel='Estimated Cost ($)',
            ylabel='Attack Success Rate',
            labels=providers,
            colors=colors,
            sizes=[200] * len(providers),
            show_trend=True
        )

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot_statistical_significance(
        self,
        statistical_tests: Dict[str, Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create statistical significance visualization.

        Args:
            statistical_tests: Dict with p_values, effect_sizes, etc.
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        if not statistical_tests.get('p_values'):
            logger.warning("No statistical test data provided")
            return plt.figure()

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Extract data
        comparisons = list(statistical_tests['p_values'].keys())
        p_values = list(statistical_tests['p_values'].values())
        effect_sizes = [
            statistical_tests.get('effect_sizes', {}).get(comp, 0)
            for comp in comparisons
        ]

        # 1. P-value plot
        colors = [
            'green' if p < 0.05 else 'orange' if p < 0.1 else 'red'
            for p in p_values
        ]

        bars = axes[0].bar(range(len(comparisons)), p_values, color=colors, alpha=0.7)

        axes[0].axhline(y=0.05, color='red', linestyle='--', alpha=0.7, label='α = 0.05')
        axes[0].axhline(y=0.01, color='darkred', linestyle='--', alpha=0.7, label='α = 0.01')

        axes[0].set_title('Statistical Significance of Provider Differences')
        axes[0].set_ylabel('P-value')
        axes[0].set_yscale('log')
        axes[0].set_xticks(range(len(comparisons)))
        axes[0].set_xticklabels(
            [comp.replace('_', ' ').title() for comp in comparisons],
            rotation=45,
            ha='right'
        )
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # Add p-value labels
        for bar, p_val in zip(bars, p_values):
            axes[0].text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() * 1.1,
                f'{p_val:.3f}',
                ha='center',
                va='bottom',
                fontsize=9
            )

        # 2. Effect size plot
        effect_bars = axes[1].bar(
            range(len(comparisons)),
            effect_sizes,
            color='steelblue',
            alpha=0.7
        )

        axes[1].axhline(y=0.2, color='orange', linestyle='--', alpha=0.7, label='Small effect')
        axes[1].axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='Medium effect')
        axes[1].axhline(y=0.8, color='darkred', linestyle='--', alpha=0.7, label='Large effect')

        axes[1].set_title("Effect Sizes of Provider Differences")
        axes[1].set_ylabel("Effect Size (Cohen's d)")
        axes[1].set_xticks(range(len(comparisons)))
        axes[1].set_xticklabels(
            [comp.replace('_', ' ').title() for comp in comparisons],
            rotation=45,
            ha='right'
        )
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        # Add effect size labels
        for bar, effect in zip(effect_bars, effect_sizes):
            axes[1].text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.02,
                f'{effect:.2f}',
                ha='center',
                va='bottom',
                fontsize=9
            )

        plt.tight_layout()

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot(self, data: Any, **kwargs) -> plt.Figure:
        """
        Generic plot method (required by BaseVisualizer).

        Args:
            data: Data to visualize
            **kwargs: Additional parameters

        Returns:
            Matplotlib Figure object
        """
        if isinstance(data, dict):
            if 'provider_results' in data:
                return self.plot_provider_comparison(
                    data['provider_results'],
                    **kwargs
                )
            elif all(isinstance(v, dict) for v in data.values()):
                # Likely transferability matrix
                return self.plot_transferability_heatmap(data, **kwargs)
            else:
                raise ValueError("Unsupported dict structure")
        elif isinstance(data, list):
            # Cross-provider results list
            return self.plot_response_time_distribution(data, **kwargs)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
