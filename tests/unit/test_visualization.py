#!/usr/bin/env python3
"""
Unit tests for visualization package.

Tests all visualization components including base classes, chart factories,
attack visualizers, comparison visualizers, and report generation.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile
import shutil

from src.visualization import (
    VisualizationConfig,
    BaseVisualizer,
    ChartBuilder,
    AttackVisualizer,
    ComparisonVisualizer,
    ReportGenerator,
    DataFormatter,
    FigureExporter
)
from src.visualization.charts import ChartFactory


class TestVisualizationConfig:
    """Test VisualizationConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = VisualizationConfig()

        assert config.figsize == (12, 8)
        assert config.dpi == 300
        assert config.style == "seaborn-v0_8-whitegrid"
        assert config.color_palette == "husl"
        assert config.font_size == 11
        assert config.title_size == 14

    def test_provider_colors(self):
        """Test provider color mappings."""
        config = VisualizationConfig()

        assert 'openai' in config.provider_colors
        assert 'anthropic' in config.provider_colors
        assert 'bedrock' in config.provider_colors

    def test_attack_colors(self):
        """Test attack type color mappings."""
        config = VisualizationConfig()

        assert 'prompt_injection' in config.attack_colors
        assert 'discreditation' in config.attack_colors
        assert 'persuasion' in config.attack_colors

    def test_custom_config(self):
        """Test custom configuration."""
        config = VisualizationConfig(
            figsize=(10, 6),
            dpi=150,
            font_size=14
        )

        assert config.figsize == (10, 6)
        assert config.dpi == 150
        assert config.font_size == 14


class TestChartFactory:
    """Test ChartFactory class."""

    def test_bar_chart(self):
        """Test bar chart creation."""
        data = {'A': 10, 'B': 20, 'C': 15}

        fig = ChartFactory.bar_chart(
            data=data,
            title="Test Bar Chart",
            xlabel="Category",
            ylabel="Value"
        )

        assert fig is not None
        assert len(fig.axes) == 1

        plt.close(fig)

    def test_grouped_bar_chart(self):
        """Test grouped bar chart creation."""
        data = {
            'Category1': {'Series1': 10, 'Series2': 15},
            'Category2': {'Series1': 20, 'Series2': 25}
        }

        fig = ChartFactory.grouped_bar_chart(
            data=data,
            title="Test Grouped Bar Chart",
            xlabel="Category",
            ylabel="Value"
        )

        assert fig is not None
        plt.close(fig)

    def test_line_chart(self):
        """Test line chart creation."""
        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 15, 13, 17, 20]

        fig = ChartFactory.line_chart(
            x_data=x_data,
            y_data=y_data,
            title="Test Line Chart",
            xlabel="X",
            ylabel="Y"
        )

        assert fig is not None
        plt.close(fig)

    def test_heatmap(self):
        """Test heatmap creation."""
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        row_labels = ['Row1', 'Row2', 'Row3']
        col_labels = ['Col1', 'Col2', 'Col3']

        fig = ChartFactory.heatmap(
            data=data,
            title="Test Heatmap",
            row_labels=row_labels,
            col_labels=col_labels
        )

        assert fig is not None
        plt.close(fig)

    def test_scatter_plot(self):
        """Test scatter plot creation."""
        x_data = [1, 2, 3, 4, 5]
        y_data = [2, 4, 5, 4, 5]

        fig = ChartFactory.scatter_plot(
            x_data=x_data,
            y_data=y_data,
            title="Test Scatter Plot",
            xlabel="X",
            ylabel="Y"
        )

        assert fig is not None
        plt.close(fig)

    def test_box_plot(self):
        """Test box plot creation."""
        data = {
            'Group1': [1, 2, 3, 4, 5],
            'Group2': [2, 3, 4, 5, 6],
            'Group3': [3, 4, 5, 6, 7]
        }

        fig = ChartFactory.box_plot(
            data=data,
            title="Test Box Plot",
            xlabel="Group",
            ylabel="Value"
        )

        assert fig is not None
        plt.close(fig)

    def test_histogram(self):
        """Test histogram creation."""
        data = [1, 2, 2, 3, 3, 3, 4, 4, 5]

        fig = ChartFactory.histogram(
            data=data,
            title="Test Histogram",
            xlabel="Value"
        )

        assert fig is not None
        plt.close(fig)


