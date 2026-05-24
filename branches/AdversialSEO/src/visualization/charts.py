#!/usr/bin/env python3
"""
Reusable chart components factory.

Provides factory methods for creating common chart types with consistent styling
and minimal duplication. All chart types return matplotlib Figure objects.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ChartFactory:
    """
    Factory for creating different chart types with consistent styling.

    All methods are static and return matplotlib Figure objects that can be
    further customized or saved.
    """

    @staticmethod
    def bar_chart(
        data: Dict[str, float],
        title: str,
        xlabel: str,
        ylabel: str,
        colors: Optional[Any] = None,
        figsize: Tuple[int, int] = (10, 6),
        show_values: bool = True,
        rotation: int = 45,
        **kwargs
    ) -> plt.Figure:
        """
        Create bar chart with value labels.

        Args:
            data: Dict mapping categories to values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            colors: Bar colors (single color or list)
            figsize: Figure size
            show_values: Whether to show value labels on bars
            rotation: X-tick label rotation angle
            **kwargs: Additional bar plot parameters

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        categories = list(data.keys())
        values = list(data.values())

        if colors is None:
            colors = 'steelblue'

        bars = ax.bar(categories, values, color=colors, **kwargs)

        ax.set_title(title, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        if rotation != 0:
            plt.xticks(rotation=rotation, ha='right')

        if show_values:
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height,
                    f'{height:.2f}',
                    ha='center',
                    va='bottom',
                    fontweight='bold'
                )

        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        return fig

    @staticmethod
    def grouped_bar_chart(
        data: Dict[str, Dict[str, float]],
        title: str,
        xlabel: str,
        ylabel: str,
        colors: Optional[Dict[str, str]] = None,
        figsize: Tuple[int, int] = (12, 6),
        show_values: bool = True,
        **kwargs
    ) -> plt.Figure:
        """
        Create grouped bar chart for comparing multiple series.

        Args:
            data: Nested dict {category: {series: value}}
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            colors: Color mapping for series
            figsize: Figure size
            show_values: Whether to show value labels
            **kwargs: Additional bar plot parameters

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        categories = list(data.keys())
        series_names = list(next(iter(data.values())).keys())
        n_series = len(series_names)

        x = np.arange(len(categories))
        width = 0.8 / n_series

        for i, series_name in enumerate(series_names):
            values = [data[cat].get(series_name, 0) for cat in categories]
            color = colors.get(series_name, None) if colors else None
            offset = (i - n_series/2 + 0.5) * width

            bars = ax.bar(
                x + offset,
                values,
                width,
                label=series_name,
                color=color,
                **kwargs
            )

            if show_values:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(
                            bar.get_x() + bar.get_width() / 2.,
                            height,
                            f'{height:.1f}',
                            ha='center',
                            va='bottom',
                            fontsize=9
                        )

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        return fig

    @staticmethod
    def line_chart(
        x_data: List[Any],
        y_data: List[float],
        title: str,
        xlabel: str,
        ylabel: str,
        figsize: Tuple[int, int] = (10, 6),
        show_points: bool = True,
        show_area: bool = False,
        **kwargs
    ) -> plt.Figure:
        """
        Create line chart with optional markers and area fill.

        Args:
            x_data: X-axis values
            y_data: Y-axis values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            figsize: Figure size
            show_points: Whether to show markers
            show_area: Whether to fill area under line
            **kwargs: Additional plot parameters

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        plot_kwargs = {'linewidth': 2}
        if show_points:
            plot_kwargs['marker'] = 'o'
            plot_kwargs['markersize'] = 8

        plot_kwargs.update(kwargs)

        ax.plot(x_data, y_data, **plot_kwargs)

        if show_area:
            ax.fill_between(x_data, y_data, alpha=0.3)

        ax.set_title(title, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    @staticmethod
    def multi_line_chart(
        data: Dict[str, Tuple[List, List]],
        title: str,
        xlabel: str,
        ylabel: str,
        figsize: Tuple[int, int] = (12, 6),
        colors: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> plt.Figure:
        """
        Create chart with multiple lines.

        Args:
            data: Dict mapping series names to (x_data, y_data) tuples
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            figsize: Figure size
            colors: Color mapping for series
            **kwargs: Additional plot parameters

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        for series_name, (x_data, y_data) in data.items():
            color = colors.get(series_name, None) if colors else None
            ax.plot(
                x_data,
                y_data,
                marker='o',
                linewidth=2,
                label=series_name,
                color=color,
                **kwargs
            )

        ax.set_title(title, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    @staticmethod
    def heatmap(
        data: np.ndarray,
        title: str,
        row_labels: List[str],
        col_labels: List[str],
        figsize: Tuple[int, int] = (12, 8),
        cmap: str = 'Reds',
        annot: bool = True,
        fmt: str = '.2f',
        **kwargs
    ) -> plt.Figure:
        """
        Create heatmap visualization.

        Args:
            data: 2D array of values
            title: Chart title
            row_labels: Labels for rows
            col_labels: Labels for columns
            figsize: Figure size
            cmap: Colormap name
            annot: Whether to annotate cells
            fmt: Format string for annotations
            **kwargs: Additional heatmap parameters

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        heatmap_kwargs = {
            'annot': annot,
            'fmt': fmt,
            'cmap': cmap,
            'xticklabels': col_labels,
            'yticklabels': row_labels,
            'square': True,
            'linewidths': 0.5,
            'cbar_kws': {'label': 'Value'},
            'ax': ax
        }
        heatmap_kwargs.update(kwargs)

        sns.heatmap(data, **heatmap_kwargs)

        ax.set_title(title, fontweight='bold', pad=20)

        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()

        return fig

    @staticmethod
    def scatter_plot(
        x_data: List[float],
        y_data: List[float],
        title: str,
        xlabel: str,
        ylabel: str,
        labels: Optional[List[str]] = None,
        colors: Optional[List[str]] = None,
        sizes: Optional[List[float]] = None,
        figsize: Tuple[int, int] = (10, 6),
        show_trend: bool = False,
        **kwargs
    ) -> plt.Figure:
        """
        Create scatter plot with optional labels and trend line.

        Args:
            x_data: X-axis values
            y_data: Y-axis values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            labels: Point labels (optional)
            colors: Point colors (optional)
            sizes: Point sizes (optional)
            figsize: Figure size
            show_trend: Whether to show trend line
            **kwargs: Additional scatter parameters

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        scatter_kwargs = {'s': sizes if sizes else 100, 'alpha': 0.7}
        if colors:
            scatter_kwargs['c'] = colors

        scatter_kwargs.update(kwargs)

        ax.scatter(x_data, y_data, **scatter_kwargs)

        if labels:
            for i, label in enumerate(labels):
                ax.annotate(
                    label,
                    (x_data[i], y_data[i]),
                    xytext=(10, 10),
                    textcoords='offset points',
                    fontsize=10,
                    ha='left'
                )

        if show_trend and len(x_data) > 1:
            z = np.polyfit(x_data, y_data, 1)
            p = np.poly1d(z)
            ax.plot(
                x_data,
                p(x_data),
                "--",
                alpha=0.5,
                color='gray',
                label='Trend'
            )
            ax.legend()

        ax.set_title(title, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    @staticmethod
    def box_plot(
        data: Dict[str, List[float]],
        title: str,
        xlabel: str,
        ylabel: str,
        colors: Optional[List[str]] = None,
        figsize: Tuple[int, int] = (10, 6),
        **kwargs
    ) -> plt.Figure:
        """
        Create box plot for distribution comparison.

        Args:
            data: Dict mapping categories to value lists
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            colors: Box colors
            figsize: Figure size
            **kwargs: Additional boxplot parameters

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        categories = list(data.keys())
        values = [data[cat] for cat in categories]

        box_plot = ax.boxplot(values, labels=categories, patch_artist=True, **kwargs)

        if colors:
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

        ax.set_title(title, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3, axis='y')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        return fig

    @staticmethod
    def histogram(
        data: List[float],
        title: str,
        xlabel: str,
        ylabel: str = "Frequency",
        bins: int = 20,
        figsize: Tuple[int, int] = (10, 6),
        color: str = 'steelblue',
        show_stats: bool = True,
        **kwargs
    ) -> plt.Figure:
        """
        Create histogram with optional statistics.

        Args:
            data: Values to plot
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            bins: Number of bins
            figsize: Figure size
            color: Bar color
            show_stats: Whether to show mean/median lines
            **kwargs: Additional hist parameters

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        hist_kwargs = {
            'bins': bins,
            'color': color,
            'alpha': 0.7,
            'edgecolor': 'black'
        }
        hist_kwargs.update(kwargs)

        ax.hist(data, **hist_kwargs)

        if show_stats and len(data) > 0:
            mean_val = np.mean(data)
            median_val = np.median(data)

            ax.axvline(
                mean_val,
                color='red',
                linestyle='--',
                linewidth=2,
                label=f'Mean: {mean_val:.2f}'
            )
            ax.axvline(
                median_val,
                color='green',
                linestyle='-',
                linewidth=2,
                label=f'Median: {median_val:.2f}'
            )
            ax.legend()

        ax.set_title(title, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        return fig
