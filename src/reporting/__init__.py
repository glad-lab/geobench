"""
Reporting framework for adversarial SEO research.

This package provides comprehensive report generation including findings showcases,
paper comparisons, and statistical analysis reports.
"""

from .base import ReportConfig, BaseReport
from .findings import FindingsReport, FindingsReportGenerator
from .comparison import PaperComparisonReport, ComparisonAnalyzer
from .exporters import ReportExporter, ExportFormat

__all__ = [
    "ReportConfig",
    "BaseReport",
    "FindingsReport",
    "FindingsReportGenerator",
    "PaperComparisonReport",
    "ComparisonAnalyzer",
    "ReportExporter",
    "ExportFormat",
]

__version__ = "1.0.0"
