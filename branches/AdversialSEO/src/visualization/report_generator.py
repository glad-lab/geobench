#!/usr/bin/env python3
"""
Automated report generation with charts.

Provides high-level interface for generating comprehensive visualization reports
from experimental results with minimal configuration.
"""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime

from .base import VisualizationConfig
from .attack_viz import AttackVisualizer
from .comparison_viz import ComparisonVisualizer
from .exporters import FigureExporter, ReportExporter

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Automated report generation with comprehensive visualizations.

    Provides high-level interface for creating complete visualization reports
    from experimental results, including attack effectiveness, cross-provider
    comparisons, and statistical analysis.
    """

    def __init__(
        self,
        output_dir: str = "visualizations/reports",
        config: Optional[VisualizationConfig] = None
    ):
        """
        Initialize report generator.

        Args:
            output_dir: Base directory for report output
            config: Visualization configuration
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.config = config or VisualizationConfig()

        self.attack_viz = AttackVisualizer(config)
        self.comparison_viz = ComparisonVisualizer(config)

        logger.info(f"ReportGenerator initialized with output: {self.output_dir}")

    def generate_attack_report(
        self,
        results: List[Dict[str, Any]],
        report_name: str = "attack_effectiveness",
        formats: List[str] = ['png', 'pdf']
    ) -> Dict[str, List[str]]:
        """
        Generate comprehensive attack effectiveness report.

        Args:
            results: List of experimental results
            report_name: Name for the report
            formats: Output formats for figures

        Returns:
            Dict mapping figure names to saved file paths
        """
        logger.info(f"Generating attack report: {report_name}")

        # Create report directory
        report_dir = ReportExporter.create_report_directory(
            str(self.output_dir),
            report_name
        )

        figures = {}

        # 1. Attack effectiveness summary
        try:
            fig = self.attack_viz.plot_attack_effectiveness_summary(results)
            figures['attack_effectiveness_summary'] = fig
        except Exception as e:
            logger.error(f"Failed to create effectiveness summary: {e}")

        # 2. Attack type comparison
        try:
            # Group by attack type
            attack_data = {}
            for result in results:
                attack_type = result.get('attack_type', 'unknown')
                if attack_type not in attack_data:
                    attack_data[attack_type] = []

                effectiveness = result.get(
                    'true_effectiveness',
                    result.get('position_1_success_rate', 0)
                )
                attack_data[attack_type].append(effectiveness)

            if attack_data:
                fig = self.attack_viz.plot_attack_type_comparison(attack_data)
                figures['attack_type_comparison'] = fig
        except Exception as e:
            logger.error(f"Failed to create attack type comparison: {e}")

        # 3. Rank distribution (if available)
        try:
            ranks = [
                result.get('final_rank', result.get('rank', 0))
                for result in results
                if 'final_rank' in result or 'rank' in result
            ]

            if ranks:
                fig = self.attack_viz.plot_rank_distribution(ranks)
                figures['rank_distribution'] = fig
        except Exception as e:
            logger.error(f"Failed to create rank distribution: {e}")

        # Export all figures
        saved_paths = ReportExporter.export_report_figures(
            figures,
            report_dir,
            formats=formats,
            dpi=self.config.dpi
        )

        # Create HTML index
        ReportExporter.create_html_index(
            report_dir,
            saved_paths,
            title=f"Attack Effectiveness Report - {report_name}"
        )

        # Save metadata
        self._save_metadata(
            report_dir,
            {
                'report_type': 'attack_effectiveness',
                'results_count': len(results),
                'figures_generated': list(figures.keys()),
                'timestamp': datetime.now().isoformat()
            }
        )

        # Close figures
        for fig in figures.values():
            plt.close(fig)

        logger.info(f"Attack report generated: {report_dir}")
        return saved_paths

    def generate_comparison_report(
        self,
        provider_results: Dict[str, Dict[str, Any]],
        cross_provider_results: Optional[List[Dict[str, Any]]] = None,
        report_name: str = "cross_provider_comparison",
        formats: List[str] = ['png', 'pdf']
    ) -> Dict[str, List[str]]:
        """
        Generate cross-provider comparison report.

        Args:
            provider_results: Dict mapping providers to results
            cross_provider_results: Optional list of detailed results
            report_name: Name for the report
            formats: Output formats for figures

        Returns:
            Dict mapping figure names to saved file paths
        """
        logger.info(f"Generating comparison report: {report_name}")

        # Create report directory
        report_dir = ReportExporter.create_report_directory(
            str(self.output_dir),
            report_name
        )

        figures = {}

        # 1. Provider performance comparison
        try:
            fig = self.comparison_viz.plot_provider_comparison(provider_results)
            figures['provider_comparison'] = fig
        except Exception as e:
            logger.error(f"Failed to create provider comparison: {e}")

        # 2. Attack type effectiveness across providers
        try:
            fig = self.comparison_viz.plot_attack_type_effectiveness(provider_results)
            figures['attack_type_effectiveness'] = fig
        except Exception as e:
            logger.error(f"Failed to create attack type effectiveness: {e}")

        # 3. Response time distribution (if detailed results available)
        if cross_provider_results:
            try:
                fig = self.comparison_viz.plot_response_time_distribution(
                    cross_provider_results
                )
                figures['response_time_distribution'] = fig
            except Exception as e:
                logger.error(f"Failed to create response time distribution: {e}")

        # Export all figures
        saved_paths = ReportExporter.export_report_figures(
            figures,
            report_dir,
            formats=formats,
            dpi=self.config.dpi
        )

        # Create HTML index
        ReportExporter.create_html_index(
            report_dir,
            saved_paths,
            title=f"Cross-Provider Comparison Report - {report_name}"
        )

        # Save metadata
        self._save_metadata(
            report_dir,
            {
                'report_type': 'cross_provider_comparison',
                'providers': list(provider_results.keys()),
                'figures_generated': list(figures.keys()),
                'timestamp': datetime.now().isoformat()
            }
        )

        # Close figures
        for fig in figures.values():
            plt.close(fig)

        logger.info(f"Comparison report generated: {report_dir}")
        return saved_paths

    def generate_complete_dashboard(
        self,
        data: Dict[str, Any],
        report_name: str = "complete_analysis",
        formats: List[str] = ['png', 'pdf']
    ) -> Dict[str, List[str]]:
        """
        Generate complete analysis dashboard from all available data.

        Args:
            data: Complete experimental data including:
                - provider_results: Provider performance metrics
                - attack_results: Attack effectiveness results
                - transferability_matrix: Cross-provider transferability
                - cost_analysis: Cost estimates (optional)
                - statistical_tests: Statistical analysis results (optional)
            report_name: Name for the report
            formats: Output formats for figures

        Returns:
            Dict mapping figure names to saved file paths
        """
        logger.info(f"Generating complete dashboard: {report_name}")

        # Create report directory
        report_dir = ReportExporter.create_report_directory(
            str(self.output_dir),
            report_name
        )

        figures = {}

        # Attack visualizations
        if 'attack_results' in data:
            try:
                fig = self.attack_viz.plot_attack_effectiveness_summary(
                    data['attack_results']
                )
                figures['attack_effectiveness'] = fig
            except Exception as e:
                logger.error(f"Failed to create attack effectiveness: {e}")

        # Provider comparisons
        if 'provider_results' in data:
            try:
                fig = self.comparison_viz.plot_provider_comparison(
                    data['provider_results']
                )
                figures['provider_comparison'] = fig
            except Exception as e:
                logger.error(f"Failed to create provider comparison: {e}")

        # Transferability heatmap
        if 'transferability_matrix' in data:
            try:
                fig = self.comparison_viz.plot_transferability_heatmap(
                    data['transferability_matrix']
                )
                figures['transferability_heatmap'] = fig
            except Exception as e:
                logger.error(f"Failed to create transferability heatmap: {e}")

        # Cost-benefit analysis
        if 'cost_analysis' in data and 'provider_results' in data:
            try:
                fig = self.comparison_viz.plot_cost_benefit_analysis(
                    data['cost_analysis'],
                    data['provider_results']
                )
                figures['cost_benefit_analysis'] = fig
            except Exception as e:
                logger.error(f"Failed to create cost-benefit analysis: {e}")

        # Statistical significance
        if 'statistical_tests' in data:
            try:
                fig = self.comparison_viz.plot_statistical_significance(
                    data['statistical_tests']
                )
                figures['statistical_significance'] = fig
            except Exception as e:
                logger.error(f"Failed to create statistical significance: {e}")

        # Prisoner's dilemma (if available)
        if 'prisoners_dilemma' in data:
            try:
                fig = self.attack_viz.plot_prisoners_dilemma(
                    data['prisoners_dilemma']
                )
                figures['prisoners_dilemma'] = fig
            except Exception as e:
                logger.error(f"Failed to create prisoner's dilemma: {e}")

        # Export all figures
        saved_paths = ReportExporter.export_report_figures(
            figures,
            report_dir,
            formats=formats,
            dpi=self.config.dpi
        )

        # Create HTML index
        ReportExporter.create_html_index(
            report_dir,
            saved_paths,
            title=f"Complete Analysis Dashboard - {report_name}"
        )

        # Save metadata
        self._save_metadata(
            report_dir,
            {
                'report_type': 'complete_dashboard',
                'data_sections': list(data.keys()),
                'figures_generated': list(figures.keys()),
                'timestamp': datetime.now().isoformat()
            }
        )

        # Close figures
        for fig in figures.values():
            plt.close(fig)

        logger.info(f"Complete dashboard generated: {report_dir}")
        return saved_paths

    def generate_from_file(
        self,
        data_file: str,
        report_name: Optional[str] = None,
        formats: List[str] = ['png', 'pdf']
    ) -> Dict[str, List[str]]:
        """
        Generate report from JSON data file.

        Args:
            data_file: Path to JSON file with experimental results
            report_name: Name for the report (default: filename)
            formats: Output formats for figures

        Returns:
            Dict mapping figure names to saved file paths
        """
        data_path = Path(data_file)

        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")

        # Load data
        with open(data_path, 'r') as f:
            data = json.load(f)

        # Use filename as report name if not provided
        if report_name is None:
            report_name = data_path.stem

        # Determine report type and generate
        if 'provider_results' in data or 'transferability_matrix' in data:
            return self.generate_complete_dashboard(data, report_name, formats)
        elif 'attack_results' in data or isinstance(data, list):
            results = data if isinstance(data, list) else data.get('attack_results', [])
            return self.generate_attack_report(results, report_name, formats)
        else:
            logger.warning("Could not determine report type from data structure")
            return {}

    def _save_metadata(self, report_dir: Path, metadata: Dict[str, Any]):
        """
        Save report metadata to JSON file.

        Args:
            report_dir: Report directory
            metadata: Metadata dictionary
        """
        metadata_path = report_dir / 'metadata.json'

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.debug(f"Saved metadata to {metadata_path}")
