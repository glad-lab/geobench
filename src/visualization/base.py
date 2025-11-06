#!/usr/bin/env python3
"""
Base classes and configuration for visualization system.

Provides abstract base classes, configuration management, and common utilities
for all visualization components.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class VisualizationConfig:
    """
    Configuration for visualizations with sensible defaults.

    Attributes:
        figsize: Default figure size (width, height)
        dpi: Resolution for saved figures
        style: Matplotlib style to use
        color_palette: Seaborn color palette name
        font_size: Base font size
        title_size: Title font size
        provider_colors: Color mapping for LLM providers
        attack_colors: Color mapping for attack types
        save_format: Default format for saving figures
    """

    figsize: Tuple[int, int] = (12, 8)
    dpi: int = 300
    style: str = "seaborn-v0_8-whitegrid"
    color_palette: str = "husl"
    font_size: int = 11
    title_size: int = 14
    save_format: str = "png"

    # Provider-specific colors for consistency
    provider_colors: Dict[str, str] = field(default_factory=lambda: {
        'openai': '#1f77b4',
        'anthropic': '#ff7f0e',
        'bedrock': '#2ca02c',
        'gpt-3.5-turbo': '#1f77b4',
        'gpt-4': '#0d47a1',
        'claude-3-haiku': '#ff7f0e',
        'claude-3-sonnet': '#e65100',
        'meta.llama3-8b-instruct-v1:0': '#2ca02c',
        'meta.llama3-70b-instruct-v1:0': '#1b5e20'
    })

    # Attack type colors for consistency
    attack_colors: Dict[str, str] = field(default_factory=lambda: {
        'prompt_injection': '#e74c3c',
        'discreditation': '#e67e22',
        'persuasion': '#f39c12',
        'attack_success': '#E74C3C',
        'attack_failure': '#95A5A6',
        'baseline': '#3498DB',
        'improved': '#27AE60',
        'degraded': '#E67E22',
        'neutral': '#34495E'
    })

    def __post_init__(self):
        """Apply configuration to matplotlib."""
        self._apply_style()

    def _apply_style(self):
        """Apply style settings to matplotlib/seaborn."""
        try:
            plt.style.use(self.style)
        except OSError:
            logger.warning(f"Style '{self.style}' not found, using default")
            plt.style.use('default')

        sns.set_palette(self.color_palette)

        plt.rcParams.update({
            'font.size': self.font_size,
            'axes.titlesize': self.title_size,
            'axes.labelsize': self.font_size + 1,
            'xtick.labelsize': self.font_size - 1,
            'ytick.labelsize': self.font_size - 1,
            'legend.fontsize': self.font_size,
            'figure.figsize': self.figsize,
            'figure.dpi': self.dpi
        })


class BaseVisualizer(ABC):
    """
    Abstract base class for all visualizers.

    Provides common functionality for configuration management, style setup,
    and figure saving. All visualizers should inherit from this class.
    """

    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize visualizer with configuration.

        Args:
            config: Visualization configuration. If None, uses defaults.
        """
        self.config = config or VisualizationConfig()
        self._setup_style()
        logger.info(f"Initialized {self.__class__.__name__}")

    def _setup_style(self):
        """Apply matplotlib style settings from config."""
        self.config._apply_style()

    @abstractmethod
    def plot(self, data: Any, **kwargs) -> plt.Figure:
        """
        Create plot from data.

        Args:
            data: Data to visualize
            **kwargs: Additional plot-specific parameters

        Returns:
            Matplotlib Figure object
        """
        pass

    def save_figure(
        self,
        fig: plt.Figure,
        filepath: str,
        format: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Save figure to file.

        Args:
            fig: Matplotlib Figure to save
            filepath: Path to save file
            format: Output format (png, pdf, svg). If None, uses config default
            **kwargs: Additional arguments passed to savefig

        Returns:
            Path to saved file
        """
        format = format or self.config.save_format

        # Ensure file has correct extension
        filepath = Path(filepath)
        if not filepath.suffix:
            filepath = filepath.with_suffix(f'.{format}')
        elif filepath.suffix[1:] != format:
            filepath = filepath.with_suffix(f'.{format}')

        # Create directory if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Save with high quality settings
        save_kwargs = {
            'dpi': self.config.dpi,
            'bbox_inches': 'tight',
            'format': format
        }
        save_kwargs.update(kwargs)

        fig.savefig(filepath, **save_kwargs)
        logger.info(f"Saved figure to {filepath}")

        return str(filepath)

    def close_figure(self, fig: plt.Figure):
        """
        Close figure to free memory.

        Args:
            fig: Figure to close
        """
        plt.close(fig)


class ChartBuilder:
    """
    Builder for creating charts with fluent API.

    Provides a convenient fluent interface for constructing charts
    with common settings and customizations.

    Example:
        >>> builder = ChartBuilder()
        >>> fig = (builder
        ...     .with_size(10, 6)
        ...     .with_title("My Chart")
        ...     .with_labels("X Axis", "Y Axis")
        ...     .with_grid(True)
        ...     .build())
    """

    def __init__(self):
        """Initialize empty chart builder."""
        self.fig = None
        self.ax = None
        self._title = None
        self._xlabel = None
        self._ylabel = None
        self._grid = False
        self._legend = False
        self._figsize = (10, 6)

    def with_size(self, width: int, height: int) -> 'ChartBuilder':
        """
        Set figure size.

        Args:
            width: Figure width in inches
            height: Figure height in inches

        Returns:
            Self for chaining
        """
        self._figsize = (width, height)
        return self

    def with_title(self, title: str) -> 'ChartBuilder':
        """
        Set chart title.

        Args:
            title: Title text

        Returns:
            Self for chaining
        """
        self._title = title
        return self

    def with_labels(self, xlabel: str, ylabel: str) -> 'ChartBuilder':
        """
        Set axis labels.

        Args:
            xlabel: X-axis label
            ylabel: Y-axis label

        Returns:
            Self for chaining
        """
        self._xlabel = xlabel
        self._ylabel = ylabel
        return self

    def with_grid(self, enabled: bool = True, **kwargs) -> 'ChartBuilder':
        """
        Enable/disable grid.

        Args:
            enabled: Whether to show grid
            **kwargs: Additional grid parameters

        Returns:
            Self for chaining
        """
        self._grid = enabled
        self._grid_kwargs = kwargs
        return self

    def with_legend(self, enabled: bool = True, **kwargs) -> 'ChartBuilder':
        """
        Enable/disable legend.

        Args:
            enabled: Whether to show legend
            **kwargs: Additional legend parameters

        Returns:
            Self for chaining
        """
        self._legend = enabled
        self._legend_kwargs = kwargs
        return self

    def build(self) -> Tuple[plt.Figure, plt.Axes]:
        """
        Build and return figure and axes.

        Returns:
            Tuple of (Figure, Axes)
        """
        self.fig, self.ax = plt.subplots(figsize=self._figsize)

        if self._title:
            self.ax.set_title(self._title)

        if self._xlabel:
            self.ax.set_xlabel(self._xlabel)

        if self._ylabel:
            self.ax.set_ylabel(self._ylabel)

        if self._grid:
            self.ax.grid(**self._grid_kwargs)

        if self._legend:
            self.ax.legend(**self._legend_kwargs)

        return self.fig, self.ax