class TestDataFormatter:
    """Test DataFormatter class."""

    def test_normalize_rates_decimal(self):
        """Test normalizing decimal rates."""
        rates = [0.25, 0.5, 0.75]
        normalized = DataFormatter.normalize_rates(rates, as_percentage=True)

        assert normalized == [25.0, 50.0, 75.0]

    def test_normalize_rates_percentage(self):
        """Test normalizing percentage rates."""
        rates = [25, 50, 75]
        normalized = DataFormatter.normalize_rates(rates, as_percentage=True)

        assert normalized == [25.0, 50.0, 75.0]

    def test_aggregate_by_category(self):
        """Test category aggregation."""
        results = [
            {'category': 'A', 'value': 10},
            {'category': 'A', 'value': 20},
            {'category': 'B', 'value': 15},
            {'category': 'B', 'value': 25}
        ]

        aggregated = DataFormatter.aggregate_by_category(
            results,
            'category',
            'value',
            'mean'
        )

        assert aggregated['A'] == 15.0
        assert aggregated['B'] == 20.0

    def test_compute_statistics(self):
        """Test statistics computation."""
        values = [1, 2, 3, 4, 5]
        stats = DataFormatter.compute_statistics(values)

        assert stats['mean'] == 3.0
        assert stats['median'] == 3.0
        assert stats['min'] == 1
        assert stats['max'] == 5
        assert stats['count'] == 5

    def test_format_percentage(self):
        """Test percentage formatting."""
        assert DataFormatter.format_percentage(0.25, decimals=1) == "25.0%"
        assert DataFormatter.format_percentage(50, decimals=1) == "50.0%"

    def test_prepare_heatmap_data(self):
        """Test heatmap data preparation."""
        data = {
            'Row1': {'Col1': 1, 'Col2': 2},
            'Row2': {'Col1': 3, 'Col2': 4}
        }

        array, rows, cols = DataFormatter.prepare_heatmap_data(data)

        assert array.shape == (2, 2)
        assert len(rows) == 2
        assert len(cols) == 2


class TestChartBuilder:
    """Test ChartBuilder class."""

    def test_builder_pattern(self):
        """Test fluent builder interface."""
        builder = ChartBuilder()

        fig, ax = (builder
                   .with_size(10, 6)
                   .with_title("Test Title")
                   .with_labels("X Label", "Y Label")
                   .with_grid(True, alpha=0.3)
                   .build())

        assert fig is not None
        assert ax is not None

        plt.close(fig)

    def test_builder_defaults(self):
        """Test builder with default values."""
        builder = ChartBuilder()
        fig, ax = builder.build()

        assert fig is not None
        plt.close(fig)


class TestAttackVisualizer:
    """Test AttackVisualizer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.viz = AttackVisualizer()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up after tests."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_plot_success_rates(self):
        """Test success rates plotting."""
        data = {
            'prompt_injection': 0.5,
            'discreditation': 0.3,
            'persuasion': 0.4
        }

        fig = self.viz.plot_success_rates(data)

        assert fig is not None
        plt.close(fig)

    def test_plot_positional_bias(self):
        """Test positional bias plotting."""
        data = {1: 0.3, 5: 0.5, 10: 0.6}

        fig = self.viz.plot_positional_bias(data)

        assert fig is not None
        plt.close(fig)

    def test_plot_rank_distribution(self):
        """Test rank distribution plotting."""
        ranks = [1, 1, 2, 3, 2, 1, 5, 4, 3, 2]

        fig = self.viz.plot_rank_distribution(ranks)

        assert fig is not None
        plt.close(fig)

    def test_plot_attack_effectiveness_summary(self):
        """Test attack effectiveness summary."""
        results = [
            {
                'query': 'test1',
                'attack_docs_retrieved': 2,
                'total_docs': 5,
                'true_effectiveness': 0.5
            },
            {
                'query': 'test2',
                'attack_docs_retrieved': 1,
                'total_docs': 5,
                'true_effectiveness': 0.3
            }
        ]

        fig = self.viz.plot_attack_effectiveness_summary(results)

        assert fig is not None
        plt.close(fig)

    def test_plot_prisoners_dilemma(self):
        """Test prisoner's dilemma plotting."""
        data = {0: 1.0, 1: 0.8, 2: 0.6, 3: 0.4}

        fig = self.viz.plot_prisoners_dilemma(data)

        assert fig is not None
        plt.close(fig)

    def test_save_figure(self):
        """Test figure saving."""
        data = {'A': 0.5, 'B': 0.3}
        fig = self.viz.plot_success_rates(data)

        save_path = self.temp_dir / "test_chart.png"
        path = self.viz.save_figure(fig, str(save_path))

        assert Path(path).exists()
        plt.close(fig)


