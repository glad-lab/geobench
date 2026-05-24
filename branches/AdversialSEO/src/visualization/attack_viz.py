#!/usr/bin/env python3
"""
Attack-specific visualizations for adversarial SEO research.

Provides specialized visualizations for analyzing attack effectiveness,
positional bias, rank distributions, and attack type comparisons.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any, Optional
import logging

from .base import BaseVisualizer, VisualizationConfig
from .charts import ChartFactory
from .formatters import DataFormatter

logger = logging.getLogger(__name__)


class AttackVisualizer(BaseVisualizer):
    """
    Visualizations for attack effectiveness analysis.

    Provides methods for creating publication-quality visualizations of
    attack success rates, positional bias, rank distributions, and more.
    """

    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize attack visualizer.

        Args:
            config: Visualization configuration
        """
        super().__init__(config)

    def plot_success_rates(
        self,
        data: Dict[str, float],
        title: str = "Attack Success Rates by Type",
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot success rates for different attack types.

        Args:
            data: Dict mapping attack types to success rates
            title: Chart title
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        # Normalize rates to percentages
        rates = DataFormatter.normalize_rates(list(data.values()))
        normalized_data = dict(zip(data.keys(), rates))

        # Get colors from config
        colors = [
            self.config.attack_colors.get(attack_type, 'steelblue')
            for attack_type in data.keys()
        ]

        fig = ChartFactory.bar_chart(
            data=normalized_data,
            title=title,
            xlabel="Attack Type",
            ylabel="Success Rate (%)",
            colors=colors,
            alpha=0.7
        )

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot_positional_bias(
        self,
        data: Dict[int, float],
        title: str = "Attack Effectiveness by Position",
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot attack effectiveness at different positions.

        Args:
            data: Dict mapping positions to success rates
            title: Chart title
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        positions = sorted(data.keys())
        success_rates = DataFormatter.normalize_rates(
            [data[pos] for pos in positions]
        )

        fig = ChartFactory.line_chart(
            x_data=positions,
            y_data=success_rates,
            title=title,
            xlabel="Document Position",
            ylabel="Success Rate (%)",
            marker='o',
            linewidth=2,
            color=self.config.attack_colors.get('attack_success', '#E74C3C'),
            show_area=True
        )

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot_rank_distribution(
        self,
        ranks: List[int],
        title: str = "Target Product Rank Distribution",
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot distribution of target product ranks.

        Args:
            ranks: List of rank values
            title: Chart title
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        fig = ChartFactory.histogram(
            data=ranks,
            title=title,
            xlabel="Rank",
            ylabel="Frequency",
            bins=20,
            color=self.config.attack_colors.get('baseline', 'steelblue'),
            show_stats=True
        )

        # Add reference line for position 1
        ax = fig.axes[0]
        ax.axvline(
            x=1,
            color='red',
            linestyle='--',
            linewidth=2,
            label='Position 1'
        )
        ax.legend()

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot_attack_effectiveness_summary(
        self,
        results: List[Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create comprehensive attack effectiveness summary.

        Args:
            results: List of experimental results
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        # Filter out error results
        valid_results = [r for r in results if 'error' not in r]

        if not valid_results:
            logger.warning("No valid results to visualize")
            return plt.figure()

        # Extract metrics
        queries = [r.get('query', f'Query {i+1}')
                  for i, r in enumerate(valid_results)]

        retrieval_rates = [
            r.get('attack_docs_retrieved', 0) / r.get('total_docs', 1) * 100
            for r in valid_results
        ]

        effectiveness_rates = DataFormatter.normalize_rates([
            r.get('true_effectiveness', r.get('position_1_success_rate', 0))
            for r in valid_results
        ])

        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Plot 1: Retrieval rates
        x_pos = np.arange(len(queries))
        bars1 = ax1.bar(
            x_pos,
            retrieval_rates,
            color=self.config.attack_colors.get('baseline', '#3498DB'),
            alpha=0.7
        )

        ax1.set_xlabel('Test Queries')
        ax1.set_ylabel('Attack Document Retrieval Rate (%)')
        ax1.set_title('Attack Document Retrieval by Query Type')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels([f'Q{i+1}' for i in range(len(queries))], rotation=45)
        ax1.set_ylim(0, 100)

        # Add value labels
        for bar, rate in zip(bars1, retrieval_rates):
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width()/2.,
                height + 1,
                f'{rate:.1f}%',
                ha='center',
                va='bottom'
            )

        # Plot 2: Effectiveness rates
        colors2 = [
            self.config.attack_colors.get('attack_success', '#E74C3C')
            if rate > 0
            else self.config.attack_colors.get('attack_failure', '#95A5A6')
            for rate in effectiveness_rates
        ]

        bars2 = ax2.bar(x_pos, effectiveness_rates, color=colors2, alpha=0.8)

        ax2.set_xlabel('Test Queries')
        ax2.set_ylabel('Position 1 Success Rate (%)')
        ax2.set_title('Attack Effectiveness (Paper Methodology)\n(Position 1 Rankings Only)')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([f'Q{i+1}' for i in range(len(queries))], rotation=45)
        ax2.set_ylim(0, 100)

        # Add value labels
        for bar, rate in zip(bars2, effectiveness_rates):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width()/2.,
                height + 1,
                f'{rate:.1f}%',
                ha='center',
                va='bottom'
            )

        # Add average line
        avg_effectiveness = np.mean(effectiveness_rates)
        ax2.axhline(
            y=avg_effectiveness,
            color=self.config.attack_colors.get('neutral', '#34495E'),
            linestyle='--',
            alpha=0.7,
            label=f'Average: {avg_effectiveness:.1f}%'
        )
        ax2.legend()

        plt.tight_layout()

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot_attack_type_comparison(
        self,
        attack_data: Dict[str, List[float]],
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Compare effectiveness of different attack types.

        Args:
            attack_data: Dict mapping attack types to success rate lists
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        attack_types = list(attack_data.keys())
        success_rates = []
        error_bars = []

        for rates in attack_data.values():
            normalized_rates = DataFormatter.normalize_rates(rates, as_percentage=True)
            success_rates.append(np.mean(normalized_rates))
            error_bars.append(np.std(normalized_rates))

        # Get colors
        colors = [
            self.config.attack_colors.get(attack_type, 'steelblue')
            for attack_type in attack_types
        ]

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        x_pos = np.arange(len(attack_types))
        bars = ax.bar(
            x_pos,
            success_rates,
            yerr=error_bars,
            capsize=5,
            color=colors,
            alpha=0.8
        )

        ax.set_xlabel('Attack Type')
        ax.set_ylabel('Position 1 Success Rate (%)')
        ax.set_title('Attack Effectiveness by Type\n(Mean ± Standard Deviation)')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(attack_types)
        ax.set_ylim(0, 100)

        # Add value labels
        for bar, rate, error in zip(bars, success_rates, error_bars):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height + error + 2,
                f'{rate:.1f}%',
                ha='center',
                va='bottom',
                fontweight='bold'
            )

        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot_prisoners_dilemma(
        self,
        collective_performance: Dict[int, float],
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Replicate prisoner's dilemma dynamics visualization.

        Args:
            collective_performance: Dict mapping number of attackers to performance
            save_path: Optional path to save figure

        Returns:
            Matplotlib Figure object
        """
        num_attackers = sorted(collective_performance.keys())
        performance = [collective_performance[n] for n in num_attackers]

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(
            num_attackers,
            performance,
            'o-',
            linewidth=3,
            markersize=8,
            color=self.config.attack_colors.get('degraded', '#E67E22')
        )

        ax.fill_between(
            num_attackers,
            performance,
            alpha=0.3,
            color=self.config.attack_colors.get('degraded', '#E67E22')
        )

        ax.set_xlabel('Number of Attackers')
        ax.set_ylabel('Collective Performance')
        ax.set_title("Prisoner's Dilemma: Collective Performance Degradation\n(Replication of Paper Figure 5)")
        ax.set_xticks(num_attackers)
        ax.grid(True, alpha=0.3)

        # Calculate and annotate degradation
        if len(performance) > 1:
            max_performance = max(performance)
            min_performance = min(performance)
            degradation = ((max_performance - min_performance) / max_performance) * 100

            ax.annotate(
                f'Performance Degradation: {degradation:.1f}%',
                xy=(max(num_attackers), min_performance),
                xytext=(max(num_attackers)-1, min_performance + 0.1),
                arrowprops=dict(arrowstyle='->', color='gray'),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
            )

        plt.tight_layout()

        if save_path:
            self.save_figure(fig, save_path)

        return fig

    def plot(self, data: Any, **kwargs) -> plt.Figure:
        """
        Generic plot method (required by BaseVisualizer).

        Delegates to appropriate specialized method based on data structure.

        Args:
            data: Data to visualize
            **kwargs: Additional parameters

        Returns:
            Matplotlib Figure object
        """
        if isinstance(data, dict):
            if all(isinstance(k, int) for k in data.keys()):
                # Positional bias data
                return self.plot_positional_bias(data, **kwargs)
            else:
                # Success rates by type
                return self.plot_success_rates(data, **kwargs)
        elif isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                # Results list
                return self.plot_attack_effectiveness_summary(data, **kwargs)
            else:
                # Rank distribution
                return self.plot_rank_distribution(data, **kwargs)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
