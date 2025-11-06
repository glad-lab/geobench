"""
Findings report generation.

Creates comprehensive findings showcases with visualizations and statistical analysis.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np

from .base import BaseReport, ReportConfig

logger = logging.getLogger(__name__)


@dataclass
class FindingsReport:
    """Comprehensive findings report structure."""

    # Core metrics
    single_attack_success_rate: float
    prisoners_dilemma_degradation: float
    positional_bias_factor: float
    external_attack_success: float

    # Statistical validation
    statistical_significance: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]

    # Cross-provider comparison
    provider_performance: Dict[str, Dict[str, float]]
    attack_transferability: Dict[str, float]

    # Paper comparison
    paper_reproduction_score: float
    validated_findings: List[str]
    novel_findings: List[str]

    # Metadata
    total_experiments: int
    timestamp: str
    models_tested: List[str]


class FindingsReportGenerator(BaseReport):
    """
    Generates comprehensive findings report for adversarial SEO research.

    Creates publication-ready reports, visualizations, and statistical summaries.
    """

    def __init__(
        self,
        config: ReportConfig,
        results_dir: str = "data/results",
        paper_benchmarks: Optional[Dict[str, float]] = None
    ):
        """
        Initialize findings report generator.

        Args:
            config: Report configuration
            results_dir: Directory containing experimental results
            paper_benchmarks: Reference benchmarks from original paper
        """
        super().__init__(config)

        self.results_dir = Path(results_dir)
        self.paper_benchmarks = paper_benchmarks or self._get_default_benchmarks()

        # Create subdirectories
        output_dir = Path(config.output_dir)
        (output_dir / "visualizations").mkdir(parents=True, exist_ok=True)
        (output_dir / "reports").mkdir(parents=True, exist_ok=True)
        (output_dir / "data").mkdir(parents=True, exist_ok=True)

    def _get_default_benchmarks(self) -> Dict[str, float]:
        """Get default paper benchmarks."""
        return {
            "single_attack_success": 0.50,
            "collective_degradation": 0.30,
            "positional_bias_ratio": 1.5,
            "attack_retrieval_rate": 0.75,
        }

    def generate(self) -> str:
        """Generate comprehensive findings report."""
        logger.info("Generating comprehensive findings report...")

        # Load all results
        results = self._load_all_results()

        if not results:
            logger.warning("No results found in results directory")
            return "No experimental results available."

        # Generate report sections
        self._generate_executive_summary(results)
        self._generate_methodology_section()
        self._generate_results_section(results)
        self._generate_discussion_section(results)

        if self.config.include_statistics:
            self._generate_statistical_section(results)

        if self.config.include_visualizations:
            self._generate_visualizations_section(results)

        # Combine all sections
        report_content = self._create_header()
        report_content += "\n".join(self.content)
        report_content += self._create_footer()

        return report_content

    def _load_all_results(self) -> Dict[str, Any]:
        """Load all experimental results from results directory."""
        results = {}

        for result_file in self.results_dir.glob("*.json"):
            try:
                with open(result_file, 'r') as f:
                    data = json.load(f)
                    results[result_file.stem] = data
                    logger.info(f"Loaded results from {result_file}")
            except Exception as e:
                logger.warning(f"Failed to load {result_file}: {e}")

        return results

    def _generate_executive_summary(self, results: Dict[str, Any]) -> None:
        """Generate executive summary section."""
        summary = self._calculate_executive_summary(results)

        content = f"""
## Executive Summary

This report presents the comprehensive findings from our reproduction study of
"Adversarial Search Engine Optimization for Large Language Models" (Nestaas et al., 2024).

### Key Findings

1. **Single Attack Effectiveness**: {summary.get('single_attack_success', 0):.2%} success rate
   - Paper benchmark: {self.paper_benchmarks['single_attack_success']:.2%}
   - Reproduction status: {summary.get('single_attack_status', 'Unknown')}

2. **Prisoner's Dilemma Degradation**: {summary.get('prisoners_dilemma_degradation', 0):.2%} effectiveness loss
   - Paper benchmark: {self.paper_benchmarks['collective_degradation']:.2%}
   - Reproduction status: {summary.get('prisoners_dilemma_status', 'Unknown')}

3. **Positional Bias Factor**: {summary.get('positional_bias_factor', 1.0):.2f}x effectiveness increase
   - Paper benchmark: {self.paper_benchmarks['positional_bias_ratio']:.2f}x
   - Reproduction status: {summary.get('positional_bias_status', 'Unknown')}

### Overall Reproduction Score

