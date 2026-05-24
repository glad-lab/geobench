"""
Report export utilities.

Supports exporting reports to multiple formats (JSON, Markdown, HTML, LaTeX).
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    LATEX = "latex"
    PDF = "pdf"


class ReportExporter:
    """Exporter for converting reports to different formats."""

    def __init__(self, output_dir: str = "findings_showcase/exports"):
        """
        Initialize report exporter.

        Args:
            output_dir: Directory for exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        report_data: Dict[str, Any],
        format: ExportFormat,
        filename: Optional[str] = None
    ) -> Path:
        """
        Export report to specified format.

        Args:
            report_data: Report data to export
            format: Target export format
            filename: Optional output filename

        Returns:
            Path to exported file
        """
        if format == ExportFormat.JSON:
            return self.export_json(report_data, filename)
        elif format == ExportFormat.MARKDOWN:
            return self.export_markdown(report_data, filename)
        elif format == ExportFormat.HTML:
            return self.export_html(report_data, filename)
        elif format == ExportFormat.LATEX:
            return self.export_latex(report_data, filename)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def export_json(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Export report as JSON."""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        elif not filename.endswith(".json"):
            filename = f"{filename}.json"

        output_path = self.output_dir / filename

        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        logger.info(f"Exported JSON report to {output_path}")
        return output_path

    def export_markdown(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Export report as Markdown."""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        elif not filename.endswith(".md"):
            filename = f"{filename}.md"

        output_path = self.output_dir / filename

        markdown_content = self._generate_markdown(report_data)

        with open(output_path, "w") as f:
            f.write(markdown_content)

        logger.info(f"Exported Markdown report to {output_path}")
        return output_path

    def _generate_markdown(self, report_data: Dict[str, Any]) -> str:
        """Generate Markdown content from report data."""
        title = report_data.get("title", "Report")
        timestamp = report_data.get("timestamp", datetime.now().isoformat())

        markdown = f"""# {title}

**Generated**: {timestamp}

---

"""

        # Add summary section
        if "summary" in report_data:
            markdown += "## Summary\n\n"
            for key, value in report_data["summary"].items():
                markdown += f"- **{key}**: {value}\n"
            markdown += "\n"

        # Add findings section
        if "findings" in report_data:
            markdown += "## Findings\n\n"
            for finding in report_data["findings"]:
                markdown += f"### {finding.get('name', 'Finding')}\n\n"
                markdown += f"{finding.get('description', '')}\n\n"

        # Add statistics section
        if "statistics" in report_data:
            markdown += "## Statistical Analysis\n\n"
            markdown += f"{report_data['statistics']}\n\n"

        markdown += f"\n---\n\n*Report generated on {timestamp}*\n"

        return markdown

    def export_html(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Export report as HTML."""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        elif not filename.endswith(".html"):
            filename = f"{filename}.html"

        output_path = self.output_dir / filename

        html_content = self._generate_html(report_data)

        with open(output_path, "w") as f:
            f.write(html_content)

        logger.info(f"Exported HTML report to {output_path}")
        return output_path

    def _generate_html(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content from report data."""
        title = report_data.get("title", "Report")
        timestamp = report_data.get("timestamp", datetime.now().isoformat())

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px;
            line-height: 1.6;
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .metric {{
            background-color: #ecf0f1;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p><strong>Generated:</strong> {timestamp}</p>
    <hr>
"""

        # Add summary section
        if "summary" in report_data:
            html += "    <div class=\"metric\">\n"
            html += "        <h2>Summary</h2>\n"
            for key, value in report_data["summary"].items():
                html += f"        <p><strong>{key}:</strong> {value}</p>\n"
            html += "    </div>\n"

        # Add findings section
        if "findings" in report_data:
            html += "    <h2>Findings</h2>\n"
            for finding in report_data["findings"]:
                html += "    <div class=\"metric\">\n"
                html += f"        <h3>{finding.get('name', 'Finding')}</h3>\n"
                html += f"        <p>{finding.get('description', '')}</p>\n"
                html += "    </div>\n"

        html += f"""    <div class="footer">
        <p><em>Report generated on {timestamp}</em></p>
    </div>
</body>
</html>
"""
        return html

    def export_latex(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Export report as LaTeX."""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex"
        elif not filename.endswith(".tex"):
            filename = f"{filename}.tex"

        output_path = self.output_dir / filename

        latex_content = self._generate_latex(report_data)

        with open(output_path, "w") as f:
            f.write(latex_content)

        logger.info(f"Exported LaTeX report to {output_path}")
        return output_path

    def _generate_latex(self, report_data: Dict[str, Any]) -> str:
        """Generate LaTeX content from report data."""
        title = report_data.get("title", "Report")
        timestamp = report_data.get("timestamp", datetime.now().isoformat())

        latex = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{booktabs}

\title{""" + title + r"""}
\author{Adversarial SEO Research}
\date{""" + timestamp + r"""}

\begin{document}

\maketitle

\section{Summary}

"""

        # Add summary
        if "summary" in report_data:
            for key, value in report_data["summary"].items():
                latex += f"\\textbf{{{key}}}: {value}\n\n"

        latex += r"""
\section{Findings}

"""

        # Add findings
        if "findings" in report_data:
            for finding in report_data["findings"]:
                latex += f"\\subsection{{{finding.get('name', 'Finding')}}}\n\n"
                latex += f"{finding.get('description', '')}\n\n"

        latex += r"""
\end{document}
"""
        return latex
