#!/usr/bin/env python3
"""
Visualization module for adversarial SEO research.
Creates paper-style charts and graphs matching Nestaas et al. (2024).

Consolidated from visualizations.py and experiment_visualizations.py
Contains both class-based methods and standalone functions for compatibility.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

sns.set_style("whitegrid")
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10

class AdversarialSEOVisualizer:
    """Creates academic-style visualizations for adversarial SEO research."""
    
    def __init__(self, figsize=(12, 8), dpi=300):
        """
        Initialize visualizer with paper-style settings.
        
        Args:
            figsize: Default figure size
            dpi: Resolution for saved figures
        """
        self.figsize = figsize
        self.dpi = dpi
        
        self.colors = {
            'attack_success': '#E74C3C',
            'attack_failure': '#95A5A6',
            'baseline': '#3498DB',
            'improved': '#27AE60',
            'degraded': '#E67E22',
            'neutral': '#34495E'
        }
        
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 11,
            'figure.titlesize': 16
        })
    
    def plot_attack_effectiveness_summary(self, results: List[Dict], save_path: Optional[str] = None) -> plt.Figure:
        """
        Create attack effectiveness summary visualization.
        Replicates paper's attack success rate analysis.
        
        Args:
            results: List of experimental results
            save_path: Optional path to save figure
            
        Returns:
            matplotlib Figure object
        """
        queries = [r['query'] for r in results if 'error' not in r]
        retrieval_rates = [r['attack_docs_retrieved']/r['total_docs'] * 100 for r in results if 'error' not in r]
        
        effectiveness_rates = []
        for r in results:
            if 'error' not in r:
                rate = r['true_effectiveness']
                if rate > 1:
                    rate = min(rate / 100, 1.0)
                effectiveness_rates.append(rate * 100)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        x_pos = np.arange(len(queries))
        bars1 = ax1.bar(x_pos, retrieval_rates, color=self.colors['baseline'], alpha=0.7, 
                       label='Attack Documents Retrieved')
        
        ax1.set_xlabel('Test Queries')
        ax1.set_ylabel('Attack Document Retrieval Rate (%)')
        ax1.set_title('Attack Document Retrieval by Query Type')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels([f'Query {i+1}' for i in range(len(queries))], rotation=45)
        ax1.set_ylim(0, 100)
        
        for bar, rate in zip(bars1, retrieval_rates):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        bars2 = ax2.bar(x_pos, effectiveness_rates, 
                       color=[self.colors['attack_success'] if rate > 0 else self.colors['attack_failure'] 
                             for rate in effectiveness_rates],
                       alpha=0.8)
        
        ax2.set_xlabel('Test Queries')
        ax2.set_ylabel('Position 1 Success Rate (%)')
        ax2.set_title('Attack Effectiveness (Paper Methodology)\n(Position 1 Rankings Only)')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([f'Query {i+1}' for i in range(len(queries))], rotation=45)
        ax2.set_ylim(0, 100)
        
        for bar, rate in zip(bars2, effectiveness_rates):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        avg_effectiveness = np.mean(effectiveness_rates)
        ax2.axhline(y=avg_effectiveness, color=self.colors['neutral'], 
                   linestyle='--', alpha=0.7, label=f'Average: {avg_effectiveness:.1f}%')
        ax2.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Attack effectiveness summary saved to {save_path}")
        
        return fig
    
    def plot_attack_type_comparison(self, attack_data: Dict[str, List[float]], save_path: Optional[str] = None) -> plt.Figure:
        """
        Compare effectiveness of different attack types.
        Similar to paper's attack strategy analysis.
        
        Args:
            attack_data: Dict mapping attack types to success rates
            save_path: Optional path to save figure
            
        Returns:
            matplotlib Figure object
        """
        attack_types = list(attack_data.keys())
        
        success_rates = []
        error_bars = []
        
        for rates in attack_data.values():
            fixed_rates = []
            for rate in rates:
                if rate > 1:
                    fixed_rates.append(min(rate / 100, 1.0))
                else:
                    fixed_rates.append(rate)
            
            success_rates.append(np.mean(fixed_rates) * 100)
            error_bars.append(np.std(fixed_rates) * 100)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_pos = np.arange(len(attack_types))
        colors = [self.colors['attack_success'], self.colors['improved'], self.colors['degraded']][:len(attack_types)]
        bars = ax.bar(x_pos, success_rates, yerr=error_bars, capsize=5,
                     color=colors, alpha=0.8)
        
        ax.set_xlabel('Attack Type')
        ax.set_ylabel('Position 1 Success Rate (%)')
        ax.set_title('Attack Effectiveness by Type\n(Mean ± Standard Deviation)')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(attack_types)
        ax.set_ylim(0, 100)
        
        for bar, rate, error in zip(bars, success_rates, error_bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + error + 2,
                   f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Attack type comparison saved to {save_path}")
        
        return fig
    
    def plot_prisoners_dilemma(self, collective_performance: Dict[int, float], save_path: Optional[str] = None) -> plt.Figure:
        """
        Replicate Figure 5 from paper: Prisoner's Dilemma dynamics.
        Shows collective performance degradation with more attackers.
        
        Args:
            collective_performance: Dict mapping number of attackers to performance
            save_path: Optional path to save figure
            
        Returns:
            matplotlib Figure object
        """
        num_attackers = sorted(collective_performance.keys())
        performance = [collective_performance[n] for n in num_attackers]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        line = ax.plot(num_attackers, performance, 'o-', linewidth=3, markersize=8,
                      color=self.colors['degraded'], label='Collective Performance')
        
        ax.fill_between(num_attackers, performance, alpha=0.3, color=self.colors['degraded'])
        
        ax.set_xlabel('Number of Attackers')
        ax.set_ylabel('Collective Performance')
        ax.set_title('Prisoner\'s Dilemma: Collective Performance Degradation\n(Replication of Paper Figure 5)')
        ax.set_xticks(num_attackers)
        ax.grid(True, alpha=0.3)
        
        max_performance = max(performance)
        min_performance = min(performance)
        degradation = ((max_performance - min_performance) / max_performance) * 100
        
        ax.annotate(f'Performance Degradation: {degradation:.1f}%',
                   xy=(max(num_attackers), min_performance),
                   xytext=(max(num_attackers)-1, min_performance + 0.1),
                   arrowprops=dict(arrowstyle='->', color=self.colors['neutral']),
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        ax.legend()
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Prisoner's dilemma chart saved to {save_path}")
        
        return fig
    
    def plot_positional_bias(self, position_data: Dict[str, List[float]], save_path: Optional[str] = None) -> plt.Figure:
        """
        Replicate Figure 7 from paper: Attack effectiveness by position.
        
        Args:
            position_data: Dict mapping positions to success rates
            save_path: Optional path to save figure
            
        Returns:
            matplotlib Figure object
        """
        positions = list(position_data.keys())
        success_rates = [np.mean(rates) * 100 for rates in position_data.values()]
        error_bars = [np.std(rates) * 100 for rates in position_data.values()]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_pos = np.arange(len(positions))
        bars = ax.bar(x_pos, success_rates, yerr=error_bars, capsize=5,
                     color=[self.colors['baseline'], self.colors['improved'], self.colors['attack_success']],
                     alpha=0.8)
        
        ax.set_xlabel('Attack Position in Context')
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Attack Effectiveness by Position\n(Replication of Paper Figure 7)')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(positions)
        ax.set_ylim(0, max(success_rates) * 1.2)
        
        for bar, rate, error in zip(bars, success_rates, error_bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + error + 1,
                   f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        max_idx = success_rates.index(max(success_rates))
        bars[max_idx].set_edgecolor('black')
        bars[max_idx].set_linewidth(2)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Positional bias chart saved to {save_path}")
        
        return fig
    
    def plot_paper_comparison(self, paper_results: Dict, our_results: Dict, save_path: Optional[str] = None) -> plt.Figure:
        """
        Create side-by-side comparison with original paper results.
        
        Args:
            paper_results: Original paper findings
            our_results: Our experimental results
            save_path: Optional path to save figure
            
        Returns:
            matplotlib Figure object
        """
        metrics = list(paper_results.keys())
        paper_values = list(paper_results.values())
        our_values = list(our_results.values())
        
        x = np.arange(len(metrics))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        bars1 = ax.bar(x - width/2, paper_values, width, label='Nestaas et al. (2024)',
                      color=self.colors['baseline'], alpha=0.8)
        bars2 = ax.bar(x + width/2, our_values, width, label='Our RAG Study',
                      color=self.colors['attack_success'], alpha=0.8)
        
        ax.set_xlabel('Experimental Metrics')
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Replication Results: Paper vs. RAG Study')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        ax.legend()
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}%', ha='center', va='bottom')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Paper comparison chart saved to {save_path}")
        
        return fig
    
    def create_summary_dashboard(self, all_results: Dict, save_path: Optional[str] = None) -> plt.Figure:
        """
        Create comprehensive dashboard with all key visualizations.
        
        Args:
            all_results: Complete experimental results
            save_path: Optional path to save figure
            
        Returns:
            matplotlib Figure object
        """
        fig = plt.figure(figsize=(16, 12))
        
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        ax1 = fig.add_subplot(gs[0, 0])
        if 'attack_effectiveness' in all_results:
            data = all_results['attack_effectiveness']
            queries = list(range(len(data)))
            rates = [d['true_effectiveness'] * 100 for d in data]
            ax1.bar(queries, rates, color=self.colors['attack_success'], alpha=0.7)
            ax1.set_title('Attack Success Rates')
            ax1.set_ylabel('Success Rate (%)')
            ax1.set_xlabel('Query Number')
        
        ax2 = fig.add_subplot(gs[0, 1])
        if 'attack_types' in all_results:
            types = list(all_results['attack_types'].keys())
            rates = [np.mean(v) * 100 for v in all_results['attack_types'].values()]
            ax2.bar(types, rates, color=[self.colors['attack_success'], 
                                       self.colors['improved'], 
                                       self.colors['degraded']], alpha=0.7)
            ax2.set_title('Attack Type Effectiveness')
            ax2.set_ylabel('Success Rate (%)')
            ax2.tick_params(axis='x', rotation=45)
        
        ax3 = fig.add_subplot(gs[1, 0])
        if 'positional_bias' in all_results:
            positions = list(all_results['positional_bias'].keys())
            rates = [np.mean(v) * 100 for v in all_results['positional_bias'].values()]
            ax3.bar(positions, rates, color=self.colors['baseline'], alpha=0.7)
            ax3.set_title('Positional Bias Analysis')
            ax3.set_ylabel('Success Rate (%)')
        
        ax4 = fig.add_subplot(gs[1, 1])
        if 'paper_comparison' in all_results:
            comparison_data = all_results['paper_comparison']
            metrics = list(comparison_data.keys())
            paper_vals = [comparison_data[metric].get('paper', 0) for metric in metrics]
            our_vals = [comparison_data[metric].get('ours', 0) for metric in metrics]
            
            x = np.arange(len(metrics))
            width = 0.35
            ax4.bar(x - width/2, paper_vals, width, label='Paper', alpha=0.7)
            ax4.bar(x + width/2, our_vals, width, label='Our Study', alpha=0.7)
            ax4.set_title('Paper vs. Our Results')
            ax4.set_ylabel('Success Rate (%)')
            ax4.set_xticks(x)
            ax4.set_xticklabels(metrics, rotation=45)
            ax4.legend()
        else:
            ax4.text(0.5, 0.5, 'Paper comparison data not available\nRun prisoner\'s dilemma experiments', 
                    transform=ax4.transAxes, ha='center', va='center', fontsize=12)
            ax4.set_title('Paper vs. Our Results')
            ax4.set_xticks([])
            ax4.set_yticks([])
        
        fig.suptitle('Adversarial SEO Attack Analysis Dashboard', fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Summary dashboard saved to {save_path}")
        
        return fig


# ============================================================================
# STANDALONE FUNCTIONS (from experiment_visualizations.py)
# Used by notebooks - maintain backward compatibility
# ============================================================================

def plot_prisoners_dilemma(results: Dict[str, Any], figsize: Tuple[int, int] = (12, 5)) -> None:
    """
    Create prisoner's dilemma visualization matching paper's Figure 5.
    
    Args:
        results: Experiment results with 'by_num_attackers' metrics
        figsize: Figure size for the plot
    """
    by_attackers = results.get('by_num_attackers', {})
    if not by_attackers:
        print("No data to visualize")
        return
    
    num_attackers = sorted(by_attackers.keys())
    collective_perf = [by_attackers[n]['collective_performance'] for n in num_attackers]
    
    baseline = by_attackers[0]['collective_performance'] if 0 in by_attackers else 1.0
    individual_benefits = []
    for i, n in enumerate(num_attackers):
        if n > 0:
            individual_benefits.append(collective_perf[i] / n)
        else:
            individual_benefits.append(collective_perf[i])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    ax1.plot(num_attackers, collective_perf, 'o-', linewidth=2.5, markersize=8, 
             color='#2C3E50', label='Collective Performance')
    ax1.fill_between(num_attackers, collective_perf, alpha=0.2, color='#2C3E50')
    ax1.set_xlabel('Number of Attackers', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Collective Performance', fontsize=12, fontweight='bold')
    ax1.set_title("Prisoner's Dilemma: Race to the Bottom", fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1.1)
    ax1.set_xlim(-0.2, max(num_attackers) + 0.2)
    
    ax1.axhspan(0.8, 1.1, alpha=0.1, color='green', label='Cooperation Zone')
    ax1.axhspan(0.4, 0.8, alpha=0.1, color='yellow', label='Competition Zone')
    ax1.axhspan(0, 0.4, alpha=0.1, color='red', label='Destruction Zone')
    
    x_pos = np.arange(len(num_attackers))
    width = 0.35
    
    ax2.bar(x_pos - width/2, collective_perf, width, label='Collective Benefit', 
            color='#3498DB', alpha=0.8)
    ax2.bar(x_pos + width/2, individual_benefits, width, label='Individual Benefit', 
            color='#E74C3C', alpha=0.8)
    
    ax2.set_xlabel('Number of Attackers', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Performance Score', fontsize=12, fontweight='bold')
    ax2.set_title('Individual vs Collective Outcomes', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(num_attackers)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, 1.1)
    
    degradation = (baseline - collective_perf[-1]) / baseline * 100
    fig.suptitle(f'Total Degradation: {degradation:.1f}% (Paper: ~30%)', 
                 fontsize=12, y=1.02)
    
    plt.tight_layout()
    plt.show()
    
    print("\n📊 KEY FINDINGS:")
    print("="*50)
    print(f"Baseline (0 attackers): {baseline:.3f}")
    print(f"All attack ({max(num_attackers)} attackers): {collective_perf[-1]:.3f}")
    print(f"Degradation: {degradation:.1f}%")
    print(f"Paper's degradation: ~30%")
    print(f"Replication: {'✅ SUCCESS' if degradation > 20 else '⚠️ PARTIAL'}")


def plot_attack_effectiveness(results: List[Any], figsize: Tuple[int, int] = (14, 5)) -> None:
    """
    Create attack effectiveness visualization matching paper's style.
    
    Args:
        results: List of attack test results
        figsize: Figure size for the plot
    """
    if not results:
        print("No results to visualize")
        return
    
    queries = [r.query for r in results]
    attack_retrieved = [r.attack_docs_retrieved for r in results]
    attacks_in_ranking = [r.attacks_in_ranking for r in results]
    position_1_success = [r.position_1_success_rate for r in results]
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=figsize)
    
    x = np.arange(len(queries))
    ax1.bar(x, attack_retrieved, color='#16A085', alpha=0.7)
    ax1.set_xlabel('Query', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Attack Docs Retrieved', fontsize=11, fontweight='bold')
    ax1.set_title('Step 1: RAG Retrieval', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'Q{i+1}' for i in range(len(queries))], rotation=0)
    ax1.grid(True, alpha=0.3, axis='y')
    
    ax2.bar(x, attacks_in_ranking, color='#E67E22', alpha=0.7)
    ax2.set_xlabel('Query', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Attacks in Final Ranking', fontsize=11, fontweight='bold')
    ax2.set_title('Step 2: LLM Ranking', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'Q{i+1}' for i in range(len(queries))], rotation=0)
    ax2.grid(True, alpha=0.3, axis='y')
    
    ax3.bar(x, position_1_success, color='#C0392B', alpha=0.7)
    ax3.set_xlabel('Query', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Position 1 Success Rate', fontsize=11, fontweight='bold')
    ax3.set_title('Attack Success (Paper Metric)', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels([f'Q{i+1}' for i in range(len(queries))], rotation=0)
    ax3.set_ylim(0, 1.1)
    ax3.grid(True, alpha=0.3, axis='y')
    
    avg_success = np.mean(position_1_success)
    ax3.axhline(y=avg_success, color='red', linestyle='--', linewidth=2, 
                label=f'Average: {avg_success:.1%}')
    ax3.axhline(y=0.5, color='gray', linestyle=':', linewidth=1, 
                label='Paper: ~50%')
    ax3.legend()
    
    plt.suptitle('Attack Effectiveness Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()
    
    print("\n📊 ATTACK EFFECTIVENESS SUMMARY:")
    print("="*50)
    print(f"Average retrieval: {np.mean(attack_retrieved):.1f} docs")
    print(f"Average in ranking: {np.mean(attacks_in_ranking):.1f} attacks")
    print(f"Position 1 success: {avg_success:.1%}")
    print(f"Paper's success rate: ~50%")
    print(f"Replication: {'✅ SUCCESS' if avg_success > 0.3 else '⚠️ PARTIAL'}")


def plot_positional_bias(results: Dict[str, Any], figsize: Tuple[int, int] = (10, 6)) -> None:
    """
    Create positional bias visualization matching paper's Figure 7.
    
    Args:
        results: Experiment results with position-based metrics
        figsize: Figure size for the plot
    """
    position_data = {'start': [], 'middle': [], 'end': []}
    
    for trial in results.trials:
        position = trial.attack_info.get('position', 'unknown')
        success = trial.metrics.get('success', 0)
        if position in position_data:
            position_data[position].append(success)
    
    if not any(position_data.values()):
        print("No positional data to visualize")
        return
    
    positions = ['start', 'middle', 'end']
    success_rates = [np.mean(position_data[p]) if position_data[p] else 0 for p in positions]
    std_errors = [np.std(position_data[p])/np.sqrt(len(position_data[p])) 
                  if position_data[p] else 0 for p in positions]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    colors = ['#3498DB', '#2ECC71', '#E74C3C']
    bars = ax.bar(positions, success_rates, yerr=std_errors, 
                   color=colors, alpha=0.8, capsize=10, width=0.6)
    
    ax.set_xlabel('Attack Position in Document', fontsize=12, fontweight='bold')
    ax.set_ylabel('Attack Success Rate', fontsize=12, fontweight='bold')
    ax.set_title('Positional Bias in Attack Effectiveness (Figure 7 Replication)', 
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.0)
    ax.grid(True, alpha=0.3, axis='y')
    
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{rate:.1%}', ha='center', va='bottom', fontweight='bold')
    
    # Add reference line for paper's findings
    if success_rates[2] > 0 and success_rates[0] > 0:
        relative_end = success_rates[2] / success_rates[0] if success_rates[0] > 0 else 1
        ax.text(0.5, 0.9, f'End position effectiveness: {relative_end:.1f}x (Paper: ~1.5x)',
                transform=ax.transAxes, ha='center', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.show()
    
    print("\n📊 POSITIONAL BIAS SUMMARY:")
    print("="*50)
    for pos, rate in zip(positions, success_rates):
        print(f"{pos.capitalize()} position: {rate:.1%}")
    if success_rates[2] > 0 and success_rates[0] > 0:
        print(f"End vs Start effectiveness: {success_rates[2]/success_rates[0]:.1f}x")
        print(f"Paper's ratio: ~1.5x")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_attack_visualization_from_results(results: List[Dict], save_dir: str = "../data/results/") -> Dict[str, str]:
    """
    Create all visualizations from experimental results.
    
    Args:
        results: List of experimental results
        save_dir: Directory to save figures
        
    Returns:
        Dict mapping visualization types to file paths
    """
    visualizer = AdversarialSEOVisualizer()
    saved_files = {}
    
    try:
        fig1 = visualizer.plot_attack_effectiveness_summary(results)
        path1 = f"{save_dir}/attack_effectiveness_summary.png"
        fig1.savefig(path1, dpi=300, bbox_inches='tight')
        saved_files['effectiveness_summary'] = path1
        plt.close(fig1)
        
        attack_types = {}
        for result in results:
            if 'attack_type' in result:
                attack_type = result['attack_type']
                if attack_type not in attack_types:
                    attack_types[attack_type] = []
                attack_types[attack_type].append(result['true_effectiveness'])
        
        if attack_types:
            fig2 = visualizer.plot_attack_type_comparison(attack_types)
            path2 = f"{save_dir}/attack_type_comparison.png"
            fig2.savefig(path2, dpi=300, bbox_inches='tight')
            saved_files['type_comparison'] = path2
            plt.close(fig2)
        
        logger.info(f"Visualizations created and saved to {save_dir}")
        return saved_files
        
    except Exception as e:
        logger.error(f"Error creating visualizations: {e}")
        return {}


if __name__ == "__main__":
    print("🎨 Adversarial SEO Visualization Module")
    print("📊 Creates paper-style charts for research analysis")
    print("⚠️  Demo mode: Using sample data for illustration")
    
    sample_results = [
        {'query': 'demo_query_1', 'attack_docs_retrieved': 1, 'total_docs': 5, 'true_effectiveness': 0.8},
        {'query': 'demo_query_2', 'attack_docs_retrieved': 0, 'total_docs': 5, 'true_effectiveness': 0.0},
        {'query': 'demo_query_3', 'attack_docs_retrieved': 2, 'total_docs': 5, 'true_effectiveness': 0.5},
    ]
    
    print("🔬 For real experiments, use create_attack_visualization_from_results() with actual results")
    
    visualizer = AdversarialSEOVisualizer()
    fig = visualizer.plot_attack_effectiveness_summary(sample_results)
    plt.show()