"""
Test result reporters.

Provides reporting and visualization of test results.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from .provider_tests import ProviderTestResult


@dataclass
class TestReport:
    """Test report summary."""

    # Report metadata
    report_name: str
    timestamp: str
    duration: float

    # Test summary
    total_tests: int
    successful_tests: int
    failed_tests: int
    success_rate: float

    # Provider analysis
    provider_results: Dict[str, Any]
    attack_type_results: Dict[str, Any]

    # Statistical metrics
    avg_response_time: float
    total_tokens_used: int
    total_cost_estimate: float

    # Detailed results
    results: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return asdict(self)


class TestReporter:
    """Reporter for test results."""

    def __init__(self, output_dir: str = "data/results/testing"):
        """
        Initialize test reporter.

        Args:
            output_dir: Directory for saving reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        results: List[ProviderTestResult],
        report_name: str = "test_report",
        duration: float = 0.0
    ) -> TestReport:
        """
        Generate test report from results.

        Args:
            results: List of test results
            report_name: Name for the report
            duration: Total test duration in seconds

        Returns:
            TestReport object
        """
        if not results:
            return self._create_empty_report(report_name)

        # Calculate summary statistics
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.attack_successful)
        failed_tests = total_tests - successful_tests
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0

        # Analyze by provider
        provider_results = self._analyze_by_provider(results)

        # Analyze by attack type
        attack_type_results = self._analyze_by_attack_type(results)

        # Calculate performance metrics
        avg_response_time = sum(r.response_time for r in results) / len(results)
        total_tokens = sum(r.tokens_used for r in results)

        # Estimate cost (simplified)
        total_cost = self._estimate_cost(results)

        # Create report
        report = TestReport(
            report_name=report_name,
            timestamp=datetime.now().isoformat(),
            duration=duration,
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            provider_results=provider_results,
            attack_type_results=attack_type_results,
            avg_response_time=avg_response_time,
            total_tokens_used=total_tokens,
            total_cost_estimate=total_cost,
            results=[asdict(r) for r in results]
        )

        return report

    def _create_empty_report(self, report_name: str) -> TestReport:
        """Create an empty report."""
        return TestReport(
            report_name=report_name,
            timestamp=datetime.now().isoformat(),
            duration=0.0,
            total_tests=0,
            successful_tests=0,
            failed_tests=0,
            success_rate=0.0,
            provider_results={},
            attack_type_results={},
            avg_response_time=0.0,
            total_tokens_used=0,
            total_cost_estimate=0.0,
            results=[]
        )

    def _analyze_by_provider(self, results: List[ProviderTestResult]) -> Dict[str, Any]:
        """Analyze results grouped by provider."""
        provider_analysis = {}

        providers = set(r.provider for r in results)
        for provider in providers:
            provider_results = [r for r in results if r.provider == provider]

            if provider_results:
                successful = sum(1 for r in provider_results if r.attack_successful)
                provider_analysis[provider] = {
                    "total_tests": len(provider_results),
                    "successful": successful,
                    "success_rate": successful / len(provider_results),
                    "avg_response_time": sum(r.response_time for r in provider_results) / len(provider_results),
                    "avg_position_change": sum(r.position_change for r in provider_results) / len(provider_results),
                    "error_rate": sum(1 for r in provider_results if r.error_occurred) / len(provider_results),
                }

        return provider_analysis

    def _analyze_by_attack_type(self, results: List[ProviderTestResult]) -> Dict[str, Any]:
        """Analyze results grouped by attack type."""
        attack_analysis = {}

        attack_types = set(r.attack_type for r in results)
        for attack_type in attack_types:
            type_results = [r for r in results if r.attack_type == attack_type]

            if type_results:
                successful = sum(1 for r in type_results if r.attack_successful)
                attack_analysis[attack_type] = {
                    "total_tests": len(type_results),
                    "successful": successful,
                    "success_rate": successful / len(type_results),
                    "avg_position_change": sum(r.position_change for r in type_results) / len(type_results),
                }

        return attack_analysis

    def _estimate_cost(self, results: List[ProviderTestResult]) -> float:
        """Estimate total cost based on token usage."""
        # Simplified cost estimation
        cost_per_1k_tokens = {
            "openai": 0.002,
            "anthropic": 0.001,
            "bedrock": 0.0015,
        }

        total_cost = 0.0
        for result in results:
            provider_cost = cost_per_1k_tokens.get(result.provider, 0.001)
            total_cost += (result.tokens_used / 1000) * provider_cost

        return total_cost

    def save_report(self, report: TestReport, format: str = "json") -> Path:
        """
        Save report to file.

        Args:
            report: Report to save
            format: Output format (json, markdown, html)

        Returns:
            Path to saved report
        """
        if format == "json":
            return self._save_json_report(report)
        elif format == "markdown":
            return self._save_markdown_report(report)
        elif format == "html":
            return self._save_html_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _save_json_report(self, report: TestReport) -> Path:
        """Save report as JSON."""
        filename = f"{report.report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = self.output_dir / filename

        with open(output_path, "w") as f:
            json.dump(report.to_dict(), f, indent=2, default=str)

        return output_path

    def _save_markdown_report(self, report: TestReport) -> Path:
        """Save report as Markdown."""
        filename = f"{report.report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        output_path = self.output_dir / filename

        markdown_content = self._generate_markdown_content(report)

        with open(output_path, "w") as f:
            f.write(markdown_content)

        return output_path

    def _generate_markdown_content(self, report: TestReport) -> str:
        """Generate Markdown report content."""
        provider_rows = []
        for provider, data in report.provider_results.items():
            provider_rows.append(
                f"| {provider} | {data['total_tests']} | {data['successful']} | "
                f"{data['success_rate']:.2%} | {data['avg_response_time']:.2f}s |"
            )
        provider_table = "\n".join(provider_rows)

        attack_rows = []
        for attack_type, data in report.attack_type_results.items():
            attack_rows.append(
                f"| {attack_type} | {data['total_tests']} | {data['successful']} | "
                f"{data['success_rate']:.2%} | {data['avg_position_change']:.2f} |"
            )
        attack_table = "\n".join(attack_rows)

        content = f"""# Test Report: {report.report_name}

## Summary

- **Timestamp**: {report.timestamp}
- **Duration**: {report.duration:.2f} seconds
- **Total Tests**: {report.total_tests}
- **Successful**: {report.successful_tests}
- **Failed**: {report.failed_tests}
- **Success Rate**: {report.success_rate:.2%}

## Performance Metrics

- **Average Response Time**: {report.avg_response_time:.2f}s
- **Total Tokens Used**: {report.total_tokens_used:,}
- **Estimated Cost**: ${report.total_cost_estimate:.4f}

## Results by Provider

| Provider | Total Tests | Successful | Success Rate | Avg Response Time |
|----------|-------------|------------|--------------|-------------------|
{provider_table}

## Results by Attack Type

| Attack Type | Total Tests | Successful | Success Rate | Avg Position Change |
|-------------|-------------|------------|--------------|---------------------|
{attack_table}

---

*Report generated on {report.timestamp}*
"""
        return content

    def _save_html_report(self, report: TestReport) -> Path:
        """Save report as HTML."""
        filename = f"{report.report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        output_path = self.output_dir / filename

        html_content = self._generate_html_content(report)

        with open(output_path, "w") as f:
            f.write(html_content)

        return output_path

    def _generate_html_content(self, report: TestReport) -> str:
        """Generate HTML report content."""
        # Simplified HTML template
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Report: {report.report_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .metric {{ background-color: #f2f2f2; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>Test Report: {report.report_name}</h1>

    <div class="metric">
        <h2>Summary</h2>
        <p><strong>Timestamp:</strong> {report.timestamp}</p>
        <p><strong>Duration:</strong> {report.duration:.2f} seconds</p>
        <p><strong>Total Tests:</strong> {report.total_tests}</p>
        <p><strong>Successful:</strong> {report.successful_tests}</p>
        <p><strong>Failed:</strong> {report.failed_tests}</p>
        <p><strong>Success Rate:</strong> {report.success_rate:.2%}</p>
    </div>

    <div class="metric">
        <h2>Performance Metrics</h2>
        <p><strong>Average Response Time:</strong> {report.avg_response_time:.2f}s</p>
        <p><strong>Total Tokens Used:</strong> {report.total_tokens_used:,}</p>
        <p><strong>Estimated Cost:</strong> ${report.total_cost_estimate:.4f}</p>
    </div>

    <h2>Results by Provider</h2>
    <table>
        <tr>
            <th>Provider</th>
            <th>Total Tests</th>
            <th>Successful</th>
            <th>Success Rate</th>
            <th>Avg Response Time</th>
        </tr>
"""

        for provider, data in report.provider_results.items():
            html += f"""        <tr>
            <td>{provider}</td>
            <td>{data['total_tests']}</td>
            <td>{data['successful']}</td>
            <td>{data['success_rate']:.2%}</td>
            <td>{data['avg_response_time']:.2f}s</td>
        </tr>
"""

        html += """    </table>

    <h2>Results by Attack Type</h2>
    <table>
        <tr>
            <th>Attack Type</th>
            <th>Total Tests</th>
            <th>Successful</th>
            <th>Success Rate</th>
            <th>Avg Position Change</th>
        </tr>
"""

        for attack_type, data in report.attack_type_results.items():
            html += f"""        <tr>
            <td>{attack_type}</td>
            <td>{data['total_tests']}</td>
            <td>{data['successful']}</td>
            <td>{data['success_rate']:.2%}</td>
            <td>{data['avg_position_change']:.2f}</td>
        </tr>
"""

        html += f"""    </table>

    <footer>
        <p><em>Report generated on {report.timestamp}</em></p>
    </footer>
</body>
</html>
"""
        return html

    def print_summary(self, report: TestReport) -> None:
        """Print report summary to console."""
        print(f"\n{'='*80}")
        print(f"Test Report: {report.report_name}")
        print(f"{'='*80}")
        print(f"\nSummary:")
        print(f"  Total Tests: {report.total_tests}")
        print(f"  Successful: {report.successful_tests}")
        print(f"  Failed: {report.failed_tests}")
        print(f"  Success Rate: {report.success_rate:.2%}")
        print(f"  Duration: {report.duration:.2f}s")
        print(f"\nPerformance:")
        print(f"  Avg Response Time: {report.avg_response_time:.2f}s")
        print(f"  Total Tokens: {report.total_tokens_used:,}")
        print(f"  Estimated Cost: ${report.total_cost_estimate:.4f}")
        print(f"\n{'-'*80}")
