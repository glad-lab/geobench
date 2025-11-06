#!/usr/bin/env python3
"""
Unified visualization package for adversarial SEO research.

This package provides comprehensive visualization tools for attack effectiveness,
cross-provider comparisons, and statistical analysis. It consolidates functionality
from legacy visualizations.py and cross_provider_visualizations.py modules.

Public API:
-----------
Classes:
    AttackVisualizer: Visualizations for attack effectiveness analysis
    ComparisonVisualizer: Cross-provider and cross-attack comparisons
    ReportGenerator: Automated report generation with charts

Configuration:
    VisualizationConfig: Unified configuration for all visualizations

Example:
    >>> from src.visualization import AttackVisualizer, ComparisonVisualizer
    >>> attack_viz = AttackVisualizer()
    >>> attack_viz.plot_success_rates(data).save("success_rates.png")
"""

from .base import BaseVisualizer, VisualizationConfig, ChartBuilder
from .attack_viz import AttackVisualizer
from .comparison_viz import ComparisonVisualizer
from .report_generator import ReportGenerator
from .formatters import DataFormatter
from .exporters import FigureExporter

__all__ = [
    'BaseVisualizer',
    'VisualizationConfig',
    'ChartBuilder',
    'AttackVisualizer',
    'ComparisonVisualizer',
    'ReportGenerator',
    'DataFormatter',
    'FigureExporter',
]

__version__ = '1.0.0'
