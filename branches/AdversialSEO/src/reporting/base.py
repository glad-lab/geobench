"""
Base classes for reporting framework.

Provides abstract interfaces and configuration for report generation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime


@dataclass
class ReportConfig:
    """Configuration for report generation."""

    # Report identity
    title: str
    description: str = ""

    # Output configuration
    output_format: str = "markdown"
    output_dir: str = "findings_showcase"

    # Content configuration
    include_visualizations: bool = True
    include_statistics: bool = True
    include_raw_data: bool = False

    # Visualization settings
    figure_format: str = "png"
    figure_dpi: int = 300

    # Statistical settings
    confidence_level: float = 0.95
    significance_threshold: float = 0.05

    # Metadata
    author: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "output_format": self.output_format,
            "output_dir": self.output_dir,
            "include_visualizations": self.include_visualizations,
            "include_statistics": self.include_statistics,
            "include_raw_data": self.include_raw_data,
            "figure_format": self.figure_format,
            "figure_dpi": self.figure_dpi,
            "confidence_level": self.confidence_level,
            "significance_threshold": self.significance_threshold,
            "author": self.author,
            "timestamp": self.timestamp,
        }


class BaseReport(ABC):
    """Abstract base class for reports."""

    def __init__(self, config: ReportConfig):
        """
        Initialize report.

        Args:
            config: Report configuration
        """
        self.config = config
        self.content: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.figures: List[Path] = []

    @abstractmethod
    def generate(self) -> str:
        """
        Generate report content.

        Returns:
            Generated report as string
        """
        pass

    @abstractmethod
    def save(self, filename: Optional[str] = None) -> Path:
        """
        Save report to file.

        Args:
            filename: Optional filename (auto-generated if not provided)

        Returns:
            Path to saved report
        """
        pass

    def add_section(self, title: str, content: str, level: int = 2) -> None:
        """
        Add a section to the report.

        Args:
            title: Section title
            content: Section content
            level: Heading level (1-6)
        """
        heading_prefix = "#" * level
        self.content.append(f"\n{heading_prefix} {title}\n\n{content}\n")

    def add_figure(self, figure_path: Path, caption: Optional[str] = None) -> None:
        """
        Add a figure to the report.

        Args:
            figure_path: Path to figure file
            caption: Optional figure caption
        """
        self.figures.append(figure_path)

        if self.config.output_format == "markdown":
            figure_ref = f"![{caption or 'Figure'}]({figure_path})"
            if caption:
                figure_ref += f"\n*{caption}*"
            self.content.append(f"\n{figure_ref}\n")

    def add_table(self, headers: List[str], rows: List[List[Any]], caption: Optional[str] = None) -> None:
        """
        Add a table to the report.

        Args:
            headers: Column headers
            rows: Table rows
            caption: Optional table caption
        """
        if self.config.output_format == "markdown":
            # Create markdown table
            table = self._create_markdown_table(headers, rows)
            if caption:
                table = f"*{caption}*\n\n{table}"
            self.content.append(f"\n{table}\n")

    def _create_markdown_table(self, headers: List[str], rows: List[List[Any]]) -> str:
        """Create markdown table."""
        # Header row
        header_row = "| " + " | ".join(str(h) for h in headers) + " |"

        # Separator row
        separator = "|" + "|".join([" --- " for _ in headers]) + "|"

        # Data rows
        data_rows = []
        for row in rows:
            row_str = "| " + " | ".join(str(cell) for cell in row) + " |"
            data_rows.append(row_str)

        return "\n".join([header_row, separator] + data_rows)

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to report.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def _create_header(self) -> str:
        """Create report header."""
        header = [
            f"# {self.config.title}",
        ]

        if self.config.description:
            header.append(f"\n{self.config.description}")

        if self.config.author:
            header.append(f"\n**Author**: {self.config.author}")

        header.append(f"\n**Generated**: {self.config.timestamp}")

        return "\n".join(header) + "\n\n---\n"

    def _create_footer(self) -> str:
        """Create report footer."""
        return f"\n\n---\n\n*Report generated on {self.config.timestamp}*\n"

    def _get_output_path(self, filename: Optional[str] = None) -> Path:
        """
        Get output path for report.

        Args:
            filename: Optional filename

        Returns:
            Path to output file
        """
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.config.title.lower().replace(' ', '_')}_{timestamp}"

        # Add extension based on format
        extension = self._get_file_extension()
        if not filename.endswith(extension):
            filename = f"{filename}{extension}"

        return output_dir / filename

    def _get_file_extension(self) -> str:
        """Get file extension based on output format."""
        extensions = {
            "markdown": ".md",
            "html": ".html",
            "latex": ".tex",
            "json": ".json",
        }
        return extensions.get(self.config.output_format, ".txt")
