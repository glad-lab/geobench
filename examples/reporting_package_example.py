"""
Example usage of the reporting package.

Demonstrates how to use the refactored reporting framework for generating
findings reports and paper comparisons.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from reporting import (
    ReportConfig,
    FindingsReportGenerator,
    ComparisonAnalyzer,
    ReportExporter,
    ExportFormat
)


def example_findings_report():
    """Example: Generate findings report."""
    print("=" * 80)
    print("Example 1: Findings Report Generation")
    print("=" * 80)

    # Create report configuration
    config = ReportConfig(
        title="Adversarial SEO Findings Report",
        description="Comprehensive findings from reproduction study",
        output_format="markdown",
        output_dir="findings_showcase",
        include_visualizations=True,
        include_statistics=True,
        author="Research Team"
    )

    # Create report generator
    generator = FindingsReportGenerator(
        config=config,
        results_dir="data/results"
    )

    # Generate report (would load actual results in practice)
    print("\nGenerating findings report...")
    print("Configuration:")
    print(f"  Title: {config.title}")
    print(f"  Format: {config.output_format}")
    print(f"  Include visualizations: {config.include_visualizations}")
    print(f"  Include statistics: {config.include_statistics}")

    # In practice, you would call:
    # report_content = generator.generate()
    # output_path = generator.save()
    # print(f"\nReport saved to: {output_path}")

    print("\n" + "=" * 80)


def example_paper_comparison():
    """Example: Paper comparison analysis."""
    print("\n" + "=" * 80)
    print("Example 2: Paper Comparison Analysis")
    print("=" * 80)

    # Create comparison analyzer
    analyzer = ComparisonAnalyzer()

    # Simulate experiment data
    experiment_data = {
        "single_attack_results": [{
            "position_1_success_rate": 0.38
        }],
        "prisoners_dilemma_results": {
            "baseline_performance": 0.85,
            "all_attack_performance": 0.62,
            "degradation": 0.27
        },
        "positional_bias_results": {
            "start_position_effectiveness": 0.30,
            "end_position_effectiveness": 0.48,
            "bias_ratio": 1.6
        }
    }

    # Analyze findings
    print("\nAnalyzing findings against paper benchmarks...")
    comparisons = analyzer.analyze_findings(experiment_data)

    # Print results
    print(f"\nComparison Results:")
    print(f"{'Metric':<40} {'Paper':<12} {'Our Study':<15} {'Status':<12}")
    print("-" * 79)

    for comp in comparisons:
        print(f"{comp.metric_name:<40} {comp.paper_value:<12.1%} {comp.our_value:<15.1%} {comp.replication_status.upper():<12}")

    # Calculate overall score
    replication_scores = {"excellent": 1.0, "good": 0.8, "partial": 0.6, "poor": 0.2}
    overall = sum(replication_scores.get(c.replication_status, 0) for c in comparisons) / len(comparisons)
    print(f"\nOverall Reproduction Score: {overall:.1%}")

    print("\n" + "=" * 80)


def example_report_export():
    """Example: Export reports to different formats."""
    print("\n" + "=" * 80)
    print("Example 3: Report Export to Multiple Formats")
    print("=" * 80)

    # Create exporter
    exporter = ReportExporter(output_dir="findings_showcase/exports")

    # Simulate report data
    report_data = {
        "title": "Adversarial SEO Findings",
        "timestamp": "2024-01-15T10:30:00",
        "summary": {
            "Total Experiments": 150,
            "Success Rate": "38%",
            "Reproduction Score": "85%"
        },
        "findings": [
            {
                "name": "Single Attack Effectiveness",
                "description": "Attacks achieved 38% position-1 success rate"
            },
            {
                "name": "Prisoner's Dilemma",
                "description": "27% collective degradation observed"
            }
        ]
    }

    # Export to different formats
    print("\nExporting report to multiple formats...")

    # JSON export
    print("\n1. JSON Export:")
    # json_path = exporter.export(report_data, ExportFormat.JSON, "example_report")
    # print(f"   Saved to: {json_path}")
    print("   Format: Structured data, machine-readable")

    # Markdown export
    print("\n2. Markdown Export:")
    # md_path = exporter.export(report_data, ExportFormat.MARKDOWN, "example_report")
    # print(f"   Saved to: {md_path}")
    print("   Format: Human-readable, version control friendly")

    # HTML export
    print("\n3. HTML Export:")
    # html_path = exporter.export(report_data, ExportFormat.HTML, "example_report")
    # print(f"   Saved to: {html_path}")
    print("   Format: Web-ready, styled presentation")

    # LaTeX export
    print("\n4. LaTeX Export:")
    # latex_path = exporter.export(report_data, ExportFormat.LATEX, "example_report")
    # print(f"   Saved to: {latex_path}")
    print("   Format: Publication-ready, academic papers")

    print("\n(File creation commented out for demonstration)")
    print("\n" + "=" * 80)


def example_custom_report():
    """Example: Create custom report with sections and tables."""
    print("\n" + "=" * 80)
    print("Example 4: Custom Report with Sections and Tables")
    print("=" * 80)

    from reporting.base import BaseReport

    class CustomReport(BaseReport):
        """Custom report implementation."""

        def generate(self) -> str:
            """Generate custom report."""
            # Add header
            content = self._create_header()

            # Add summary section
            self.add_section(
                "Summary",
                "This is a custom report demonstrating the BaseReport API.",
                level=2
            )

            # Add table
            headers = ["Attack Type", "Success Rate", "Position Change"]
            rows = [
                ["Prompt Injection", "42%", "+2.3"],
                ["Discreditation", "28%", "+1.5"],
                ["Persuasion", "35%", "+1.8"]
            ]
            self.add_table(headers, rows, caption="Attack Effectiveness Results")

            # Add metadata
            self.add_metadata("experiments", 150)
            self.add_metadata("models_tested", ["gpt-3.5-turbo", "claude-3-haiku"])

            # Combine sections
            content += "\n".join(self.content)
            content += self._create_footer()

            return content

        def save(self, filename=None):
            """Save report."""
            output_path = self._get_output_path(filename)
            content = self.generate()

            with open(output_path, "w") as f:
                f.write(content)

            return output_path

    # Create and generate custom report
    config = ReportConfig(
        title="Custom Findings Report",
        description="Demonstrating custom report generation",
        output_format="markdown"
    )

    report = CustomReport(config)
    print("\nGenerating custom report...")
    print("Report structure:")
    print("  - Header with title and metadata")
    print("  - Summary section")
    print("  - Data table with results")
    print("  - Footer with timestamp")

    # In practice, you would call:
    # content = report.generate()
    # output_path = report.save("custom_report")
    # print(f"\nReport saved to: {output_path}")

    print("\n" + "=" * 80)


def example_complete_workflow():
    """Example: Complete reporting workflow."""
    print("\n" + "=" * 80)
    print("Example 5: Complete Reporting Workflow")
    print("=" * 80)

    print("""
This example demonstrates a complete reporting workflow:

1. Load experimental results from data/results directory
2. Configure report settings (format, output, visualizations)
3. Generate findings report with statistical analysis
4. Perform paper comparison analysis
5. Export reports to multiple formats (JSON, Markdown, HTML, LaTeX)
6. Generate visualizations (if enabled)
7. Save all outputs to findings_showcase directory

The reporting package integrates with:
- experiments package (for result loading)
- evaluation package (for metrics calculation)
- visualization package (for figure generation)

See the documentation for full implementation details.
""")

    print("=" * 80)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("REPORTING PACKAGE EXAMPLES")
    print("=" * 80)

    # Run examples
    example_findings_report()
    example_paper_comparison()
    example_report_export()
    example_custom_report()
    example_complete_workflow()

    print("\nAll examples completed!")
    print("\nNote: File creation is commented out for demonstration.")
    print("Uncomment save operations for actual file generation.")
    print("\n" + "=" * 80)
