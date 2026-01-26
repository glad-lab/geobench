## Local Documentation Index

For experiment documentation, please refer to:

- **中文说明**：`README_CN.md`  
- **English summary**：`README_EN.md`
- If different categories have different numbers of products, you get a different number of
  StealthRank runs per category, making results harder to compare and aggregate.
- By giving every category the same (>1) number of products, you can sweep `target_product_idx`
  over the same range in all categories (e.g., `1..8`), obtaining a consistent number of
  StealthRank runs and CSV outputs per category.

## Experiments
<table border="1" style="width: 100%; table-layout: fixed;">
  <thead>
    <tr>
      <th rowspan="2">Paper</th>
      <th rowspan="2">Test Datasets</th>
      <th colspan="6">Results</th>
    </tr>
    <tr>
      <th>Original Description</th>
      <th>Original Ranking</th>
      <th>New Description</th>
      <th>New Ranking</th>
      <th>Metrics (Hits@X, Perplexity)</th>
      <th>Rank Improvement</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="5">Rewrite-to-Rank</td>
      <td>Stealth Rank</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>C-SEO Bench</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Manipulating LLMs to Increase Product Visibility</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Adversarial Engine Optimization for LLMs</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td rowspan="5">Stealth Rank</td>
      <td>C-SEO Bench</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Manipulating LLMs to Increase Product Visibility</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Adversarial Engine Optimization for LLMs</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td><a href="https://github.com/glad-lab/geobench/tree/Stealth-Rank/benchmark_data/rewrite_to_rank">Rewrite-to-Rank</a></td>
      <td>N/A</td>
      <td>N/A</td>
      <td>N/A</td>
      <td>7.37 (avg)</td>
      <td>Rank: 7.37, Perplexity: 75.05, Bad Word: 0.17</td>
      <td>N/A</td>
    </tr>
    <tr>
      <td rowspan="5">C-SEO Bench</td>
      <td>Stealth Rank</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Manipulating LLMs to Increase Product Visibility</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Adversarial Engine Optimization for LLMs</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Rewrite-to-Rank</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td rowspan="5">Manipulating LLMs to Increase Product Visibility</td>
      <td>Stealth Rank</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>C-SEO Bench</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Adversarial Engine Optimization for LLMs</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Rewrite-to-Rank</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td rowspan="5">Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
      <td>Stealth Rank</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>C-SEO Bench</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Manipulating LLMs to Increase Product Visibility</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Adversarial Engine Optimization for LLMs</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Rewrite-to-Rank</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td rowspan="5">Adversarial Engine Optimization for LLMs</td>
      <td>Stealth Rank</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>C-SEO Bench</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Manipulating LLMs to Increase Product Visibility</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Rewrite-to-Rank</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </tbody>
</table>

## Evaluation Results Summary (datasets_5)

基于 `results_datasets_5` 目录中所有评估结果的统计汇总：

| Algorithm | # Experiments | Avg Rank (Base) | Avg Rank (Opt) | Rank Improvement | Improvement Rate (%) | Improved (%) | Unchanged (%) | Degraded (%) | Hits@1 (Opt) | Hits@3 (Opt) | Hits@5 (Opt) |
|-----------|---------------|----------------|----------------|------------------|---------------------|--------------|---------------|--------------|--------------|--------------|--------------|
| AdversarialSEO | 2 | 5.59 | 5.66 | -0.07 | -1.05% | 10.75% | 73.50% | 15.75% | 13.50% | 23.25% | 27.25% |
| GEO | 1 | 5.17 | 5.12 | 0.05 | 0.97% | 18.50% | 63.50% | 18.00% | 13.00% | 27.00% | 44.50% |
| StealthRank | 21 | 4.31 | 3.79 | 0.52 | 11.02% | 33.07% | 47.90% | 19.02% | 28.81% | 50.21% | 69.05% |
| Zero-Shot Rankers | 2 | 3.70 | 3.40 | 0.31 | 7.69% | 25.75% | 51.25% | 23.00% | 23.00% | 58.75% | 77.75% |
| llm-rank-optimizer | 6 | 6.12 | 6.57 | -0.45 | -11.93% | 18.75% | 46.83% | 34.42% | 15.25% | 21.25% | 25.25% |

### 指标说明

- **Avg Rank (Base)**: 优化前的平均排名（越小越好）
- **Avg Rank (Opt)**: 优化后的平均排名（越小越好）
- **Rank Improvement**: 排名提升 = Base - Opt（正数表示提升）
- **Improvement Rate (%)**: 排名提升率 = (Base - Opt) / Base × 100%
- **Improved (%)**: 排名提升的样本比例
- **Unchanged (%)**: 排名不变的样本比例
- **Degraded (%)**: 排名下降的样本比例
- **Hits@K (Opt)**: 优化后排名在前 K 位的样本比例

### 主要发现

- **StealthRank** 表现最佳：平均排名提升 0.52（11.02%），33.07% 的样本排名提升，Hits@1 达到 28.81%
- **Zero-Shot Rankers** 次之：平均排名提升 0.31（7.69%），Hits@5 达到 77.75%
- **llm-rank-optimizer** 表现较差：平均排名下降 0.45（-11.93%），34.42% 的样本排名下降

> 注：此统计表格可通过运行 `python3 collect_eval_results.py` 自动更新。
