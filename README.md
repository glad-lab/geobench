let us upload datasets to the github [Datasets](https://github.com/glad-lab/geobench/tree/main/Datasets), if it is really large, upload to [the google drive](https://drive.google.com/drive/folders/1zcMZWQGrDCNr6qI2sJ36KDQKnocEgZAp?usp=drive_link) instead.

## Paper Assignments

| Person   | Assigned Paper Title                          | Dataset Used                        | Unified Dataset | Metrics                        | Code | Results |
|----------|-----------------------------------------------|-------------------------------------| ------------------------------------- | -------------------------------------|-------------------------------------| ------------------------------------- |
| Andrew Yu    | [Rewrite-to-Rank](https://arxiv.org/abs/2507.21099) | [RewriteToRank](https://github.com/glad-lab/geobench/tree/main/Datasets/RewriteToRank) |[Data](https://github.com/glad-lab/geobench/blob/main/Datasets/GEO/unified_dataset.json)                  | ∆MRR(Change in ranking of ads), ∆DIR(Change in inclusion) | [Main Code](https://github.com/dan778912/ad-doc-reranker/tree/main) <br>[PPO Code](https://github.com/dan778912/adppolora/tree/main) | Raw Results, Summarized Results |
| Ojas Nimase | [Stealth Rank](https://arxiv.org/abs/2504.05804) | [main branch](https://github.com/glad-lab/geobench/tree/main/Datasets/StealthRank), [stealth rank branch](https://github.com/glad-lab/geobench/tree/Stealth-Rank/data2) | [Data](https://github.com/glad-lab/geobench/blob/Stealth-Rank/unified_dataset.json) | Rank, Perplexity (naturalness of text), Bad Word Ratio (proportion of prompts containing promotional keywords) | [Replicated Code](https://github.com/glad-lab/geobench/tree/Stealth-Rank), [Original Code](https://github.com/Tangyiming205069/controllable-seo/tree/main) | [Raw Results](https://github.com/glad-lab/geobench/tree/Stealth-Rank/results_new), [Summarized Results](https://github.com/glad-lab/geobench/blob/Stealth-Rank/results_summary.md) | 
| Gengpei Qi | [C-SEO Bench](https://arxiv.org/abs/2506.11097) | [C-SEO Bench](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) | [Data](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) | Rank Improvement， Area Under the Curve - AUC， Statistical Significance | [Main Code](https://github.com/parameterlab/c-seo-bench) <br> [Updated Code](https://github.com/gengpeiqi2001/2.0-cseo) | Raw Results, Summarized Results |
| Zhe Chen    | [Manipulating LLMs to Increase Product Visibility](<https://arxiv.org/abs/2404.07981>) | Fictitious product catalogs (e.g., coffee machines, books, cameras)(details in [data folder](<https://github.com/glad-lab/geobench/tree/main/Datasets/llm-rank-optimizer>)) | | Rank Distribution | [Main Code](<https://github.com/aounon/llm-rank-optimizer>) [Updated Code](<https://github.com/KillerQueen-Z/llm-rank-optimizer>)| Raw Results, Summarized Results |
| xuzhizhang | [Large Language Models are Zero-Shot Rankers for Recommender Systems](https://arxiv.org/abs/2305.08845) | [LLMRank JSON Datasets](https://drive.google.com/drive/folders/1lw478Vt1IdlXz0Kzqrzr6NzUbfL093qU?usp=drive_link) | | NDCG@K (K=1,5,10,20) | [Code](https://github.com/RUCAIBox/LLMRank) | Raw Results, Summarized Results |
| Freddy Song | [Adversarial Search Engine Optimization for Large Language Models](<https://arxiv.org/pdf/2406.18382>) | [Fictitious product data, combination of real and attack (e.g., books, photography, furniture)](https://github.com/glad-lab/geobench/tree/main/Datasets/AdversarialSEO) | | Rank Position, Attack Success Rate | [Code](https://github.com/freddysongg/Adversarial-SEO) | Raw Results, Summarized Results |
|  | [RAF](<https://arxiv.org/abs/2510.06732>) | same with Stealth Rank |  | [Original Code](https://github.com/glad-lab/RAF) | |

## Experiments
<table border="1">
  <thead>
    <tr>
      <th style="width: 15%;">Paper</th>
      <th style="width: 25%;">Test Datasets</th>
      <th style="width: 60%;">Results</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="5">Rewrite-to-Rank</td>
      <td>Stealth Rank</td>
      <td rowspan="5"></td>
    </tr>
    <tr>
      <td>C-SEO Bench</td>
    </tr>
    <tr>
      <td>Manipulating LLMs to Increase Product Visibility</td>
    </tr>
    <tr>
      <td>Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
    </tr>
    <tr>
      <td>Adversarial Engine Optimization for LLMs</td>
    </tr>
    <tr>
      <td rowspan="5">Stealth Rank</td>
      <td>C-SEO Bench</td>
      <td rowspan="5"></td>
    </tr>
    <tr>
      <td>Manipulating LLMs to Increase Product Visibility</td>
    </tr>
    <tr>
      <td>Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
    </tr>
    <tr>
      <td>Adversarial Engine Optimization for LLMs</td>
    </tr>
    <tr>
      <td><a href="https://github.com/glad-lab/geobench/tree/Stealth-Rank/benchmark_data/rewrite_to_rank">Rewrite-to-Rank</a></td>
    </tr>
    <tr>
      <td rowspan="5">C-SEO Bench</td>
      <td>Stealth Rank</td>
      <td rowspan="5"></td>
    </tr>
    <tr>
      <td>Manipulating LLMs to Increase Product Visibility</td>
    </tr>
    <tr>
      <td>Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
    </tr>
    <tr>
      <td>Adversarial Engine Optimization for LLMs</td>
    </tr>
    <tr>
      <td>Rewrite-to-Rank</td>
    </tr>
    <tr>
      <td rowspan="5">Manipulating LLMs to Increase Product Visibility</td>
      <td>Stealth Rank</td>
      <td rowspan="5"></td>
    </tr>
    <tr>
      <td>C-SEO Bench</td>
    </tr>
    <tr>
      <td>Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
    </tr>
    <tr>
      <td>Adversarial Engine Optimization for LLMs</td>
    </tr>
    <tr>
      <td>Rewrite-to-Rank</td>
    </tr>
    <tr>
      <td rowspan="5">Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
      <td>Stealth Rank</td>
      <td rowspan="5"></td>
    </tr>
    <tr>
      <td>C-SEO Bench</td>
    </tr>
    <tr>
      <td>Manipulating LLMs to Increase Product Visibility</td>
    </tr>
    <tr>
      <td>Adversarial Engine Optimization for LLMs</td>
    </tr>
    <tr>
      <td>Rewrite-to-Rank</td>
    </tr>
    <tr>
      <td rowspan="5">Adversarial Engine Optimization for LLMs</td>
      <td>Stealth Rank</td>
      <td rowspan="5"></td>
    </tr>
    <tr>
      <td>C-SEO Bench</td>
    </tr>
    <tr>
      <td>Manipulating LLMs to Increase Product Visibility</td>
    </tr>
    <tr>
      <td>Large Language Models are Zero-Shot Rankers for Recommender Systems</td>
    </tr>
    <tr>
      <td>Rewrite-to-Rank</td>
    </tr>
  </tbody>
</table>
