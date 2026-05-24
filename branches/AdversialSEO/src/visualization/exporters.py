#!/usr/bin/env python3
"""
Export utilities for saving visualizations in different formats.

Provides utilities for exporting figures to PNG, PDF, SVG, and HTML formats,
with support for batch operations and quality control.
"""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FigureExporter:
    """
    Utility class for exporting matplotlib figures to various formats.

    Supports PNG, PDF, SVG, and HTML exports with consistent quality settings
    and batch processing capabilities.
    """

    DEFAULT_DPI = 300
    SUPPORTED_FORMATS = ['png', 'pdf', 'svg', 'html']

    @staticmethod
    def export_figure(
        fig: plt.Figure,
        filepath: str,
        format: str = 'png',
        dpi: int = DEFAULT_DPI,
        transparent: bool = False,
        **kwargs
    ) -> str:
        """
        Export figure to file with specified format.

        Args:
            fig: Matplotlib Figure to export
            filepath: Output file path
            format: Output format (png, pdf, svg, html)
            dpi: Resolution for raster formats
            transparent: Whether to use transparent background
            **kwargs: Additional arguments for savefig

        Returns:
            Path to saved file

        Raises:
            ValueError: If format is not supported
        """
        format = format.lower()

        if format not in FigureExporter.SUPPORTED_FORMATS:
            raise ValueError(
                f"Format '{format}' not supported. "
                f"Supported formats: {', '.join(FigureExporter.SUPPORTED_FORMATS)}"
            )

        # Ensure file has correct extension
        filepath = Path(filepath)
        if not filepath.suffix or filepath.suffix[1:] != format:
            filepath = filepath.with_suffix(f'.{format}')

        # Create directory if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Prepare save arguments
        save_kwargs = {
            'dpi': dpi,
            'bbox_inches': 'tight',
            'transparent': transparent,
            'format': format
        }
        save_kwargs.update(kwargs)

        # Save figure
        try:
            fig.savefig(filepath, **save_kwargs)
            logger.info(f"Exported figure to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to export figure to {filepath}: {e}")
            raise

    @staticmethod
    def export_to_png(
        fig: plt.Figure,
        filepath: str,
        dpi: int = DEFAULT_DPI,
        **kwargs
    ) -> str:
        """
        Export figure to PNG format.

        Args:
            fig: Matplotlib Figure to export
            filepath: Output file path
            dpi: Resolution
            **kwargs: Additional arguments for savefig

        Returns:
            Path to saved file
        """
        return FigureExporter.export_figure(fig, filepath, 'png', dpi, **kwargs)

    @staticmethod
    def export_to_pdf(
        fig: plt.Figure,
        filepath: str,
        **kwargs
    ) -> str:
        """
        Export figure to PDF format (vector).

        Args:
            fig: Matplotlib Figure to export
            filepath: Output file path
            **kwargs: Additional arguments for savefig

        Returns:
            Path to saved file
        """
        return FigureExporter.export_figure(fig, filepath, 'pdf', **kwargs)

    @staticmethod
    def export_to_svg(
        fig: plt.Figure,
        filepath: str,
        **kwargs
    ) -> str:
        """
        Export figure to SVG format (vector).

        Args:
            fig: Matplotlib Figure to export
            filepath: Output file path
            **kwargs: Additional arguments for savefig

        Returns:
            Path to saved file
        """
        return FigureExporter.export_figure(fig, filepath, 'svg', **kwargs)

    @staticmethod
    def export_batch(
        figures: Dict[str, plt.Figure],
        output_dir: str,
        format: str = 'png',
        dpi: int = DEFAULT_DPI,
        **kwargs
    ) -> List[str]:
        """
        Export multiple figures to files.

        Args:
            figures: Dict mapping filenames to Figures
            output_dir: Output directory
            format: Output format
            dpi: Resolution for raster formats
            **kwargs: Additional arguments for savefig

        Returns:
            List of paths to saved files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = []

        for filename, fig in figures.items():
            filepath = output_dir / filename

            try:
                path = FigureExporter.export_figure(
                    fig, filepath, format, dpi, **kwargs
                )
                saved_paths.append(path)
            except Exception as e:
                logger.error(f"Failed to export {filename}: {e}")

        logger.info(f"Exported {len(saved_paths)} figures to {output_dir}")
        return saved_paths

    @staticmethod
    def export_multi_format(
        fig: plt.Figure,
        base_filepath: str,
        formats: List[str] = ['png', 'pdf'],
        dpi: int = DEFAULT_DPI,
        **kwargs
    ) -> Dict[str, str]:
        """
        Export figure to multiple formats.

        Args:
            fig: Matplotlib Figure to export
            base_filepath: Base file path (without extension)
            formats: List of formats to export
            dpi: Resolution for raster formats
            **kwargs: Additional arguments for savefig

        Returns:
            Dict mapping formats to saved file paths
        """
        base_filepath = Path(base_filepath).with_suffix('')
        saved_paths = {}

        for format in formats:
            try:
                path = FigureExporter.export_figure(
                    fig, base_filepath, format, dpi, **kwargs
                )
                saved_paths[format] = path
            except Exception as e:
                logger.error(f"Failed to export to {format}: {e}")

        return saved_paths

    @staticmethod
    def close_all_figures():
        """Close all open matplotlib figures to free memory."""
        plt.close('all')
        logger.debug("Closed all matplotlib figures")


class ReportExporter:
    """
    Utility for exporting visualization reports.

    Combines multiple figures into organized output directories
    with metadata and index files.
    """

    @staticmethod
    def create_report_directory(
        base_dir: str,
        report_name: str
    ) -> Path:
        """
        Create organized directory structure for report.

        Args:
            base_dir: Base output directory
            report_name: Name of report

        Returns:
            Path to report directory
        """
        report_dir = Path(base_dir) / report_name
        report_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (report_dir / 'figures').mkdir(exist_ok=True)
        (report_dir / 'data').mkdir(exist_ok=True)

        logger.info(f"Created report directory: {report_dir}")
        return report_dir

    @staticmethod
    def export_report_figures(
        figures: Dict[str, plt.Figure],
        report_dir: Path,
        formats: List[str] = ['png'],
        dpi: int = 300
    ) -> Dict[str, List[str]]:
        """
        Export all figures for a report.

        Args:
            figures: Dict mapping figure names to Figures
            report_dir: Report directory
            formats: List of formats to export
            dpi: Resolution for raster formats

        Returns:
            Dict mapping figure names to list of saved paths
        """
        figures_dir = report_dir / 'figures'
        results = {}

        for fig_name, fig in figures.items():
            base_path = figures_dir / fig_name
            saved_paths = []

            for format in formats:
                try:
                    path = FigureExporter.export_figure(
                        fig, base_path, format, dpi
                    )
                    saved_paths.append(path)
                except Exception as e:
                    logger.error(f"Failed to export {fig_name} to {format}: {e}")

            results[fig_name] = saved_paths

        return results

    @staticmethod
    def create_html_index(
        report_dir: Path,
        figure_paths: Dict[str, List[str]],
        title: str = "Visualization Report"
    ) -> str:
        """
        Create HTML index file for report.

        Args:
            report_dir: Report directory
            figure_paths: Dict mapping figure names to paths
            title: Report title

        Returns:
            Path to HTML index file
        """
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        .figure {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .figure h2 {{
            color: #555;
            margin-top: 0;
        }}
        .figure img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
"""

        for fig_name, paths in figure_paths.items():
            # Find PNG for display
            png_path = next((p for p in paths if p.endswith('.png')), paths[0])
            rel_path = Path(png_path).relative_to(report_dir)

            html_content += f"""
    <div class="figure">
        <h2>{fig_name.replace('_', ' ').title()}</h2>
        <img src="{rel_path}" alt="{fig_name}">
    </div>
"""

        html_content += """
</body>
</html>
"""

        index_path = report_dir / 'index.html'
        index_path.write_text(html_content)

        logger.info(f"Created HTML index: {index_path}")
        return str(index_path)
