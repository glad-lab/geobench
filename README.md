let us upload datasets to the github [Datasets](https://github.com/glad-lab/geobench/tree/main/Datasets), if it is really large, upload to [the google drive](https://drive.google.com/drive/folders/1zcMZWQGrDCNr6qI2sJ36KDQKnocEgZAp?usp=drive_link) instead.

## Paper Assignments

| Person   | Assigned Paper Title                    | Paper Objective (Product Ranking, Content Recommendation, etc)      | Dataset Used                        | Unified Dataset | Metrics                        | Code | Results |
|----------|---------------------------------------| --------|-------------------------------------| ------------------------------------- | -------------------------------------|-------------------------------------| ------------------------------------- |
| Andrew Yu    | [Rewrite-to-Rank](https://arxiv.org/abs/2507.21099) (**Only using Dataset and not Algorithm**) | | [RewriteToRank](https://github.com/glad-lab/geobench/tree/main/Datasets/RewriteToRank) |[Data](https://github.com/glad-lab/geobench/blob/main/Datasets/GEO/unified_dataset.json)                  | ∆MRR(Change in ranking of ads), ∆DIR(Change in inclusion) | [Main Code](https://github.com/dan778912/ad-doc-reranker/tree/main) <br>[PPO Code](https://github.com/dan778912/adppolora/tree/main) | Raw Results, Summarized Results |
| Ojas Nimase | [Stealth Rank](https://arxiv.org/abs/2504.05804) | Product rankings mainly | [main branch](https://github.com/glad-lab/geobench/tree/main/Datasets/StealthRank), [stealth rank branch](https://github.com/glad-lab/geobench/tree/Stealth-Rank/data2) | [Data](https://github.com/glad-lab/geobench/tree/Stealth-Rank/unified_data) | Rank, Perplexity (naturalness of text), Bad Word Ratio (proportion of prompts containing promotional keywords) | [Replicated Code](https://github.com/glad-lab/geobench/tree/Stealth-Rank), [Original Code](https://github.com/Tangyiming205069/controllable-seo/tree/main) | [Raw Results](https://github.com/glad-lab/geobench/tree/Stealth-Rank/results_new), [Summarized Results](https://github.com/glad-lab/geobench/blob/Stealth-Rank/results_summary.md) | 
| Gengpei Qi | [C-SEO Bench Does Conversational SEO Work](https://arxiv.org/abs/2506.11097) | | [C-SEO Bench](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) | [Data](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) | Rank Improvement， Area Under the Curve - AUC， Statistical Significance | [Main Code](https://github.com/parameterlab/c-seo-bench) <br> [Updated Code](https://github.com/gengpeiqi2001/2.0-cseo) | Raw Results, Summarized Results |
| Zhe Chen | [Manipulating LLMs to Increase Product Visibility](https://arxiv.org/abs/2404.07981) | | Fictitious product catalogs (e.g., coffee machines, books, cameras)(details in [data folder](<https://github.com/glad-lab/geobench/tree/main/Datasets/llm-rank-optimizer>)) | [Data](https://github.com/glad-lab/geobench/blob/main/Datasets/llm-rank-optimizer/data/unified_dataset.json) | Rank Distribution | [Main Code](<https://github.com/aounon/llm-rank-optimizer>) [Updated Code](<https://github.com/KillerQueen-Z/llm-rank-optimizer>)| Raw Results, Summarized Results |
| Zhe Chen | [Large Language Models are Zero-Shot Rankers for Recommender Systems](https://arxiv.org/abs/2305.08845) (**Only using Dataset and not Algorithm**) | Content Recommendation (movies, products, etc) | [LLMRank JSON Datasets](https://drive.google.com/drive/folders/1lw478Vt1IdlXz0Kzqrzr6NzUbfL093qU?usp=drive_link) | [Data](https://github.com/glad-lab/geobench/blob/main/Datasets/Zero-Shot%20Rankers/unified_dataset.json) | NDCG@K (K=1,5,10,20) | [Code](https://github.com/RUCAIBox/LLMRank) | Raw Results, Summarized Results |
| Andrew Yu | [Adversarial Search Engine Optimization for Large Language Models](https://arxiv.org/pdf/2406.18382) | | [Fictitious product data, combination of real and attack (e.g., books, photography, furniture)](https://github.com/glad-lab/geobench/tree/main/Datasets/AdversarialSEO) | | Rank Position, Attack Success Rate | [Code](https://github.com/freddysongg/Adversarial-SEO) | Raw Results, Summarized Results |
| Ojas Nimase | Are LLMs Reliable Rankers? Rank Manipulation via Two-Stage Token Optimization ([RAF](<https://arxiv.org/abs/2510.06732>)) | Product rankings mainly | Same as Stealth Rank STS Data: [Branch](https://github.com/glad-lab/geobench/tree/RAF/data2/json)  | Same as Stealth Rank STS Data: [Data](https://github.com/glad-lab/geobench/tree/Stealth-Rank/unified_data) | Rank, Perplexity (naturalness of text), Bad Word Ratio (proportion of prompts containing promotional keywords) | [Original Code](https://github.com/glad-lab/RAF) | Raw Results, Summarized Results |
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
| MovieLens 1M | Large Language Models are Zero-Shot Rankers for Recommender Systems | 3841 | 18 | 353.22 | <details><summary>View all 18 categories</summary>Action, Adventure, Animation, Children's, Comedy, Crime, Documentary, Drama, Fantasy, Film-Noir, Horror, Musical, Mystery, Romance, Sci-Fi, Thriller, War, Western</details> | Movies/Content Recommendation | [Data](https://github.com/glad-lab/geobench/blob/main/Datasets/Zero-Shot%20Rankers/unified_dataset.json) |
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

Stealth Rank results are here: https://github.com/glad-lab/geobench/blob/Stealth-Rank/benchmark_results.md


## Ranking Manipulation for Conversational Search Engines - Evaluation Results

<table>
  <thead>
    <tr>
      <th align="left">Test Dataset</th>
      <th align="left">Model</th>
      <th align="left">Category</th>
      <th align="center">NRG</th>
      <th align="center">Success@0.1</th>
      <th align="center">Promote@0.1</th>
      <th align="center">KVR</th>
      <th align="center">MRR</th>
      <th align="center">PPL-R</th>
    </tr>
  </thead>
  <tbody>
    <!-- Ragroll Dataset -->
    <tr>
      <td><strong>Ragroll</strong></td>
      <td>groq-llama3-8b</td>
      <td><em>All categories (49)</em></td>
      <td align="center">NA</td>
      <td align="center"><strong>0.84</strong></td>
      <td align="center"><strong>0.84</strong></td>
      <td align="center"><strong>0.96</strong></td>
      <td align="center"><strong>0.8835</strong></td>
      <td align="center">NA</td>
    </tr>
    <!-- STSData Dataset -->
    <tr>
      <td rowspan="4"><strong>STSData</strong></td>
      <td>groq-llama3-8b</td>
      <td>books</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>cameras</td>
      <td align="center">NA</td>
      <td align="center">0.00</td>
      <td align="center">0.00</td>
      <td align="center">1.00</td>
      <td align="center">0.1000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>coffee_machines</td>
      <td align="center">NA</td>
      <td align="center">0.00</td>
      <td align="center">0.00</td>
      <td align="center">1.00</td>
      <td align="center">0.1111</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td><strong>📊 Overall (3 categories)</strong></td>
      <td align="center">NA</td>
      <td align="center"><strong>0.33</strong></td>
      <td align="center"><strong>0.33</strong></td>
      <td align="center"><strong>1.00</strong></td>
      <td align="center"><strong>0.4037</strong></td>
      <td align="center">NA</td>
    </tr>
    <!-- RewriteToRank Dataset -->
    <tr>
      <td><strong>RewriteToRank</strong></td>
      <td>groq-llama3-8b</td>
      <td><em>All categories (50)</em></td>
      <td align="center">NA</td>
      <td align="center"><strong>0.78</strong></td>
      <td align="center"><strong>0.78</strong></td>
      <td align="center"><strong>0.90</strong></td>
      <td align="center"><strong>0.8354</strong></td>
      <td align="center">NA</td>
    </tr>
    <!-- LLM Rank Optimizer Dataset -->
    <tr>
      <td rowspan="5"><strong>LLM Rank Optimizer</strong></td>
      <td>groq-llama3-8b</td>
      <td>books</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>cameras</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>coffee_machines</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>election_articles</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">0.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td><strong>📊 Overall (4 categories)</strong></td>
      <td align="center">NA</td>
      <td align="center"><strong>1.00</strong></td>
      <td align="center"><strong>1.00</strong></td>
      <td align="center"><strong>0.75</strong></td>
      <td align="center"><strong>1.0000</strong></td>
      <td align="center">NA</td>
    </tr>
    <!-- LLM Rank Dataset -->
    <tr>
      <td rowspan="8"><strong>LLM Rank</strong></td>
      <td>groq-llama3-8b</td>
      <td>computers</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>software</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">0.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>books</td>
      <td align="center">NA</td>
      <td align="center">0.00</td>
      <td align="center">0.00</td>
      <td align="center">1.00</td>
      <td align="center">0.2000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>automotive</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>baby</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">0.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>grocery</td>
      <td align="center">NA</td>
      <td align="center">0.00</td>
      <td align="center">0.00</td>
      <td align="center">1.00</td>
      <td align="center">0.1429</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>appliances</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">0.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td><strong>📊 Overall (7 categories)</strong></td>
      <td align="center">NA</td>
      <td align="center"><strong>0.71</strong></td>
      <td align="center"><strong>0.71</strong></td>
      <td align="center"><strong>0.57</strong></td>
      <td align="center"><strong>0.7633</strong></td>
      <td align="center">NA</td>
    </tr>
    <!-- AdversarialSEO Dataset -->
    <tr>
      <td rowspan="8"><strong>AdversarialSEO</strong></td>
      <td>groq-llama3-8b</td>
      <td>cameras</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>books_and_media</td>
      <td align="center">NA</td>
      <td align="center">0.00</td>
      <td align="center">0.00</td>
      <td align="center">1.00</td>
      <td align="center">0.1250</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>computing_hardware</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>home_furniture</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>kitchen_appliances</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>lenses</td>
      <td align="center">NA</td>
      <td align="center">0.00</td>
      <td align="center">0.00</td>
      <td align="center">1.00</td>
      <td align="center">0.2500</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>accessories</td>
      <td align="center">NA</td>
      <td align="center">0.00</td>
      <td align="center">0.00</td>
      <td align="center">1.00</td>
      <td align="center">0.5000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td><strong>📊 Overall (7 categories)</strong></td>
      <td align="center">NA</td>
      <td align="center"><strong>0.57</strong></td>
      <td align="center"><strong>0.57</strong></td>
      <td align="center"><strong>1.00</strong></td>
      <td align="center"><strong>0.6964</strong></td>
      <td align="center">NA</td>
    </tr>
    <!-- C-SEO Dataset -->
    <tr>
      <td rowspan="7"><strong>C-SEO</strong></td>
      <td>groq-llama3-8b</td>
      <td>books</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>debate</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>news</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">0.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>retail</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>videogames</td>
      <td align="center">NA</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.00</td>
      <td align="center">1.0000</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td>web</td>
      <td align="center">NA</td>
      <td align="center">0.00</td>
      <td align="center">0.00</td>
      <td align="center">1.00</td>
      <td align="center">0.1111</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td><strong>📊 Overall (6 categories)</strong></td>
      <td align="center">NA</td>
      <td align="center"><strong>0.83</strong></td>
      <td align="center"><strong>0.67</strong></td>
      <td align="center"><strong>1.00</strong></td>
      <td align="center"><strong>0.8519</strong></td>
      <td align="center">NA</td>
    </tr>
    <!-- Ragdoll Dataset -->
    <tr>
      <td><strong>Ragdoll</strong></td>
      <td>groq-llama3-8b</td>
      <td><em>All categories (50)</em></td>
      <td align="center">NA</td>
      <td align="center"><strong>0.38</strong></td>
      <td align="center"><strong>0.38</strong></td>
      <td align="center"><strong>0.60</strong></td>
      <td align="center"><strong>0.4053</strong></td>
      <td align="center">NA</td>
    </tr>
  </tbody>
</table>

> **Note:**
> - 📊 **Overall** rows represent aggregated metrics across all categories for each test dataset.
> - All evaluations use the **groq-llama3-8b** model.
> - **NA** indicates that the metric is not applicable or not available.
> - Values in **bold** indicate overall/summary metrics.

## C-SEO - Evaluation Results

- **[Complete Results](https://github.com/glad-lab/geobench/blob/cseo/results.md)** - Full benchmark evaluation with all metrics
