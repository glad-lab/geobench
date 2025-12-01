let us upload datasets to the github [Datasets](https://github.com/glad-lab/geobench/tree/main/Datasets), if it is really large, upload to [the google drive](https://drive.google.com/drive/folders/1zcMZWQGrDCNr6qI2sJ36KDQKnocEgZAp?usp=drive_link) instead.

## Paper Assignments

| Person   | Assigned Paper Title                          | Dataset Used                        | Unified Dataset | Metrics                        | Code | Results |
|----------|-----------------------------------------------|-------------------------------------| ------------------------------------- | -------------------------------------|-------------------------------------| ------------------------------------- |
| Andrew Yu    | [Rewrite-to-Rank](https://arxiv.org/abs/2507.21099) (**Only using Dataset and not Algorithm**) | [RewriteToRank](https://github.com/glad-lab/geobench/tree/main/Datasets/RewriteToRank) |[Data](https://github.com/glad-lab/geobench/blob/main/Datasets/GEO/unified_dataset.json)                  | ∆MRR(Change in ranking of ads), ∆DIR(Change in inclusion) | [Main Code](https://github.com/dan778912/ad-doc-reranker/tree/main) <br>[PPO Code](https://github.com/dan778912/adppolora/tree/main) | Raw Results, Summarized Results |
| Ojas Nimase | [Stealth Rank](https://arxiv.org/abs/2504.05804) | [main branch](https://github.com/glad-lab/geobench/tree/main/Datasets/StealthRank), [stealth rank branch](https://github.com/glad-lab/geobench/tree/Stealth-Rank/data2) | [Data](https://github.com/glad-lab/geobench/blob/Stealth-Rank/unified_dataset.json) | Rank, Perplexity (naturalness of text), Bad Word Ratio (proportion of prompts containing promotional keywords) | [Replicated Code](https://github.com/glad-lab/geobench/tree/Stealth-Rank), [Original Code](https://github.com/Tangyiming205069/controllable-seo/tree/main) | [Raw Results](https://github.com/glad-lab/geobench/tree/Stealth-Rank/results_new), [Summarized Results](https://github.com/glad-lab/geobench/blob/Stealth-Rank/results_summary.md) | 
| Gengpei Qi | [C-SEO Bench](https://arxiv.org/abs/2506.11097) | [C-SEO Bench](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) | [Data](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) | Rank Improvement， Area Under the Curve - AUC， Statistical Significance | [Main Code](https://github.com/parameterlab/c-seo-bench) <br> [Updated Code](https://github.com/gengpeiqi2001/2.0-cseo) | Raw Results, Summarized Results |
| Zhe Chen | [Manipulating LLMs to Increase Product Visibility](<https://arxiv.org/abs/2404.07981>) | Fictitious product catalogs (e.g., coffee machines, books, cameras)(details in [data folder](<https://github.com/glad-lab/geobench/tree/main/Datasets/llm-rank-optimizer>)) | | Rank Distribution | [Main Code](<https://github.com/aounon/llm-rank-optimizer>) [Updated Code](<https://github.com/KillerQueen-Z/llm-rank-optimizer>)| Raw Results, Summarized Results |
| Zhe Chen | [Large Language Models are Zero-Shot Rankers for Recommender Systems](https://arxiv.org/abs/2305.08845) (**Only using Dataset and not Algorithm**) | [LLMRank JSON Datasets](https://drive.google.com/drive/folders/1lw478Vt1IdlXz0Kzqrzr6NzUbfL093qU?usp=drive_link) | | NDCG@K (K=1,5,10,20) | [Code](https://github.com/RUCAIBox/LLMRank) | Raw Results, Summarized Results |
| Andrew Yu | [Adversarial Search Engine Optimization for Large Language Models](<https://arxiv.org/pdf/2406.18382>) | [Fictitious product data, combination of real and attack (e.g., books, photography, furniture)](https://github.com/glad-lab/geobench/tree/main/Datasets/AdversarialSEO) | | Rank Position, Attack Success Rate | [Code](https://github.com/freddysongg/Adversarial-SEO) | Raw Results, Summarized Results |
| Ojas Nimase | Are LLMs Reliable Rankers? Rank Manipulation via Two-Stage Token Optimization ([RAF](<https://arxiv.org/abs/2510.06732>)) | [main branch](https://github.com/glad-lab/geobench/tree/main/Datasets/StealthRank), [stealth rank branch](https://github.com/glad-lab/geobench/tree/Stealth-Rank/data2) | Same as Stealth Rank: [Data](https://github.com/glad-lab/geobench/blob/Stealth-Rank/unified_dataset.json) | Rank, Perplexity (naturalness of text), Bad Word Ratio (proportion of prompts containing promotional keywords) | [Original Code](https://github.com/glad-lab/RAF) | Raw Results, Summarized Results |
| Gengpei Qi | [Ranking Manipulation for Conversational Search Engines](https://arxiv.org/abs/2406.03589) | [Ragdoll](https://huggingface.co/datasets/Bai-YT/RAGDOLL) | [Data](https://drive.google.com/drive/folders/1pUsJw0AibGXnadS7VnxgOH-Y96AJG0ax) | Not sure yet | Main Code   Updated Code | Raw Results, Summarized Results |

## Dataset Metadata Table
| Dataset Name | Source Paper | Total Items | Number of Categories | Avg Items per Category | Categories | Domain/Field | Link |
|--------------|--------------|-------------|---------------------|------------------------|--------------|--------------|------|
| Ragroll | Stealth Rank | 399 | 50 | 7.98 | <details><summary>View all 50 categories</summary>air compressor, air purifier, automatic garden watering system, barbecue grill, beard trimmer, blender, coffee maker, computer monitor, computer power supply, cordless drill, curling iron, dishwasher, electric sander, electric toothbrush, eyeshadow, fascia gun, hair dryer, hair straightener, hammock, hedge trimmer, laptop, laser measure, lawn mower, leaf blower, lipstick, microwave oven, network attached storage, noise-canceling headphone, paint sprayer, pool cleaner, portable air conditioner, portable speaker, pressure washer, robot vacuum, screw driver, shampoo, skin cleansing brush, sleeping bag, slow cooker, smartphone, solid state drive, space heater, string trimmer, tablet, tent, tool chest, washing machine, wet-dry vacuum, wifi router, wood router</details> | Products | [Branch](https://github.com/glad-lab/geobench/tree/Stealth-Rank/data2/ragroll) |
| STSData | Stealth Rank | 30 | 3 | 10.00 | books, cameras, coffee_machines | Products | [Branch](https://github.com/glad-lab/geobench/tree/Stealth-Rank/data2/json) |
| | Rewrite-to-Rank |  |  |  |  | | [Data](https://github.com/glad-lab/geobench/tree/main/Datasets/RewriteToRank) |
| | C-SEO Bench |  |  |  |  | | [Data](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) |
| | Manipulating LLMs to Increase Product Visibility |  |  |  |  | | [Data](https://github.com/glad-lab/geobench/tree/main/Datasets/llm-rank-optimizer) |
| | Large Language Models are Zero-Shot Rankers for Recommender Systems |  |  |  |  | | [Data](https://drive.google.com/drive/folders/1lw478Vt1IdlXz0Kzqrzr6NzUbfL093qU?usp=drive_link) |
| | Adversarial Search Engine Optimization for LLMs |  |  |  |  | | [Data](https://github.com/glad-lab/geobench/tree/main/Datasets/AdversarialSEO) |

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
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
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
