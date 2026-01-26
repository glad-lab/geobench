#!/usr/bin/env python3
"""
收集 results_datasets_5 中所有 eval.json 的结果，生成统计表格
"""
import json
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

def load_eval_json(eval_path: str) -> dict:
    """加载 eval.json 文件"""
    try:
        with open(eval_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 无法加载 {eval_path}: {e}")
        return None

def calculate_metrics(eval_data: dict) -> dict:
    """从 eval.json 计算关键指标"""
    if not eval_data:
        return None
    
    metrics = {}
    
    # 基础排名和优化后排名
    rank_list = eval_data.get('rank_list', [])
    rank_list_opt = eval_data.get('rank_list_opt', [])
    
    if not rank_list or not rank_list_opt:
        return None
    
    # 计算平均排名
    metrics['avg_rank_base'] = sum(rank_list) / len(rank_list)
    metrics['avg_rank_opt'] = sum(rank_list_opt) / len(rank_list_opt)
    metrics['avg_rank_improvement'] = metrics['avg_rank_base'] - metrics['avg_rank_opt']  # 正数表示提升
    
    # 计算排名提升率（rank_improvement / rank_base）
    if metrics['avg_rank_base'] > 0:
        metrics['rank_improvement_rate'] = metrics['avg_rank_improvement'] / metrics['avg_rank_base'] * 100
    else:
        metrics['rank_improvement_rate'] = 0.0
    
    # 从 advantage 计算提升/不变/下降的比例
    advantage = eval_data.get('advantage', {})
    metrics['improved_pct'] = advantage.get('1', 0.0)  # 提升的比例
    metrics['unchanged_pct'] = advantage.get('0', 0.0)  # 不变的比例
    metrics['degraded_pct'] = advantage.get('-1', 0.0)  # 下降的比例
    
    # 从 advantage_cleaned 计算（清理后的数据）
    advantage_cleaned = eval_data.get('advantage_cleaned', {})
    metrics['improved_pct_cleaned'] = advantage_cleaned.get('1', 0.0)
    metrics['unchanged_pct_cleaned'] = advantage_cleaned.get('0', 0.0)
    metrics['degraded_pct_cleaned'] = advantage_cleaned.get('-1', 0.0)
    
    # 计算 Top-1, Top-3, Top-5 命中率（优化后）
    rank_dist_opt = eval_data.get('rank_dist_opt', {})
    metrics['hits_at_1'] = rank_dist_opt.get('1', 0.0)
    metrics['hits_at_3'] = sum([rank_dist_opt.get(str(i), 0.0) for i in range(1, 4)])
    metrics['hits_at_5'] = sum([rank_dist_opt.get(str(i), 0.0) for i in range(1, 6)])
    
    # 基础版本的命中率
    rank_dist = eval_data.get('rank_dist', {})
    metrics['hits_at_1_base'] = rank_dist.get('1', 0.0)
    metrics['hits_at_3_base'] = sum([rank_dist.get(str(i), 0.0) for i in range(1, 4)])
    metrics['hits_at_5_base'] = sum([rank_dist.get(str(i), 0.0) for i in range(1, 6)])
    
    return metrics

def collect_all_results(results_dir: str = "results_datasets_5") -> Dict[str, List[dict]]:
    """收集所有算法的评估结果"""
    results = defaultdict(list)
    
    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"❌ 结果目录不存在: {results_dir}")
        return results
    
    # 遍历所有 eval.json 文件
    for eval_file in results_path.rglob("eval.json"):
        # 解析路径: results_datasets_5/{algorithm}/{category}/self/llama/default/product{idx}/run{run}/eval.json
        parts = eval_file.parts
        try:
            # 找到 algorithm 的位置（在 results_datasets_5 之后）
            if 'results_datasets_5' in parts or results_dir in parts:
                idx = parts.index(results_dir) if results_dir in parts else parts.index('results_datasets_5')
                if idx + 1 < len(parts):
                    algorithm = parts[idx + 1]
                    category = parts[idx + 2] if idx + 2 < len(parts) else "unknown"
                    product_idx = None
                    for part in parts:
                        if part.startswith('product'):
                            product_idx = part.replace('product', '')
                            break
                    
                    eval_data = load_eval_json(str(eval_file))
                    if eval_data:
                        metrics = calculate_metrics(eval_data)
                        if metrics:
                            metrics['algorithm'] = algorithm
                            metrics['category'] = category
                            metrics['product_idx'] = product_idx
                            metrics['eval_path'] = str(eval_file)
                            results[algorithm].append(metrics)
        except Exception as e:
            print(f"⚠️ 解析路径失败 {eval_file}: {e}")
            continue
    
    return results

