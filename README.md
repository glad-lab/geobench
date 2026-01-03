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

<!-- ========================================================================= -->
<!-- Ranking Manipulation for Conversational Search Engines Results          -->
<!-- ========================================================================= -->

<h2 style="margin-top: 40px; margin-bottom: 20px; font-family: Arial, sans-serif; color: #333;">
  Ranking Manipulation for Conversational Search Engines - Evaluation Results
</h2>

<table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px;">
  <thead>
    <tr style="background: linear-gradient(to bottom, #4a90e2, #357abd); color: white;">
      <th style="padding: 12px 8px; text-align: left; border: 1px solid #ddd; font-weight: 600;">Test Dataset</th>
      <th style="padding: 12px 8px; text-align: left; border: 1px solid #ddd; font-weight: 600;">Model</th>
      <th style="padding: 12px 8px; text-align: left; border: 1px solid #ddd; font-weight: 600;">Category</th>
      <th style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-weight: 600;">NRG</th>
      <th style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-weight: 600;">Success@0.1</th>
      <th style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-weight: 600;">Promote@0.1</th>
      <th style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-weight: 600;">KVR</th>
      <th style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-weight: 600;">MRR</th>
      <th style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-weight: 600;">PPL-R</th>
    </tr>
  </thead>
  <tbody>
    <!-- Ragroll Dataset -->
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd; font-weight: 600; color: #2c3e50;">Ragroll</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; font-style: italic;">All categories (49)</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">0.84</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">0.84</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">0.92</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">0.8835</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>

    <!-- STSData Dataset -->
    <tr style="background-color: #fff;">
      <td rowspan="4" style="padding: 10px 8px; border: 1px solid #ddd; font-weight: 600; vertical-align: top; color: #2c3e50;">STSData</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">books</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">cameras</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.1000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">coffee_machines</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.1111</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #cfe2ff; font-weight: 600;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">📊 Overall (3 categories)</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.33</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.33</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.67</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.4037</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>

    <!-- RewriteToRank Dataset -->
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd; font-weight: 600; color: #2c3e50;">RewriteToRank</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; font-style: italic;">All categories (50)</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">0.78</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">0.78</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">0.86</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">0.8354</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>

    <!-- LLM Rank Optimizer Dataset -->
    <tr style="background-color: #fff;">
      <td rowspan="5" style="padding: 10px 8px; border: 1px solid #ddd; font-weight: 600; vertical-align: top; color: #2c3e50;">LLM Rank Optimizer</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">books</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">cameras</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">coffee_machines</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">election_articles</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #cfe2ff; font-weight: 600;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">📊 Overall (4 categories)</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.75</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>

    <!-- LLM Rank Dataset -->
    <tr style="background-color: #f8f9fa;">
      <td rowspan="8" style="padding: 10px 8px; border: 1px solid #ddd; font-weight: 600; vertical-align: top; color: #2c3e50;">LLM Rank</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">computers</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">software</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">books</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.2000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">automotive</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">baby</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">grocery</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.1429</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">appliances</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #cfe2ff; font-weight: 600;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">📊 Overall (7 categories)</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.71</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.71</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.57</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.7633</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>

    <!-- AdversarialSEO Dataset -->
    <tr style="background-color: #fff;">
      <td rowspan="8" style="padding: 10px 8px; border: 1px solid #ddd; font-weight: 600; vertical-align: top; color: #2c3e50;">AdversarialSEO</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">cameras</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">books_and_media</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.1250</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">computing_hardware</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">home_furniture</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">kitchen_appliances</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">lenses</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.2500</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">accessories</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.5000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #cfe2ff; font-weight: 600;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">📊 Overall (7 categories)</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.57</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.57</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.6964</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>

    <!-- C-SEO Dataset -->
    <tr style="background-color: #f8f9fa;">
      <td rowspan="7" style="padding: 10px 8px; border: 1px solid #ddd; font-weight: 600; vertical-align: top; color: #2c3e50;">C-SEO</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">books</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">debate</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">news</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">retail</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">videogames</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.0000</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #f8f9fa;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">web</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #f8d7da;">0.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #d4edda;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.1111</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
    <tr style="background-color: #cfe2ff; font-weight: 600;">
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">📊 Overall (6 categories)</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.83</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.67</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">1.00</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center;">0.8519</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>

    <!-- Ragdoll Dataset -->
    <tr style="background-color: #fff;">
      <td style="padding: 10px 8px; border: 1px solid #ddd; font-weight: 600; color: #2c3e50;">Ragdoll</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd;">groq-llama3-8b</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; font-style: italic;">All categories (50)</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.38</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.38</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.60</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; background-color: #fff3cd;">0.4053</td>
      <td style="padding: 10px 8px; border: 1px solid #ddd; text-align: center; color: #999;">NA</td>
    </tr>
  </tbody>
</table>

<div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #4a90e2; font-family: Arial, sans-serif; font-size: 13px; color: #555;">
  <strong style="color: #2c3e50;">Legend:</strong>
  <ul style="margin-top: 8px; margin-bottom: 0; line-height: 1.8;">
    <li><span style="background-color: #d4edda; padding: 2px 8px; border-radius: 3px;">Green</span> = High performance (≥0.75)</li>
    <li><span style="background-color: #fff3cd; padding: 2px 8px; border-radius: 3px;">Yellow</span> = Medium performance (0.25-0.74)</li>
    <li><span style="background-color: #f8d7da; padding: 2px 8px; border-radius: 3px;">Red</span> = Low performance (<0.25)</li>
    <li><span style="background-color: #cfe2ff; padding: 2px 8px; border-radius: 3px;">Blue</span> = Overall aggregated results</li>
    <li><span style="color: #999;">NA</span> = Not applicable or not available</li>
  </ul>
  <p style="margin-top: 12px; margin-bottom: 0; font-size: 12px; font-style: italic;">
    📊 Overall rows represent aggregated metrics across all categories for each test dataset using the groq-llama3-8b model.
  </p>
</div>
