let us upload datasets to the github [Datasets](https://github.com/glad-lab/geobench/tree/main/Datasets), if it is really large, upload to [the google drive](https://drive.google.com/drive/folders/1zcMZWQGrDCNr6qI2sJ36KDQKnocEgZAp?usp=drive_link) instead.

## Paper Assignments

| Person   | Assigned Paper Title                    | Paper Objective (Product Ranking, Content Recommendation, etc)      | Dataset Used                        | Unified Dataset | Metrics                        | Code | Results |
|----------|---------------------------------------| --------|-------------------------------------| ------------------------------------- | -------------------------------------|-------------------------------------| ------------------------------------- |
| Andrew Yu    | [Rewrite-to-Rank](https://arxiv.org/abs/2507.21099) (**Only using Dataset and not Algorithm**) | | [RewriteToRank](https://github.com/glad-lab/geobench/tree/main/Datasets/RewriteToRank) |[Data](https://github.com/glad-lab/geobench/blob/main/Datasets/GEO/unified_dataset.json)                  | ∆MRR(Change in ranking of ads), ∆DIR(Change in inclusion) | [Main Code](https://github.com/dan778912/ad-doc-reranker/tree/main) <br>[PPO Code](https://github.com/dan778912/adppolora/tree/main) | Raw Results, Summarized Results |
| Ojas Nimase | [Stealth Rank](https://arxiv.org/abs/2504.05804) | Product rankings mainly | [main branch](https://github.com/glad-lab/geobench/tree/main/Datasets/StealthRank), [stealth rank branch](https://github.com/glad-lab/geobench/tree/Stealth-Rank/data2) | [Data](https://github.com/glad-lab/geobench/blob/Stealth-Rank/unified_dataset.json) | Rank, Perplexity (naturalness of text), Bad Word Ratio (proportion of prompts containing promotional keywords) | [Replicated Code](https://github.com/glad-lab/geobench/tree/Stealth-Rank), [Original Code](https://github.com/Tangyiming205069/controllable-seo/tree/main) | [Raw Results](https://github.com/glad-lab/geobench/tree/Stealth-Rank/results_new), [Summarized Results](https://github.com/glad-lab/geobench/blob/Stealth-Rank/results_summary.md) | 
| Gengpei Qi | [C-SEO Bench Does Conversational SEO Work](https://arxiv.org/abs/2506.11097) | | [C-SEO Bench](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) | [Data](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) | Rank Improvement， Area Under the Curve - AUC， Statistical Significance | [Main Code](https://github.com/parameterlab/c-seo-bench) <br> [Updated Code](https://github.com/gengpeiqi2001/2.0-cseo) | Raw Results, Summarized Results |
| Zhe Chen | [Manipulating LLMs to Increase Product Visibility](https://arxiv.org/abs/2404.07981) | | Fictitious product catalogs (e.g., coffee machines, books, cameras)(details in [data folder](<https://github.com/glad-lab/geobench/tree/main/Datasets/llm-rank-optimizer>)) | [Data](https://github.com/glad-lab/geobench/blob/main/Datasets/llm-rank-optimizer/data/unified_dataset.json) | Rank Distribution | [Main Code](<https://github.com/aounon/llm-rank-optimizer>) [Updated Code](<https://github.com/KillerQueen-Z/llm-rank-optimizer>)| Raw Results, Summarized Results |
| Zhe Chen | [Large Language Models are Zero-Shot Rankers for Recommender Systems](https://arxiv.org/abs/2305.08845) (**Only using Dataset and not Algorithm**) | Content Recommendation (movies, products, etc) | [LLMRank JSON Datasets](https://drive.google.com/drive/folders/1lw478Vt1IdlXz0Kzqrzr6NzUbfL093qU?usp=drive_link) | | NDCG@K (K=1,5,10,20) | [Code](https://github.com/RUCAIBox/LLMRank) | Raw Results, Summarized Results |
| Andrew Yu | [Adversarial Search Engine Optimization for Large Language Models](https://arxiv.org/pdf/2406.18382) | | [Fictitious product data, combination of real and attack (e.g., books, photography, furniture)](https://github.com/glad-lab/geobench/tree/main/Datasets/AdversarialSEO) | | Rank Position, Attack Success Rate | [Code](https://github.com/freddysongg/Adversarial-SEO) | Raw Results, Summarized Results |
| Ojas Nimase | Are LLMs Reliable Rankers? Rank Manipulation via Two-Stage Token Optimization ([RAF](<https://arxiv.org/abs/2510.06732>)) | Product rankings mainly | Same as Stealth Rank STS Data: [Branch](https://github.com/glad-lab/geobench/tree/RAF/data2/json)  | Same as Stealth Rank STS Data: [Data](https://github.com/glad-lab/geobench/blob/Stealth-Rank/unified_dataset.json) | Rank, Perplexity (naturalness of text), Bad Word Ratio (proportion of prompts containing promotional keywords) | [Original Code](https://github.com/glad-lab/RAF) | Raw Results, Summarized Results |
| Gengpei Qi | [Ranking Manipulation for Conversational Search Engines](https://arxiv.org/abs/2406.03589) | | [Ragdoll](https://huggingface.co/datasets/Bai-YT/RAGDOLL) | [Data](https://drive.google.com/drive/folders/1pUsJw0AibGXnadS7VnxgOH-Y96AJG0ax) | Not sure yet | Main Code   Updated Code | Raw Results, Summarized Results |

## Dataset Metadata Table
| Dataset Name | Source Paper | Total Items | Number of Categories | Avg Items per Category | Categories | Domain/Field | Link |
|--------------|--------------|-------------|---------------------|------------------------|--------------|--------------|------|
| Ragroll | Stealth Rank | 399 | 50 | 7.98 | <details><summary>View all 50 categories</summary>air compressor, air purifier, automatic garden watering system, barbecue grill, beard trimmer, blender, coffee maker, computer monitor, computer power supply, cordless drill, curling iron, dishwasher, electric sander, electric toothbrush, eyeshadow, fascia gun, hair dryer, hair straightener, hammock, hedge trimmer, laptop, laser measure, lawn mower, leaf blower, lipstick, microwave oven, network attached storage, noise-canceling headphone, paint sprayer, pool cleaner, portable air conditioner, portable speaker, pressure washer, robot vacuum, screw driver, shampoo, skin cleansing brush, sleeping bag, slow cooker, smartphone, solid state drive, space heater, string trimmer, tablet, tent, tool chest, washing machine, wet-dry vacuum, wifi router, wood router</details> | Products | [Branch](https://github.com/glad-lab/geobench/tree/Stealth-Rank/data2/ragroll) |
| STSData | Stealth Rank | 30 | 3 | 10.00 | books, cameras, coffee_machines | Products | [Branch](https://github.com/glad-lab/geobench/tree/Stealth-Rank/data2/json) |
| STSData | RAF | 30 | 3 | 10.00 | books, cameras, coffee_machines | Products | [Branch](https://github.com/glad-lab/geobench/tree/RAF/data2/json) |
| RewriteToRank | Rewrite-to-Rank | 10000 | 2202 | 4.54 |  | Products | [Data](https://github.com/glad-lab/geobench/tree/main/Datasets/RewriteToRank) |
| C-SEO Bench | C-SEO Bench Does Conversational SEO Work | 16360 | 6 | 2726.67 | books, debate, news, retail, videogames, web | Mixed | [Data](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) |
| llm-rank-optimizer | Manipulating LLMs to Increase Product Visibility | 40 | 4 | 10.00 | books, cameras, coffee_machines, election_articles | Products | [Data](https://github.com/glad-lab/geobench/tree/main/Datasets/llm-rank-optimizer) |
| LLMRank | Large Language Models are Zero-Shot Rankers for Recommender Systems | 6408 | 18 | 356.00 | <details><summary>View all 18 categories</summary>Action, Adventure, Animation, Children's, Comedy, Crime, Documentary, Drama, Fantasy, Film-Noir, Horror, Musical, Mystery, Romance, Sci-Fi, Thriller, War, Western</details> | Movies/Content Recommendation | [Data](https://drive.google.com/drive/folders/1lw478Vt1IdlXz0Kzqrzr6NzUbfL093qU?usp=drive_link) |
| | Adversarial Search Engine Optimization for LLMs | 63 | 7 |  9.0 | <details><summary>View all 7 categories</summary> Cameras, Books & Media, Computing Hardware, Home Furniture, Kitchen Appliances, Lenses, Accessories</details> | Products | [Data](https://github.com/glad-lab/geobench/tree/main/Datasets/AdversarialSEO) |
| Ragdoll | Ranking Manipulation for Conversational Search Engines | 832 | 50 | 16.64 | <details><summary>View all 50 categories</summary>air compressor, air purifier, automatic garden watering system, barbecue grill, beard trimmer, blender, coffee maker, computer monitor, computer power supply, cordless drill, curling iron, dishwasher, electric sander, electric toothbrush, eyeshadow, fascia gun, hair dryer, hair straightener, hammock, hedge trimmer, laptop, laser measure, lawn mower, leaf blower, lipstick, microwave oven, network attached storage, noise-canceling headphone, paint sprayer, pool cleaner, portable air conditioner, portable speaker, pressure washer, robot vacuum, screw driver, shampoo, skin cleansing brush, sleeping bag, slow cooker, smartphone, solid state drive, space heater, string trimmer, tablet, tent, tool chest, washing machine, wet-dry vacuum, wifi router, wood router</details> | Products | [Data](https://drive.google.com/drive/folders/1pUsJw0AibGXnadS7VnxgOH-Y96AJG0ax) |

### StealthRank requirement for unified JSONL datasets

For StealthRank to run cleanly and comparably across categories, each `{catalog}.jsonl`
must:

1. Contain **more than one product**, and  
2. Contain **the same number of products across all categories**.

**Reasoning:**

- StealthRank runs a separate optimization for each `target_product_idx`, i.e., for each
  product line in `{catalog}.jsonl`. If a file has only one product, you can only run
  StealthRank once for that category.
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
      <td rowspan="5">C-SEO Bench Does Conversational SEO Work</td>
      <td>Stealth Rank</td>
      <td><a href="https://github.com/glad-lab/geobench/blob/cseo/CSEO_Results.md"> all results </a></td>
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