def calculate_algorithm_stats(results: List[dict]) -> dict:
    """计算每个算法的平均统计信息"""
    if not results:
        return None
    
    stats = {
        'num_experiments': len(results),
        'avg_rank_base': sum(r['avg_rank_base'] for r in results) / len(results),
        'avg_rank_opt': sum(r['avg_rank_opt'] for r in results) / len(results),
        'avg_rank_improvement': sum(r['avg_rank_improvement'] for r in results) / len(results),
        'avg_rank_improvement_rate': sum(r['rank_improvement_rate'] for r in results) / len(results),
        'avg_improved_pct': sum(r['improved_pct'] for r in results) / len(results),
        'avg_unchanged_pct': sum(r['unchanged_pct'] for r in results) / len(results),
        'avg_degraded_pct': sum(r['degraded_pct'] for r in results) / len(results),
        'avg_improved_pct_cleaned': sum(r['improved_pct_cleaned'] for r in results) / len(results),
        'avg_hits_at_1': sum(r['hits_at_1'] for r in results) / len(results),
        'avg_hits_at_3': sum(r['hits_at_3'] for r in results) / len(results),
        'avg_hits_at_5': sum(r['hits_at_5'] for r in results) / len(results),
        'avg_hits_at_1_base': sum(r['hits_at_1_base'] for r in results) / len(results),
        'avg_hits_at_3_base': sum(r['hits_at_3_base'] for r in results) / len(results),
        'avg_hits_at_5_base': sum(r['hits_at_5_base'] for r in results) / len(results),
    }
    
    return stats

def generate_markdown_table(all_results: Dict[str, List[dict]]) -> str:
    """生成 Markdown 表格"""
    table_lines = []
    
    # 表头
    table_lines.append("## Results Summary (datasets_5)")
    table_lines.append("")
    table_lines.append("| Algorithm | # Experiments | Avg Rank (Base) | Avg Rank (Opt) | Rank Improvement | Improvement Rate (%) | Improved (%) | Unchanged (%) | Degraded (%) | Hits@1 (Opt) | Hits@3 (Opt) | Hits@5 (Opt) |")
    table_lines.append("|-----------|---------------|----------------|----------------|------------------|---------------------|--------------|---------------|--------------|--------------|--------------|--------------|")
    
    # 按算法名称排序
    for algorithm in sorted(all_results.keys()):
        stats = calculate_algorithm_stats(all_results[algorithm])
        if stats:
            table_lines.append(
                f"| {algorithm} | "
                f"{stats['num_experiments']} | "
                f"{stats['avg_rank_base']:.2f} | "
                f"{stats['avg_rank_opt']:.2f} | "
                f"{stats['avg_rank_improvement']:.2f} | "
                f"{stats['avg_rank_improvement_rate']:.2f}% | "
                f"{stats['avg_improved_pct']:.2f}% | "
                f"{stats['avg_unchanged_pct']:.2f}% | "
                f"{stats['avg_degraded_pct']:.2f}% | "
                f"{stats['avg_hits_at_1']:.2f}% | "
                f"{stats['avg_hits_at_3']:.2f}% | "
                f"{stats['avg_hits_at_5']:.2f}% |"
            )
    
    table_lines.append("")
    table_lines.append("### 指标说明")
    table_lines.append("- **Avg Rank (Base)**: 优化前的平均排名（越小越好）")
    table_lines.append("- **Avg Rank (Opt)**: 优化后的平均排名（越小越好）")
    table_lines.append("- **Rank Improvement**: 排名提升 = Base - Opt（正数表示提升）")
    table_lines.append("- **Improvement Rate (%)**: 排名提升率 = (Base - Opt) / Base × 100%")
    table_lines.append("- **Improved (%)**: 排名提升的样本比例")
    table_lines.append("- **Unchanged (%)**: 排名不变的样本比例")
    table_lines.append("- **Degraded (%)**: 排名下降的样本比例")
    table_lines.append("- **Hits@K (Opt)**: 优化后排名在前 K 位的样本比例")
    table_lines.append("")
    
    return "\n".join(table_lines)

def main():
    print("开始收集评估结果...")
    all_results = collect_all_results()
    
    if not all_results:
        print("❌ 未找到任何评估结果")
        return
    
    print(f"\n找到 {len(all_results)} 个算法的结果:")
    for algorithm, results in all_results.items():
        print(f"  - {algorithm}: {len(results)} 个实验")
    
    # 生成表格
    table = generate_markdown_table(all_results)
    
    # 保存到文件
    output_file = "EVAL_RESULTS_SUMMARY.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(table)
    
    print(f"\n✅ 统计表格已保存到: {output_file}")
    print("\n" + "="*80)
    print(table)
    print("="*80)

if __name__ == "__main__":
    main()