class TestComparisonVisualizer:
    """Test ComparisonVisualizer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.viz = ComparisonVisualizer()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up after tests."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_plot_provider_comparison(self):
        """Test provider comparison plotting."""
        provider_results = {
            'openai': {
                'success_rate': 0.5,
                'avg_response_time': 1.2,
                'error_rate': 0.05,
                'avg_position_change': 2.3
            },
            'anthropic': {
                'success_rate': 0.6,
                'avg_response_time': 0.8,
                'error_rate': 0.03,
                'avg_position_change': 3.1
            }
        }

        fig = self.viz.plot_provider_comparison(provider_results)

        assert fig is not None
        plt.close(fig)

    def test_plot_transferability_heatmap(self):
        """Test transferability heatmap."""
        matrix = {
            'openai': {'prompt_injection': 0.5, 'discreditation': 0.3},
            'anthropic': {'prompt_injection': 0.6, 'discreditation': 0.4}
        }

        fig = self.viz.plot_transferability_heatmap(matrix)

        assert fig is not None
        plt.close(fig)

    def test_plot_attack_type_effectiveness(self):
        """Test attack type effectiveness plotting."""
        provider_results = {
            'openai': {
                'attack_type_breakdown': {
                    'prompt_injection': {'success_rate': 0.5},
                    'discreditation': {'success_rate': 0.3}
                }
            },
            'anthropic': {
                'attack_type_breakdown': {
                    'prompt_injection': {'success_rate': 0.6},
                    'discreditation': {'success_rate': 0.4}
                }
            }
        }

        fig = self.viz.plot_attack_type_effectiveness(provider_results)

        assert fig is not None
        plt.close(fig)


class TestFigureExporter:
    """Test FigureExporter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up after tests."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_export_to_png(self):
        """Test PNG export."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        save_path = self.temp_dir / "test.png"
        path = FigureExporter.export_to_png(fig, str(save_path))

        assert Path(path).exists()
        assert Path(path).suffix == '.png'

        plt.close(fig)

    def test_export_to_pdf(self):
        """Test PDF export."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        save_path = self.temp_dir / "test.pdf"
        path = FigureExporter.export_to_pdf(fig, str(save_path))

        assert Path(path).exists()
        assert Path(path).suffix == '.pdf'

        plt.close(fig)

    def test_export_multi_format(self):
        """Test multi-format export."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        save_path = self.temp_dir / "test"
        paths = FigureExporter.export_multi_format(
            fig,
            str(save_path),
            formats=['png', 'pdf']
        )

        assert 'png' in paths
        assert 'pdf' in paths
        assert Path(paths['png']).exists()
        assert Path(paths['pdf']).exists()

        plt.close(fig)


class TestReportGenerator:
    """Test ReportGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.generator = ReportGenerator(output_dir=str(self.temp_dir))

    def teardown_method(self):
        """Clean up after tests."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_generate_attack_report(self):
        """Test attack report generation."""
        results = [
            {
                'query': 'test1',
                'attack_type': 'prompt_injection',
                'attack_docs_retrieved': 2,
                'total_docs': 5,
                'true_effectiveness': 0.5
            },
            {
                'query': 'test2',
                'attack_type': 'discreditation',
                'attack_docs_retrieved': 1,
                'total_docs': 5,
                'true_effectiveness': 0.3
            }
        ]

        saved_paths = self.generator.generate_attack_report(
            results,
            report_name="test_attack_report",
            formats=['png']
        )

        assert len(saved_paths) > 0

        # Check report directory exists
        report_dir = self.temp_dir / "test_attack_report"
        assert report_dir.exists()
        assert (report_dir / "figures").exists()
        assert (report_dir / "index.html").exists()
        assert (report_dir / "metadata.json").exists()

    def test_generate_comparison_report(self):
        """Test comparison report generation."""
        provider_results = {
            'openai': {
                'success_rate': 0.5,
                'avg_response_time': 1.2,
                'error_rate': 0.05,
                'avg_position_change': 2.3,
                'attack_type_breakdown': {
                    'prompt_injection': {'success_rate': 0.5}
                }
            },
            'anthropic': {
                'success_rate': 0.6,
                'avg_response_time': 0.8,
                'error_rate': 0.03,
                'avg_position_change': 3.1,
                'attack_type_breakdown': {
                    'prompt_injection': {'success_rate': 0.6}
                }
            }
        }

        saved_paths = self.generator.generate_comparison_report(
            provider_results,
            report_name="test_comparison_report",
            formats=['png']
        )

        assert len(saved_paths) > 0

        # Check report directory exists
        report_dir = self.temp_dir / "test_comparison_report"
        assert report_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
