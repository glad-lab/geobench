"""
Results analysis module for adversarial SEO research.
Compares results with Nestaas et al., 2024 paper findings.
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
import logging

logger = logging.getLogger(__name__)


@dataclass 
class PaperFindings:
    """Expected findings from Nestaas et al., 2024."""
    
    single_attack_success_rate: float = 0.25
    camera_recommendation_increase: float = 2.5
    collective_degradation_all_attack: float = 0.45
    external_attack_success: float = 0.25
    end_position_effectiveness: float = 1.3
    gpt35_success: float = 0.30
    gpt4_success: float = 0.25
    claude_success: float = 0.20


class ResultsAnalysis:
    """
    Analyzes experimental results and compares with paper findings.
    Generates visualizations and statistical comparisons.
    """
    
    def __init__(
        self,
        output_dir: str = "data/results",
        paper_findings: Optional[PaperFindings] = None
    ):
        """
        Initialize the results analyzer.
        
        Args:
            output_dir: Directory containing result files
            paper_findings: Expected findings from the paper
        """
        self.output_dir = Path(output_dir)
        self.paper_findings = paper_findings or PaperFindings()

        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
    
    def load_results(self, experiment_type: str) -> List[Dict]:
        """
        Load all results for a specific experiment type.
        
        Args:
            experiment_type: Type of experiment to load
            
        Returns:
            List of experiment results
        """
        results = []
        
        for file_path in self.output_dir.glob(f"{experiment_type}_*.json"):
            with open(file_path, "r") as f:
                data = json.load(f)
                results.append(data)
        
        logger.info(f"Loaded {len(results)} result files for {experiment_type}")
        return results
    
    def analyze_single_attack(
        self,
        results: List[Dict],
        save_plots: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze single attack experiment results.
        
        Args:
            results: List of experiment results
            save_plots: Whether to save visualization plots
            
        Returns:
            Analysis summary
        """
        analysis = {
            "experiment_type": "single_attack",
            "num_experiments": len(results),
            "total_trials": 0,
            "metrics": {}
        }
        
        all_success_rates = []
        all_position_changes = []
        attack_type_success = {}
        
        for exp in results:
            for trial in exp.get("trials", []):
                metrics = trial.get("metrics", {})
                
                if "success" in metrics:
                    all_success_rates.append(metrics["success"])
                
                if "position_change" in metrics:
                    all_position_changes.append(metrics["position_change"])
                
                attack_info = trial.get("attack_info", {})
                attack_type = attack_info.get("attack_type", "unknown")
                
                if attack_type not in attack_type_success:
                    attack_type_success[attack_type] = []
                
                attack_type_success[attack_type].append(metrics.get("success", 0))
                analysis["total_trials"] += 1
        
        if all_success_rates:
            analysis["metrics"]["overall_success_rate"] = np.mean(all_success_rates)
            analysis["metrics"]["success_rate_std"] = np.std(all_success_rates)
            analysis["metrics"]["success_rate_ci"] = stats.t.interval(
                0.95,
                len(all_success_rates) - 1,
                loc=np.mean(all_success_rates),
                scale=stats.sem(all_success_rates)
            )
        
        if all_position_changes:
            analysis["metrics"]["mean_position_change"] = np.mean(all_position_changes)
            analysis["metrics"]["position_change_std"] = np.std(all_position_changes)
        
        analysis["by_attack_type"] = {}
        for attack_type, successes in attack_type_success.items():
            analysis["by_attack_type"][attack_type] = {
                "success_rate": np.mean(successes),
                "num_trials": len(successes)
            }
        
        analysis["paper_comparison"] = self._compare_with_paper(
            "single_attack",
            analysis["metrics"]
        )
        
        if save_plots:
            self._plot_single_attack_results(analysis)
        
        return analysis
    
    def analyze_prisoners_dilemma(
        self,
        results: List[Dict],
        save_plots: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze prisoner's dilemma experiment results.
        
        Args:
            results: List of experiment results
            save_plots: Whether to save visualization plots
            
        Returns:
            Analysis summary
        """
        analysis = {
            "experiment_type": "prisoners_dilemma",
            "num_experiments": len(results),
            "total_trials": 0,
            "by_num_attackers": {}
        }
        
        attacker_groups = {}
        
        for exp in results:
            for trial in exp.get("trials", []):
                attack_info = trial.get("attack_info", {})
                num_attackers = attack_info.get("num_attackers", 0)
                
                if num_attackers not in attacker_groups:
                    attacker_groups[num_attackers] = {
                        "collective_performance": [],
                        "avg_improvement": []
                    }
                
                metrics = trial.get("metrics", {})
                if "collective_performance" in metrics:
                    attacker_groups[num_attackers]["collective_performance"].append(
                        metrics["collective_performance"]
                    )
                
                if "avg_attacker_improvement" in metrics:
                    attacker_groups[num_attackers]["avg_improvement"].append(
                        metrics["avg_attacker_improvement"]
                    )
                
                analysis["total_trials"] += 1
        
        for num_attackers, data in attacker_groups.items():
            analysis["by_num_attackers"][num_attackers] = {
                "mean_collective_performance": np.mean(data["collective_performance"]) if data["collective_performance"] else 0,
                "std_collective_performance": np.std(data["collective_performance"]) if data["collective_performance"] else 0,
                "mean_improvement": np.mean(data["avg_improvement"]) if data["avg_improvement"] else 0,
                "num_trials": len(data["collective_performance"])
            }
        
        if 0 in analysis["by_num_attackers"] and 4 in analysis["by_num_attackers"]:
            baseline_perf = analysis["by_num_attackers"][0]["mean_collective_performance"]
            all_attack_perf = analysis["by_num_attackers"][4]["mean_collective_performance"]
            
            if baseline_perf > 0:
                analysis["collective_degradation"] = 1 - (all_attack_perf / baseline_perf)
            else:
                analysis["collective_degradation"] = 0
        
        analysis["paper_comparison"] = self._compare_with_paper(
            "prisoners_dilemma",
            {"collective_degradation": analysis.get("collective_degradation", 0)}
        )
        
        if save_plots:
            self._plot_prisoners_dilemma_results(analysis)
        
        return analysis
    
    def analyze_positional_bias(
        self,
        results: List[Dict],
        save_plots: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze positional bias experiment results.
        
        Args:
            results: List of experiment results
            save_plots: Whether to save visualization plots
            
        Returns:
            Analysis summary
        """
        analysis = {
            "experiment_type": "positional_bias",
            "num_experiments": len(results),
            "total_trials": 0,
            "by_position": {}
        }
        
        position_groups = {}
        
        for exp in results:
            for trial in exp.get("trials", []):
                attack_info = trial.get("attack_info", {})
                position = attack_info.get("position", "unknown")
                
                if position not in position_groups:
                    position_groups[position] = {
                        "success": [],
                        "position_change": []
                    }
                
                metrics = trial.get("metrics", {})
                if "success" in metrics:
                    position_groups[position]["success"].append(metrics["success"])
                
                if "position_change" in metrics:
                    position_groups[position]["position_change"].append(metrics["position_change"])
                
                analysis["total_trials"] += 1
        
        for position, data in position_groups.items():
            analysis["by_position"][position] = {
                "success_rate": np.mean(data["success"]) if data["success"] else 0,
                "success_rate_std": np.std(data["success"]) if data["success"] else 0,
                "mean_position_change": np.mean(data["position_change"]) if data["position_change"] else 0,
                "num_trials": len(data["success"])
            }
        
        if "start" in analysis["by_position"] and "end" in analysis["by_position"]:
            start_success = analysis["by_position"]["start"]["success_rate"]
            end_success = analysis["by_position"]["end"]["success_rate"]
            
            if start_success > 0:
                analysis["end_relative_effectiveness"] = end_success / start_success
            else:
                analysis["end_relative_effectiveness"] = 0
        
        if len(position_groups) > 1:
            position_data = [data["success"] for data in position_groups.values()]
            if all(len(d) > 0 for d in position_data):
                f_stat, p_value = stats.f_oneway(*position_data)
                analysis["position_effect_test"] = {
                    "f_statistic": f_stat,
                    "p_value": p_value,
                    "significant": p_value < 0.05
                }
        
        analysis["paper_comparison"] = self._compare_with_paper(
            "positional_bias",
            {"end_relative_effectiveness": analysis.get("end_relative_effectiveness", 0)}
        )
        
        if save_plots:
            self._plot_positional_bias_results(analysis)
        
        return analysis
    
    def generate_comprehensive_report(
        self,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis report for all experiments.
        
        Args:
            save_path: Optional path to save the report
            
        Returns:
            Comprehensive analysis report
        """
        report = {
            "title": "Adversarial SEO for LLMs - Reproduction Study Results",
            "timestamp": pd.Timestamp.now().isoformat(),
            "experiments": {}
        }
        
        experiment_types = [
            "baseline",
            "single_attack",
            "prisoners_dilemma",
            "external_attack",
            "positional_bias"
        ]
        
        for exp_type in experiment_types:
            results = self.load_results(exp_type)
            
            if results:
                if exp_type == "single_attack":
                    analysis = self.analyze_single_attack(results)
                elif exp_type == "prisoners_dilemma":
                    analysis = self.analyze_prisoners_dilemma(results)
                elif exp_type == "positional_bias":
                    analysis = self.analyze_positional_bias(results)
                else:
                    analysis = self._generic_analysis(results, exp_type)
                
                report["experiments"][exp_type] = analysis
        
        report["replication_summary"] = self._assess_replication_success(report["experiments"])
        
        if save_path:
            with open(save_path, "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Comprehensive report saved to {save_path}")
        
        return report
    
    def _compare_with_paper(
        self,
        experiment_type: str,
        our_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Compare our results with paper findings."""
        comparison = {}
        
        if experiment_type == "single_attack":
            if "overall_success_rate" in our_metrics:
                paper_value = self.paper_findings.single_attack_success_rate
                our_value = our_metrics["overall_success_rate"]
                
                comparison["success_rate"] = {
                    "our_value": our_value,
                    "paper_value": paper_value,
                    "difference": our_value - paper_value,
                    "relative_difference": (our_value - paper_value) / paper_value if paper_value > 0 else 0
                }
        
        elif experiment_type == "prisoners_dilemma":
            if "collective_degradation" in our_metrics:
                paper_value = self.paper_findings.collective_degradation_all_attack
                our_value = our_metrics["collective_degradation"]
                
                comparison["collective_degradation"] = {
                    "our_value": our_value,
                    "paper_value": paper_value,
                    "difference": our_value - paper_value,
                    "relative_difference": (our_value - paper_value) / paper_value if paper_value > 0 else 0
                }
        
        elif experiment_type == "positional_bias":
            if "end_relative_effectiveness" in our_metrics:
                paper_value = self.paper_findings.end_position_effectiveness
                our_value = our_metrics["end_relative_effectiveness"]
                
                comparison["end_effectiveness"] = {
                    "our_value": our_value,
                    "paper_value": paper_value,
                    "difference": our_value - paper_value,
                    "relative_difference": (our_value - paper_value) / paper_value if paper_value > 0 else 0
                }
        
        return comparison
    
    def _plot_single_attack_results(self, analysis: Dict):
        """Generate plots for single attack results."""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        if "by_attack_type" in analysis:
            attack_types = list(analysis["by_attack_type"].keys())
            success_rates = [analysis["by_attack_type"][at]["success_rate"] for at in attack_types]
            
            axes[0].bar(attack_types, success_rates)
            axes[0].set_xlabel("Attack Type")
            axes[0].set_ylabel("Success Rate")
            axes[0].set_title("Attack Success Rate by Type")
            axes[0].set_ylim([0, 1])
            
            axes[0].axhline(
                y=self.paper_findings.single_attack_success_rate,
                color='r',
                linestyle='--',
                label='Paper Result'
            )
            axes[0].legend()
        
        axes[1].hist(
            [0, 1],
            bins=20,
            edgecolor='black'
        )
        axes[1].set_xlabel("Success Rate")
        axes[1].set_ylabel("Frequency")
        axes[1].set_title("Distribution of Attack Success")
        
        plt.suptitle("Single Attack Experiment Results")
        plt.tight_layout()
        plt.savefig(self.output_dir / "single_attack_analysis.png")
        plt.close()
    
    def _plot_prisoners_dilemma_results(self, analysis: Dict):
        """Generate plots for prisoner's dilemma results."""
        if "by_num_attackers" not in analysis:
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        num_attackers = sorted(analysis["by_num_attackers"].keys())
        collective_perf = [
            analysis["by_num_attackers"][n]["mean_collective_performance"]
            for n in num_attackers
        ]
        avg_improvement = [
            analysis["by_num_attackers"][n]["mean_improvement"]
            for n in num_attackers
        ]
        
        axes[0].plot(num_attackers, collective_perf, 'o-', linewidth=2, markersize=8)
        axes[0].set_xlabel("Number of Attackers")
        axes[0].set_ylabel("Collective Performance")
        axes[0].set_title("Prisoner's Dilemma: Collective Performance")
        axes[0].grid(True, alpha=0.3)
        
        axes[1].bar(num_attackers, avg_improvement)
        axes[1].set_xlabel("Number of Attackers")
        axes[1].set_ylabel("Average Position Improvement")
        axes[1].set_title("Individual Benefit vs Competition")
        
        plt.suptitle("Prisoner's Dilemma Experiment Results")
        plt.tight_layout()
        plt.savefig(self.output_dir / "prisoners_dilemma_analysis.png")
        plt.close()
    
    def _plot_positional_bias_results(self, analysis: Dict):
        """Generate plots for positional bias results."""
        if "by_position" not in analysis:
            return
        
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        positions = list(analysis["by_position"].keys())
        success_rates = [
            analysis["by_position"][pos]["success_rate"]
            for pos in positions
        ]
        
        bars = ax.bar(positions, success_rates)
        ax.set_xlabel("Attack Position")
        ax.set_ylabel("Success Rate")
        ax.set_title("Attack Effectiveness by Position in Context")
        ax.set_ylim([0, max(success_rates) * 1.2 if success_rates else 1])
        
        if all("success_rate_std" in analysis["by_position"][pos] for pos in positions):
            errors = [analysis["by_position"][pos]["success_rate_std"] for pos in positions]
            ax.errorbar(
                positions,
                success_rates,
                yerr=errors,
                fmt='none',
                color='black',
                capsize=5
            )
        
        max_rate = max(success_rates) if success_rates else 1
        for bar, rate in zip(bars, success_rates):
            bar.set_color(plt.cm.RdYlGn(rate / max_rate))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "positional_bias_analysis.png")
        plt.close()
    
    def _generic_analysis(
        self,
        results: List[Dict],
        experiment_type: str
    ) -> Dict[str, Any]:
        """Generic analysis for experiment types without specific methods."""
        analysis = {
            "experiment_type": experiment_type,
            "num_experiments": len(results),
            "total_trials": sum(len(exp.get("trials", [])) for exp in results)
        }
        
        return analysis
    
    def _assess_replication_success(
        self,
        experiments: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """Assess overall replication success."""
        summary = {
            "findings_replicated": [],
            "findings_not_replicated": [],
            "overall_success_rate": 0
        }
        
        findings_checks = []
        
        if "single_attack" in experiments:
            comparison = experiments["single_attack"].get("paper_comparison", {})
            if "success_rate" in comparison:
                relative_diff = abs(comparison["success_rate"]["relative_difference"])
                if relative_diff < 0.5:
                    summary["findings_replicated"].append("Single attack effectiveness")
                    findings_checks.append(True)
                else:
                    summary["findings_not_replicated"].append("Single attack effectiveness")
                    findings_checks.append(False)
        
        if "prisoners_dilemma" in experiments:
            comparison = experiments["prisoners_dilemma"].get("paper_comparison", {})
            if "collective_degradation" in comparison:
                relative_diff = abs(comparison["collective_degradation"]["relative_difference"])
                if relative_diff < 0.5:
                    summary["findings_replicated"].append("Prisoner's dilemma dynamic")
                    findings_checks.append(True)
                else:
                    summary["findings_not_replicated"].append("Prisoner's dilemma dynamic")
                    findings_checks.append(False)
        
        if "positional_bias" in experiments:
            comparison = experiments["positional_bias"].get("paper_comparison", {})
            if "end_effectiveness" in comparison:
                relative_diff = abs(comparison["end_effectiveness"]["relative_difference"])
                if relative_diff < 0.5:
                    summary["findings_replicated"].append("Positional bias effect")
                    findings_checks.append(True)
                else:
                    summary["findings_not_replicated"].append("Positional bias effect")
                    findings_checks.append(False)
        
        if findings_checks:
            summary["overall_success_rate"] = sum(findings_checks) / len(findings_checks)
        
        return summary