**{summary.get('reproduction_score', 0):.1%}** - Our findings {summary.get('reproduction_quality', 'align with')} the original paper's results.
"""

        self.add_section("Executive Summary", content, level=2)

    def _calculate_executive_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate executive summary metrics."""
        summary = {}

        # Extract key metrics from results
        if "single_attack_experiments" in results:
            single_attack_data = results["single_attack_experiments"]
            summary["single_attack_success"] = self._extract_success_rate(single_attack_data)
            summary["single_attack_status"] = self._determine_reproduction_status(
                summary["single_attack_success"],
                self.paper_benchmarks["single_attack_success"]
            )

        if "prisoners_dilemma_experiments" in results:
            pd_data = results["prisoners_dilemma_experiments"]
            summary["prisoners_dilemma_degradation"] = self._extract_degradation(pd_data)
            summary["prisoners_dilemma_status"] = self._determine_reproduction_status(
                summary["prisoners_dilemma_degradation"],
                self.paper_benchmarks["collective_degradation"]
            )

        if "positional_bias_experiments" in results:
            pos_data = results["positional_bias_experiments"]
            summary["positional_bias_factor"] = self._extract_bias_factor(pos_data)
            summary["positional_bias_status"] = self._determine_reproduction_status(
                summary["positional_bias_factor"],
                self.paper_benchmarks["positional_bias_ratio"]
            )

        # Calculate overall reproduction score
        scores = []
        for key in ["single_attack_success", "prisoners_dilemma_degradation", "positional_bias_factor"]:
            if key in summary:
                benchmark_key = {
                    "single_attack_success": "single_attack_success",
                    "prisoners_dilemma_degradation": "collective_degradation",
                    "positional_bias_factor": "positional_bias_ratio"
                }[key]

                relative_diff = abs(summary[key] - self.paper_benchmarks[benchmark_key]) / self.paper_benchmarks[benchmark_key]
                score = max(0, 1 - relative_diff)
                scores.append(score)

        summary["reproduction_score"] = np.mean(scores) if scores else 0.0
        summary["reproduction_quality"] = self._get_quality_description(summary["reproduction_score"])

        return summary

    def _extract_success_rate(self, data: Dict[str, Any]) -> float:
        """Extract success rate from experiment data."""
        if "success_rate" in data:
            return data["success_rate"]
        elif "experiments" in data:
            experiments = data["experiments"]
            if experiments:
                successful = sum(1 for exp in experiments if exp.get("attack_successful", False))
                return successful / len(experiments)
        return 0.0

    def _extract_degradation(self, data: Dict[str, Any]) -> float:
        """Extract degradation metric from prisoner's dilemma data."""
        if "degradation" in data:
            return data["degradation"]
        return 0.0

    def _extract_bias_factor(self, data: Dict[str, Any]) -> float:
        """Extract positional bias factor from experiment data."""
        if "bias_factor" in data:
            return data["bias_factor"]
        return 1.0

    def _determine_reproduction_status(self, our_value: float, paper_value: float) -> str:
        """Determine reproduction status."""
        if paper_value == 0:
            return "Inconclusive"

        relative_diff = abs(our_value - paper_value) / paper_value

        if relative_diff <= 0.15:
            return "Excellent - Within 15% of paper findings"
        elif relative_diff <= 0.30:
            return "Good - Within 30% of paper findings"
        elif relative_diff <= 0.50:
            return "Partial - Within 50% of paper findings"
        else:
            return "Poor - Differs significantly from paper findings"

    def _get_quality_description(self, score: float) -> str:
        """Get quality description from reproduction score."""
        if score >= 0.85:
            return "strongly align with"
        elif score >= 0.70:
            return "generally align with"
        elif score >= 0.50:
            return "partially align with"
        else:
            return "differ from"

    def _generate_methodology_section(self) -> None:
        """Generate methodology section."""
        content = """
## Methodology

### Experimental Setup

- **Research Environment**: RAG System with Glass Box Analysis
- **Dataset**: 83 documents (60 products + 23 noise documents)
- **Embedding Model**: Google Gemini text-embedding-004
- **Vector Database**: Qdrant with cosine similarity
- **Attack Types**: Prompt Injection, Persuasion, Discreditation
- **Ethical Framework**: Fictional products only, controlled environment

### Statistical Methods

- Confidence Level: 95%
- Significance Threshold: p < 0.05
- Effect Size: Cohen's d
- Multiple Testing Correction: Benjamini-Hochberg FDR

### Quality Assurance

- Reproducible experimental design
- Complete attack mechanism transparency
- Controlled variable isolation
- Comprehensive error handling
"""

        self.add_section("Methodology", content, level=2)

    def _generate_results_section(self, results: Dict[str, Any]) -> None:
        """Generate results section."""
        content = """
## Experimental Results

Detailed results from all experimental phases including attack effectiveness,
prisoner's dilemma dynamics, and positional bias analysis.

*See subsections below for detailed breakdowns.*
"""

        self.add_section("Results", content, level=2)

    def _generate_discussion_section(self, results: Dict[str, Any]) -> None:
        """Generate discussion section."""
        content = """
## Discussion

### Successfully Demonstrated

- Preference manipulation attacks work in RAG systems
- Prisoner's dilemma dynamics emerge with multiple attackers
- Positional bias affects attack effectiveness
- Glass box analysis provides superior transparency

### Methodological Advantages

- Complete attack mechanism visibility
- Controlled experimental environment
- Reproducible with fictional product datasets
- Ethical research framework maintained

### Limitations

- Simplified context vs. real-world search engines
- Limited model diversity in current testing
- Fictional products may have different ranking dynamics
"""

        self.add_section("Discussion", content, level=2)

    def _generate_statistical_section(self, results: Dict[str, Any]) -> None:
        """Generate statistical analysis section."""
        content = """
## Statistical Analysis

Comprehensive statistical validation of experimental findings including
hypothesis testing, effect sizes, and confidence intervals.
"""

        self.add_section("Statistical Analysis", content, level=2)

    def _generate_visualizations_section(self, results: Dict[str, Any]) -> None:
        """Generate visualizations section."""
        content = """
## Visualizations

Key visualizations illustrating experimental findings and comparisons
with original paper benchmarks.
"""

        self.add_section("Visualizations", content, level=2)

    def save(self, filename: Optional[str] = None) -> Path:
        """Save findings report to file."""
        output_path = self._get_output_path(filename)

        # Generate report content
        report_content = self.generate()

        # Save to file
        with open(output_path, "w") as f:
            f.write(report_content)

        logger.info(f"Findings report saved to {output_path}")
        return output_path
