let us upload datasets to the github [Datasets](https://github.com/glad-lab/geobench/tree/main/Datasets), if it is really large, upload to [the google drive](https://drive.google.com/drive/folders/1zcMZWQGrDCNr6qI2sJ36KDQKnocEgZAp?usp=drive_link) instead.

## Paper Assignments

| Person   | Assigned Paper Title                    | Paper Objective (Product Ranking, Content Recommendation, etc)      | Dataset Used                        | Unified Dataset | Metrics                        | Code | Results |
|----------|---------------------------------------| --------|-------------------------------------| ------------------------------------- | -------------------------------------|-------------------------------------| ------------------------------------- |
| Andrew Yu    | [Rewrite-to-Rank](https://arxiv.org/abs/2507.21099) (**Only using Dataset and not Algorithm**) | | [RewriteToRank](https://github.com/glad-lab/geobench/tree/main/Datasets/RewriteToRank) |[Data](https://github.com/glad-lab/geobench/blob/main/Datasets/GEO/unified_dataset.json)                  | ∆MRR(Change in ranking of ads), ∆DIR(Change in inclusion) | [Main Code](https://github.com/dan778912/ad-doc-reranker/tree/main) <br>[PPO Code](https://github.com/dan778912/adppolora/tree/main) | Raw Results, Summarized Results |
| Ojas Nimase | [Stealth Rank](https://arxiv.org/abs/2504.05804) | Product rankings mainly | [main branch](https://github.com/glad-lab/geobench/tree/main/Datasets/StealthRank), [stealth rank branch](https://github.com/glad-lab/geobench/tree/Stealth-Rank/data2) | [Data](https://github.com/glad-lab/geobench/tree/Stealth-Rank/unified_data) | Rank, Perplexity (naturalness of text), Bad Word Ratio (proportion of prompts containing promotional keywords) | [Replicated Code](https://github.com/glad-lab/geobench/tree/Stealth-Rank), [Original Code](https://github.com/Tangyiming205069/controllable-seo/tree/main) | [Raw Results](https://github.com/glad-lab/geobench/tree/Stealth-Rank/results_new), [Summarized Results](https://github.com/glad-lab/geobench/blob/Stealth-Rank/results_summary.md) | 
| Gengpei Qi | [C-SEO Bench Does Conversational SEO Work](https://arxiv.org/abs/2506.11097) | | [C-SEO Bench](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) | [Data](https://drive.google.com/drive/folders/1PePkMvDAeEEW0G53QPNafBAZj0uibJdj) | Rank Improvement， Area Under the Curve - AUC， Statistical Significance | [Main Code](https://github.com/parameterlab/c-seo-bench) <br> [Updated Code](https://github.com/gengpeiqi2001/2.0-cseo) | Raw Results, Summarized Results |
| Zhe Chen | [Manipulating LLMs to Increase Product Visibility](https://arxiv.org/abs/2404.07981) | | Fictitious product catalogs (e.g., coffee machines, books, cameras)(details in [data folder](<https://github.com/glad-lab/geobench/tree/main/Datasets/llm-rank-optimizer>)) | [Data](https://github.com/glad-lab/geobench/blob/main/Datasets/llm-rank-optimizer/data/unified_dataset.json) | Rank Distribution | [Main Code](<https://github.com/aounon/llm-rank-optimizer>) [Updated Code](<https://github.com/KillerQueen-Z/llm-rank-optimizer>)| Raw Results, Summarized Results |
| Zhe Chen | [Large Language Models are Zero-Shot Rankers for Recommender Systems](https://arxiv.org/abs/2305.08845) (**Only using Dataset and not Algorithm**) | Content Recommendation (movies, products, etc) | [LLMRank JSON Datasets](https://drive.google.com/drive/folders/1lw478Vt1IdlXz0Kzqrzr6NzUbfL093qU?usp=drive_link) | [Data](https://drive.google.com/drive/folders/1lw478Vt1IdlXz0Kzqrzr6NzUbfL093qU?usp=drive_link) | NDCG@K (K=1,5,10,20) | [Code](https://github.com/RUCAIBox/LLMRank) | Raw Results, Summarized Results |
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
<table border="1" style="width: 100%; table-layout: fixed; border-collapse: collapse;">
  <thead>
    <tr>
      <th rowspan="2">Algorithm</th>
      <th rowspan="2">Test Dataset</th>
      <th colspan="5" style="text-align: center;">Evaluation Metrics</th>
    </tr>
    <tr>
      <th>NRG</th>
      <th>Success@0.1</th>
      <th>Promote@0.1</th>
      <th>KVR</th>
      <th>PPL-R</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td rowspan="7">Rewrite-to-Rank</td>
      <td>Ragroll</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>STSData</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>RewriteToRank</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>LLM Rank Optimizer</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>LLM Rank</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>AdversarialSEO</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>Ragdoll</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td rowspan="7">StealthRank</td>
      <td>Ragroll</td>
      <td>NA</td>NA<td>NA</td>NA<td>NA</td>NA<td>NA</td>NA<td>NA</td>
    </tr>
    <tr>
      <td>STSData</td>
      <td>NA</td>NA<td>NA</td>NA<td>NA</td>NA<td>NA</td>NA<td>NA</td>
    </tr>
    <!-- StealthRank × RewriteToRank with nested table + per-model aggregation -->
    <tr>
      <td>
        RewriteToRank
        (DeepSeek 7B + Mistral 7B: 2 categories; Llama 3.1 8B + Vicuna 7B: 1 category)
      </td>
      <td colspan="5" style="padding: 8px;">
        <table border="1" style="width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 12px; line-height: 1.25;">
          <thead>
            <tr>
              <th style="width: 14%;">Model</th>
              <th style="width: 18%;">Category</th>
              <th style="width: 14%;">NRG</th>
              <th style="width: 14%;">Success@0.1 (reach)</th>
              <th style="width: 14%;">Promote@0.1</th>
              <th style="width: 13%;">KVR</th>
              <th style="width: 13%;">PPL-R</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>deepseek-7b</td>
              <td>electrical_supplies</td>
              <td>0.250±0.463</td>
              <td>0.25</td>
              <td>0.25</td>
              <td>0.25±0.46</td>
              <td>1.15±0.66</td>
            </tr>
            <tr>
              <td>deepseek-7b</td>
              <td>gun_accessories</td>
              <td>0.161±0.354</td>
              <td>0.38</td>
              <td>0.25</td>
              <td>0.38±0.52</td>
              <td>1.31±0.60</td>
            </tr>
            <tr>
              <td><strong>deepseek-7b</strong></td>
              <td><strong>Overall (micro)</strong></td>
              <td><strong>0.206±0.401</strong></td>
              <td><strong>0.31</strong></td>
              <td><strong>0.25</strong></td>
              <td><strong>0.315±0.479</strong></td>
              <td><strong>1.23±0.61</strong></td>
            </tr>
            <tr>
              <td>llama-3.1-8b</td>
              <td>electrical_supplies</td>
              <td>0.125±0.354</td>
              <td>0.25</td>
              <td>0.12</td>
              <td>0.62±0.52</td>
              <td>1.14±0.39</td>
            </tr>
            <tr>
              <td>mistral-7b</td>
              <td>electrical_supplies</td>
              <td>0.250±0.463</td>
              <td>0.12</td>
              <td>0.12</td>
              <td>0.38±0.52</td>
              <td>1.40±0.41</td>
            </tr>
            <tr>
              <td>mistral-7b</td>
              <td>gun_accessories</td>
              <td>0.018±0.051</td>
              <td>0.38</td>
              <td>0.12</td>
              <td>0.12±0.35</td>
              <td>1.65±1.56</td>
            </tr>
            <tr>
              <td><strong>mistral-7b</strong></td>
              <td><strong>Overall (micro)</strong></td>
              <td><strong>0.134±0.340</strong></td>
              <td><strong>0.25</strong></td>
              <td><strong>0.12</strong></td>
              <td><strong>0.25±0.45</strong></td>
              <td><strong>1.53±1.11</strong></td>
            </tr>
            <tr>
              <td>vicuna-7b</td>
              <td>electrical_supplies</td>
              <td>0.018±0.051</td>
              <td>0.25</td>
              <td>0.12</td>
              <td>0.38±0.52</td>
              <td>0.96±0.28</td>
            </tr>
          </tbody>
        </table>
        <div style="margin-top: 6px; font-size: 11px;">
          <em>Overall (micro) aggregates across available categories for that model (equal-weight here because each category has the same number of evaluated instances).</em>
        </div>
      </td>
    </tr>
    <tr>
      <td>LLM Rank Optimizer</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>LLM Rank</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>AdversarialSEO (skipping because descriptions lengths are too long and will probably cause OOM errors)</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>Ragdoll</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td rowspan="7">C-SEO</td>
      <td>Ragroll</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>STSData</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>RewriteToRank</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>LLM Rank Optimizer</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>LLM Rank</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>AdversarialSEO</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>Ragdoll</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td rowspan="7">STS (Kumar et al.)</td>
      <td>Ragroll</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>STSData</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>RewriteToRank</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>LLM Rank Optimizer</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>LLM Rank</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>AdversarialSEO</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>Ragdoll</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td rowspan="7">Baseline (Zero-Shot Ranker)</td>
      <td>Ragroll</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>STSData</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>RewriteToRank</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>LLM Rank Optimizer</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>LLM Rank</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>AdversarialSEO</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>Ragdoll</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td rowspan="7">PMA (Nestaas et al.)</td>
      <td>Ragroll</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>STSData</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>RewriteToRank</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>LLM Rank Optimizer</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>LLM Rank</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>AdversarialSEO</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td>Ragdoll</td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
  </tbody>
</table>

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
      <td align="center"><strong>0.92</strong></td>
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
      <td align="center">0.00</td>
      <td align="center">0.1111</td>
      <td align="center">NA</td>
    </tr>
    <tr>
      <td>groq-llama3-8b</td>
      <td><strong>📊 Overall (3 categories)</strong></td>
      <td align="center">NA</td>
      <td align="center"><strong>0.33</strong></td>
      <td align="center"><strong>0.33</strong></td>
      <td align="center"><strong>0.67</strong></td>
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
      <td align="center"><strong>0.86</strong></td>
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

## C-SEO Benchmark Comprehensive Metrics Results

<table>
  <thead>
    <tr>
      <th align="left">Dataset</th>
      <th align="left">Method</th>
      <th align="center">ΔRank</th>
      <th align="center">NRG</th>
      <th align="center">Succ@0.1</th>
      <th align="center">Succ@0.2</th>
      <th align="center">Prom@0.1</th>
      <th align="center">MRR Δ</th>
      <th align="center">p-value</th>
      <th align="center">Win Rate</th>
      <th align="center">Samples</th>
    </tr>
  </thead>
  <tbody>
    <!-- Books Dataset -->
    <tr>
      <td rowspan="10"><strong>Books</strong></td>
      <td>Statistics</td>
      <td align="center"><strong>0.3167</strong></td>
      <td align="center">0.0633</td>
      <td align="center">58.33%</td>
      <td align="center">58.33%</td>
      <td align="center">38.33%</td>
      <td align="center">0.1681</td>
      <td align="center"><strong>0.0012 ***</strong></td>
      <td align="center">31.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Quotes</td>
      <td align="center"><strong>0.2667</strong></td>
      <td align="center">0.0533</td>
      <td align="center">58.33%</td>
      <td align="center">58.33%</td>
      <td align="center">33.33%</td>
      <td align="center"><strong>0.2000</strong></td>
      <td align="center"><strong>0.0013 ***</strong></td>
      <td align="center">35.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center"><strong>0.2333</strong></td>
      <td align="center">0.0467</td>
      <td align="center">53.33%</td>
      <td align="center">53.33%</td>
      <td align="center">35.00%</td>
      <td align="center">0.1611</td>
      <td align="center"><strong>0.0066 ***</strong></td>
      <td align="center">33.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center"><strong>0.2333</strong></td>
      <td align="center">0.0467</td>
      <td align="center">50.00%</td>
      <td align="center">50.00%</td>
      <td align="center">35.00%</td>
      <td align="center">0.1306</td>
      <td align="center"><strong>0.0145 ***</strong></td>
      <td align="center">30.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center">0.1833</td>
      <td align="center">0.0367</td>
      <td align="center">41.67%</td>
      <td align="center">41.67%</td>
      <td align="center">28.33%</td>
      <td align="center">0.0389</td>
      <td align="center"><strong>0.0438 ***</strong></td>
      <td align="center">28.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Authoritative</td>
      <td align="center">0.1333</td>
      <td align="center">0.0267</td>
      <td align="center">50.00%</td>
      <td align="center">50.00%</td>
      <td align="center">30.00%</td>
      <td align="center">0.1222</td>
      <td align="center"><strong>0.0237 ***</strong></td>
      <td align="center">31.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">0.1333</td>
      <td align="center">0.0267</td>
      <td align="center">40.00%</td>
      <td align="center">40.00%</td>
      <td align="center">25.00%</td>
      <td align="center">0.0444</td>
      <td align="center">0.0645</td>
      <td align="center">25.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center">0.0667</td>
      <td align="center">0.0133</td>
      <td align="center">48.33%</td>
      <td align="center">48.33%</td>
      <td align="center">25.00%</td>
      <td align="center">0.0906</td>
      <td align="center">0.1868</td>
      <td align="center">21.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">-0.0333</td>
      <td align="center">-0.0067</td>
      <td align="center">35.00%</td>
      <td align="center">35.00%</td>
      <td align="center">21.67%</td>
      <td align="center">-0.0347</td>
      <td align="center">0.4704</td>
      <td align="center">16.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">-0.0333</td>
      <td align="center">-0.0067</td>
      <td align="center">28.33%</td>
      <td align="center">28.33%</td>
      <td align="center">16.67%</td>
      <td align="center">-0.0494</td>
      <td align="center">0.5877</td>
      <td align="center">13.33%</td>
      <td align="center">60</td>
    </tr>
    <!-- Debate Dataset -->
    <tr>
      <td rowspan="10"><strong>Debate</strong></td>
      <td>LLMstxt</td>
      <td align="center">0.1000</td>
      <td align="center">0.0200</td>
      <td align="center">25.00%</td>
      <td align="center">25.00%</td>
      <td align="center">21.67%</td>
      <td align="center">0.0189</td>
      <td align="center">0.2452</td>
      <td align="center">20.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Quotes</td>
      <td align="center">0.0833</td>
      <td align="center">0.0167</td>
      <td align="center">23.33%</td>
      <td align="center">23.33%</td>
      <td align="center">16.67%</td>
      <td align="center">-0.0033</td>
      <td align="center">0.1284</td>
      <td align="center">18.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center">0.0833</td>
      <td align="center">0.0167</td>
      <td align="center">20.00%</td>
      <td align="center">20.00%</td>
      <td align="center">15.00%</td>
      <td align="center">-0.0367</td>
      <td align="center">0.1284</td>
      <td align="center">18.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center">0.0667</td>
      <td align="center">0.0133</td>
      <td align="center">33.33%</td>
      <td align="center">33.33%</td>
      <td align="center">28.33%</td>
      <td align="center">0.0883</td>
      <td align="center">0.2398</td>
      <td align="center">16.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center">0.0667</td>
      <td align="center">0.0133</td>
      <td align="center">15.00%</td>
      <td align="center">15.00%</td>
      <td align="center">8.33%</td>
      <td align="center">-0.0867</td>
      <td align="center">0.2071</td>
      <td align="center">11.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Statistics</td>
      <td align="center">0.0500</td>
      <td align="center">0.0100</td>
      <td align="center">20.00%</td>
      <td align="center">20.00%</td>
      <td align="center">11.67%</td>
      <td align="center">-0.0283</td>
      <td align="center">0.3527</td>
      <td align="center">13.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Authoritative</td>
      <td align="center">0.0333</td>
      <td align="center">0.0067</td>
      <td align="center">26.67%</td>
      <td align="center">26.67%</td>
      <td align="center">20.00%</td>
      <td align="center">0.0467</td>
      <td align="center">0.4323</td>
      <td align="center">11.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">0.0167</td>
      <td align="center">0.0033</td>
      <td align="center">16.67%</td>
      <td align="center">16.67%</td>
      <td align="center">13.33%</td>
      <td align="center">-0.0617</td>
      <td align="center">0.5344</td>
      <td align="center">8.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">-0.0167</td>
      <td align="center">-0.0033</td>
      <td align="center">25.00%</td>
      <td align="center">25.00%</td>
      <td align="center">15.00%</td>
      <td align="center">0.0133</td>
      <td align="center">0.5730</td>
      <td align="center">10.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">-0.0333</td>
      <td align="center">-0.0067</td>
      <td align="center">25.00%</td>
      <td align="center">25.00%</td>
      <td align="center">18.33%</td>
      <td align="center">0.0133</td>
      <td align="center">0.7929</td>
      <td align="center">6.67%</td>
      <td align="center">60</td>
    </tr>
    <!-- News Dataset -->
    <tr>
      <td rowspan="10"><strong>News</strong></td>
      <td>Quotes</td>
      <td align="center"><strong>0.1500</strong></td>
      <td align="center">0.0300</td>
      <td align="center">45.00%</td>
      <td align="center">45.00%</td>
      <td align="center">30.00%</td>
      <td align="center">0.1444</td>
      <td align="center">0.1192</td>
      <td align="center">23.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center">0.0667</td>
      <td align="center">0.0133</td>
      <td align="center">26.67%</td>
      <td align="center">26.67%</td>
      <td align="center">18.33%</td>
      <td align="center">-0.0556</td>
      <td align="center">0.2290</td>
      <td align="center">18.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">0.0667</td>
      <td align="center">0.0133</td>
      <td align="center">30.00%</td>
      <td align="center">30.00%</td>
      <td align="center">16.67%</td>
      <td align="center">-0.0139</td>
      <td align="center">0.1030</td>
      <td align="center">15.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">0.0167</td>
      <td align="center">0.0033</td>
      <td align="center">33.33%</td>
      <td align="center">33.33%</td>
      <td align="center">21.67%</td>
      <td align="center">0.0361</td>
      <td align="center">0.5546</td>
      <td align="center">13.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Statistics</td>
      <td align="center">0.0167</td>
      <td align="center">0.0033</td>
      <td align="center">21.67%</td>
      <td align="center">21.67%</td>
      <td align="center">15.00%</td>
      <td align="center">-0.0972</td>
      <td align="center">0.4014</td>
      <td align="center">11.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Authoritative</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">35.00%</td>
      <td align="center">35.00%</td>
      <td align="center">26.67%</td>
      <td align="center">0.0486</td>
      <td align="center">0.3402</td>
      <td align="center">10.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center">-0.0167</td>
      <td align="center">-0.0033</td>
      <td align="center">13.33%</td>
      <td align="center">13.33%</td>
      <td align="center">6.67%</td>
      <td align="center">-0.1583</td>
      <td align="center">0.5986</td>
      <td align="center">8.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">-0.0167</td>
      <td align="center">-0.0033</td>
      <td align="center">21.67%</td>
      <td align="center">21.67%</td>
      <td align="center">13.33%</td>
      <td align="center">-0.0889</td>
      <td align="center">0.6473</td>
      <td align="center">10.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center">-0.0667</td>
      <td align="center">-0.0133</td>
      <td align="center">21.67%</td>
      <td align="center">21.67%</td>
      <td align="center">16.67%</td>
      <td align="center">-0.0583</td>
      <td align="center">0.8222</td>
      <td align="center">8.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center">-0.1333</td>
      <td align="center">-0.0267</td>
      <td align="center">18.33%</td>
      <td align="center">18.33%</td>
      <td align="center">11.67%</td>
      <td align="center">-0.1167</td>
      <td align="center">0.8932</td>
      <td align="center">8.33%</td>
      <td align="center">60</td>
    </tr>
    <!-- Retail Dataset -->
    <tr>
      <td rowspan="10"><strong>Retail</strong></td>
      <td>Authoritative</td>
      <td align="center">0.0833</td>
      <td align="center">0.0167</td>
      <td align="center">31.67%</td>
      <td align="center">31.67%</td>
      <td align="center">26.67%</td>
      <td align="center">0.0972</td>
      <td align="center">0.2334</td>
      <td align="center">16.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center">0.0833</td>
      <td align="center">0.0167</td>
      <td align="center">33.33%</td>
      <td align="center">33.33%</td>
      <td align="center">26.67%</td>
      <td align="center">0.1167</td>
      <td align="center">0.1669</td>
      <td align="center">20.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center">0.0667</td>
      <td align="center">0.0133</td>
      <td align="center">23.33%</td>
      <td align="center">23.33%</td>
      <td align="center">18.33%</td>
      <td align="center">0.0278</td>
      <td align="center">0.2087</td>
      <td align="center">15.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center">0.0333</td>
      <td align="center">0.0067</td>
      <td align="center">21.67%</td>
      <td align="center">21.67%</td>
      <td align="center">15.00%</td>
      <td align="center">0.0250</td>
      <td align="center">0.2635</td>
      <td align="center">13.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">0.0333</td>
      <td align="center">0.0067</td>
      <td align="center">21.67%</td>
      <td align="center">21.67%</td>
      <td align="center">16.67%</td>
      <td align="center">0.0000</td>
      <td align="center">0.3815</td>
      <td align="center">11.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">0.0167</td>
      <td align="center">0.0033</td>
      <td align="center">18.33%</td>
      <td align="center">18.33%</td>
      <td align="center">16.67%</td>
      <td align="center">-0.0028</td>
      <td align="center">0.3694</td>
      <td align="center">10.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Statistics</td>
      <td align="center">0.0167</td>
      <td align="center">0.0033</td>
      <td align="center">23.33%</td>
      <td align="center">23.33%</td>
      <td align="center">20.00%</td>
      <td align="center">0.0250</td>
      <td align="center">0.4279</td>
      <td align="center">11.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">31.67%</td>
      <td align="center">31.67%</td>
      <td align="center">25.00%</td>
      <td align="center">0.1250</td>
      <td align="center">0.3551</td>
      <td align="center">11.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Quotes</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">21.67%</td>
      <td align="center">21.67%</td>
      <td align="center">15.00%</td>
      <td align="center">0.0083</td>
      <td align="center">0.5000</td>
      <td align="center">8.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">-0.0667</td>
      <td align="center">-0.0133</td>
      <td align="center">20.00%</td>
      <td align="center">20.00%</td>
      <td align="center">20.00%</td>
      <td align="center">-0.0028</td>
      <td align="center">0.7771</td>
      <td align="center">6.67%</td>
      <td align="center">60</td>
    </tr>
    <!-- Videogames Dataset -->
    <tr>
      <td rowspan="10"><strong>Videogames</strong></td>
      <td>Statistics</td>
      <td align="center"><strong>0.3667</strong></td>
      <td align="center">0.0733</td>
      <td align="center">43.33%</td>
      <td align="center">43.33%</td>
      <td align="center">30.00%</td>
      <td align="center"><strong>0.1979</strong></td>
      <td align="center"><strong>0.0307 ***</strong></td>
      <td align="center">28.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center"><strong>0.3500</strong></td>
      <td align="center">0.0700</td>
      <td align="center">33.33%</td>
      <td align="center">33.33%</td>
      <td align="center">20.00%</td>
      <td align="center">0.1368</td>
      <td align="center"><strong>0.0152 ***</strong></td>
      <td align="center">31.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Quotes</td>
      <td align="center"><strong>0.3167</strong></td>
      <td align="center">0.0633</td>
      <td align="center">40.00%</td>
      <td align="center">40.00%</td>
      <td align="center">31.67%</td>
      <td align="center"><strong>0.1993</strong></td>
      <td align="center">0.0795</td>
      <td align="center">36.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center"><strong>0.2667</strong></td>
      <td align="center">0.0533</td>
      <td align="center">31.67%</td>
      <td align="center">31.67%</td>
      <td align="center">21.67%</td>
      <td align="center">0.1451</td>
      <td align="center"><strong>0.0438 ***</strong></td>
      <td align="center">28.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center"><strong>0.2167</strong></td>
      <td align="center">0.0433</td>
      <td align="center">28.33%</td>
      <td align="center">28.33%</td>
      <td align="center">18.33%</td>
      <td align="center">0.0729</td>
      <td align="center"><strong>0.0424 ***</strong></td>
      <td align="center">20.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Authoritative</td>
      <td align="center">0.1667</td>
      <td align="center">0.0333</td>
      <td align="center">33.33%</td>
      <td align="center">33.33%</td>
      <td align="center">18.33%</td>
      <td align="center">0.1490</td>
      <td align="center">0.0809</td>
      <td align="center">26.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">0.1333</td>
      <td align="center">0.0267</td>
      <td align="center">28.33%</td>
      <td align="center">28.33%</td>
      <td align="center">21.67%</td>
      <td align="center">0.0938</td>
      <td align="center">0.2714</td>
      <td align="center">15.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">0.1167</td>
      <td align="center">0.0233</td>
      <td align="center">21.67%</td>
      <td align="center">21.67%</td>
      <td align="center">15.00%</td>
      <td align="center">0.0021</td>
      <td align="center">0.2680</td>
      <td align="center">16.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">0.0833</td>
      <td align="center">0.0167</td>
      <td align="center">31.67%</td>
      <td align="center">31.67%</td>
      <td align="center">20.00%</td>
      <td align="center">0.1271</td>
      <td align="center">0.3048</td>
      <td align="center">15.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center">-0.0500</td>
      <td align="center">-0.0100</td>
      <td align="center">16.67%</td>
      <td align="center">16.67%</td>
      <td align="center">10.00%</td>
      <td align="center">-0.0118</td>
      <td align="center">0.5890</td>
      <td align="center">10.00%</td>
      <td align="center">60</td>
    </tr>
    <!-- Web Dataset -->
    <tr>
      <td rowspan="10"><strong>Web</strong></td>
      <td>ContentImprovement</td>
      <td align="center">0.1500</td>
      <td align="center">0.0300</td>
      <td align="center">25.00%</td>
      <td align="center">25.00%</td>
      <td align="center">21.67%</td>
      <td align="center">0.0917</td>
      <td align="center">0.0536</td>
      <td align="center">21.67%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">0.1000</td>
      <td align="center">0.0200</td>
      <td align="center">28.33%</td>
      <td align="center">28.33%</td>
      <td align="center">25.00%</td>
      <td align="center">0.1333</td>
      <td align="center">0.1681</td>
      <td align="center">20.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center">0.0833</td>
      <td align="center">0.0167</td>
      <td align="center">35.00%</td>
      <td align="center">35.00%</td>
      <td align="center">30.00%</td>
      <td align="center"><strong>0.1917</strong></td>
      <td align="center"><strong>0.0294 ***</strong></td>
      <td align="center">18.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Quotes</td>
      <td align="center">0.0833</td>
      <td align="center">0.0167</td>
      <td align="center">26.67%</td>
      <td align="center">26.67%</td>
      <td align="center">25.00%</td>
      <td align="center">0.1083</td>
      <td align="center"><strong>0.0294 ***</strong></td>
      <td align="center">18.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center">0.0667</td>
      <td align="center">0.0133</td>
      <td align="center">31.67%</td>
      <td align="center">31.67%</td>
      <td align="center">28.33%</td>
      <td align="center">0.1639</td>
      <td align="center">0.1397</td>
      <td align="center">15.00%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Statistics</td>
      <td align="center">0.0333</td>
      <td align="center">0.0067</td>
      <td align="center">25.00%</td>
      <td align="center">25.00%</td>
      <td align="center">21.67%</td>
      <td align="center">0.1028</td>
      <td align="center">0.2943</td>
      <td align="center">13.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center">0.0000</td>
      <td align="center">-0.0000</td>
      <td align="center">25.00%</td>
      <td align="center">25.00%</td>
      <td align="center">25.00%</td>
      <td align="center">0.1139</td>
      <td align="center">0.5617</td>
      <td align="center">13.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">25.00%</td>
      <td align="center">25.00%</td>
      <td align="center">23.33%</td>
      <td align="center">0.0917</td>
      <td align="center">0.5000</td>
      <td align="center">13.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">-0.0333</td>
      <td align="center">-0.0067</td>
      <td align="center">26.67%</td>
      <td align="center">26.67%</td>
      <td align="center">20.00%</td>
      <td align="center">0.1167</td>
      <td align="center">0.8413</td>
      <td align="center">8.33%</td>
      <td align="center">60</td>
    </tr>
    <tr>
      <td>Authoritative</td>
      <td align="center">-0.0500</td>
      <td align="center">-0.0100</td>
      <td align="center">18.33%</td>
      <td align="center">18.33%</td>
      <td align="center">15.00%</td>
      <td align="center">0.0250</td>
      <td align="center">0.9101</td>
      <td align="center">6.67%</td>
      <td align="center">60</td>
    </tr>
  </tbody>
</table>

### Method Ranking Across All Datasets

<table>
  <thead>
    <tr>
      <th align="left">Rank</th>
      <th align="left">Method</th>
      <th align="center">Datasets</th>
      <th align="center">Avg ΔRank</th>
      <th align="center">Avg NRG</th>
      <th align="center">Avg Succ@0.1</th>
      <th align="center">Avg Prom@0.1</th>
      <th align="center">Avg MRR Δ</th>
      <th align="center">Avg Win Rate</th>
      <th align="center">Sig. Count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🥇 1</td>
      <td><strong>Quotes</strong></td>
      <td align="center">6</td>
      <td align="center"><strong>0.1500</strong></td>
      <td align="center">0.0300</td>
      <td align="center">35.83%</td>
      <td align="center">25.28%</td>
      <td align="center"><strong>0.1095</strong></td>
      <td align="center">15.28%</td>
      <td align="center">2/6</td>
    </tr>
    <tr>
      <td>🥈 2</td>
      <td><strong>Statistics</strong></td>
      <td align="center">6</td>
      <td align="center"><strong>0.1333</strong></td>
      <td align="center">0.0267</td>
      <td align="center">31.94%</td>
      <td align="center">22.78%</td>
      <td align="center">0.0614</td>
      <td align="center">14.17%</td>
      <td align="center">2/6</td>
    </tr>
    <tr>
      <td>🥉 3</td>
      <td><strong>Citations</strong></td>
      <td align="center">6</td>
      <td align="center"><strong>0.1194</strong></td>
      <td align="center">0.0239</td>
      <td align="center">33.33%</td>
      <td align="center">24.72%</td>
      <td align="center">0.0908</td>
      <td align="center">13.89%</td>
      <td align="center">3/6</td>
    </tr>
    <tr>
      <td>4</td>
      <td>ContentImprovement</td>
      <td align="center">6</td>
      <td align="center">0.1139</td>
      <td align="center">0.0228</td>
      <td align="center">28.06%</td>
      <td align="center">20.00%</td>
      <td align="center">0.0310</td>
      <td align="center">13.06%</td>
      <td align="center">2/6</td>
    </tr>
    <tr>
      <td>5</td>
      <td>TechnicalTerms</td>
      <td align="center">6</td>
      <td align="center">0.1000</td>
      <td align="center">0.0200</td>
      <td align="center">28.33%</td>
      <td align="center">20.83%</td>
      <td align="center">0.0426</td>
      <td align="center">14.72%</td>
      <td align="center">2/6</td>
    </tr>
    <tr>
      <td>6</td>
      <td>Authoritative</td>
      <td align="center">6</td>
      <td align="center">0.0611</td>
      <td align="center">0.0122</td>
      <td align="center">32.50%</td>
      <td align="center">22.78%</td>
      <td align="center">0.0815</td>
      <td align="center">13.06%</td>
      <td align="center">1/6</td>
    </tr>
    <tr>
      <td>7</td>
      <td>UniqueWords</td>
      <td align="center">6</td>
      <td align="center">0.0417</td>
      <td align="center">0.0083</td>
      <td align="center">26.11%</td>
      <td align="center">18.61%</td>
      <td align="center">0.0188</td>
      <td align="center">10.56%</td>
      <td align="center">0/6</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Fluency</td>
      <td align="center">6</td>
      <td align="center">0.0361</td>
      <td align="center">0.0072</td>
      <td align="center">28.06%</td>
      <td align="center">20.28%</td>
      <td align="center">0.0398</td>
      <td align="center">10.28%</td>
      <td align="center">0/6</td>
    </tr>
    <tr>
      <td>9</td>
      <td>LLMstxt</td>
      <td align="center">6</td>
      <td align="center">0.0250</td>
      <td align="center">0.0050</td>
      <td align="center">27.50%</td>
      <td align="center">19.44%</td>
      <td align="center">0.0380</td>
      <td align="center">11.11%</td>
      <td align="center">0/6</td>
    </tr>
    <tr>
      <td>10</td>
      <td>SimpleLanguage</td>
      <td align="center">6</td>
      <td align="center">0.0028</td>
      <td align="center">0.0006</td>
      <td align="center">25.28%</td>
      <td align="center">17.78%</td>
      <td align="center">0.0110</td>
      <td align="center">9.17%</td>
      <td align="center">0/6</td>
    </tr>
  </tbody>
</table>

> **Note:**
> - **ΔRank**: Delta Rank - Higher is better
> - **NRG**: Normalized Ranking Gain
> - **Succ@0.1/0.2**: Success at Top 10%/20%
> - **Prom@0.1**: Promote to Top 10%
> - **MRR Δ**: MRR Improvement
> - **p-value**: Statistical Significance (*** p<0.05)
> - **Win Rate**: Proportion of improved samples
> - **Sig. Count**: Number of datasets where p<0.05
> - Top 3 methods (Quotes, Statistics, Citations) show the best performance across datasets
> - Only 11 out of 60 evaluations (18.3%) achieved statistical significance (p < 0.05)
