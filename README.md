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

<h2 style="margin-top: 40px; margin-bottom: 20px;">Ranking Manipulation for Conversational Search Engines</h2>

<table border="1" style="width: 100%; table-layout: fixed; border-collapse: collapse;">
  <thead>
    <tr>
      <th rowspan="2">Test Dataset</th>
      <th colspan="6" style="text-align: center;">Evaluation Metrics</th>
    </tr>
    <tr>
      <th>NRG</th>
      <th>Success@0.1</th>
      <th>Promote@0.1</th>
      <th>KVR</th>
      <th>MRR</th>
      <th>PPL-R</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td>Ragroll (groq-llama3-8b: 49 categories)</td>
      <td>NA</td>
      <td>0.84</td>
      <td>0.84</td>
      <td>0.92</td>
      <td>0.8835</td>
      <td>NA</td>
    </tr>
    <tr>
      <!-- STSData dataset with expanded categories -->
      <td colspan="7" style="padding: 8px;">
        <div style="margin-bottom: 4px; font-weight: bold;">STSData (groq-llama3-8b: 3 categories)</div>
        <table border="1" style="width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 12px; line-height: 1.25;">
          <thead>
            <tr>
              <th style="width: 14%;">Model</th>
              <th style="width: 14%;">Category</th>
              <th style="width: 12%;">NRG</th>
              <th style="width: 12%;">Success@0.1</th>
              <th style="width: 12%;">Promote@0.1</th>
              <th style="width: 12%;">KVR</th>
              <th style="width: 12%;">MRR</th>
              <th style="width: 12%;">PPL-R</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>groq-llama3-8b</td>
              <td>books</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>cameras</td>
              <td>NA</td>
              <td>0.00</td>
              <td>0.00</td>
              <td>1.00</td>
              <td>0.1000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>coffee_machines</td>
              <td>NA</td>
              <td>0.00</td>
              <td>0.00</td>
              <td>0.00</td>
              <td>0.1111</td>
              <td>NA</td>
            </tr>
            <tr>
              <td><strong>groq-llama3-8b</strong></td>
              <td><strong>Overall</strong></td>
              <td><strong>NA</strong></td>
              <td><strong>0.33</strong></td>
              <td><strong>0.33</strong></td>
              <td><strong>0.67</strong></td>
              <td><strong>0.4037</strong></td>
              <td><strong>NA</strong></td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
    <tr>
      <td>RewriteToRank (groq-llama3-8b: 50 categories)</td>
      <td>NA</td>
      <td>0.78</td>
      <td>0.78</td>
      <td>0.86</td>
      <td>0.8354</td>
      <td>NA</td>
    </tr>
    <tr>
      <!-- LLM Rank Optimizer with expanded categories -->
      <td colspan="7" style="padding: 8px;">
        <div style="margin-bottom: 4px; font-weight: bold;">LLM Rank Optimizer (groq-llama3-8b: 4 categories)</div>
        <table border="1" style="width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 12px; line-height: 1.25;">
          <thead>
            <tr>
              <th style="width: 14%;">Model</th>
              <th style="width: 14%;">Category</th>
              <th style="width: 12%;">NRG</th>
              <th style="width: 12%;">Success@0.1</th>
              <th style="width: 12%;">Promote@0.1</th>
              <th style="width: 12%;">KVR</th>
              <th style="width: 12%;">MRR</th>
              <th style="width: 12%;">PPL-R</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>groq-llama3-8b</td>
              <td>books</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>cameras</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>coffee_machines</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>election_articles</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>0.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td><strong>groq-llama3-8b</strong></td>
              <td><strong>Overall</strong></td>
              <td><strong>NA</strong></td>
              <td><strong>1.00</strong></td>
              <td><strong>1.00</strong></td>
              <td><strong>0.75</strong></td>
              <td><strong>1.0000</strong></td>
              <td><strong>NA</strong></td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
    <tr>
      <!-- LLM Rank with expanded categories -->
      <td colspan="7" style="padding: 8px;">
        <div style="margin-bottom: 4px; font-weight: bold;">LLM Rank(groq-llama3-8b: 7 categories)</div>
        <table border="1" style="width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 12px; line-height: 1.25;">
          <thead>
            <tr>
              <th style="width: 14%;">Model</th>
              <th style="width: 14%;">Category</th>
              <th style="width: 12%;">NRG</th>
              <th style="width: 12%;">Success@0.1</th>
              <th style="width: 12%;">Promote@0.1</th>
              <th style="width: 12%;">KVR</th>
              <th style="width: 12%;">MRR</th>
              <th style="width: 12%;">PPL-R</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>groq-llama3-8b</td>
              <td>computers</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>software</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>0.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>books</td>
              <td>NA</td>
              <td>0.00</td>
              <td>0.00</td>
              <td>1.00</td>
              <td>0.2000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>automotive</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>baby</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>0.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>grocery</td>
              <td>NA</td>
              <td>0.00</td>
              <td>0.00</td>
              <td>1.00</td>
              <td>0.1429</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>appliances</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>0.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td><strong>groq-llama3-8b</strong></td>
              <td><strong>Overall</strong></td>
              <td><strong>NA</strong></td>
              <td><strong>0.71</strong></td>
              <td><strong>0.71</strong></td>
              <td><strong>0.57</strong></td>
              <td><strong>0.7633</strong></td>
              <td><strong>NA</strong></td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
    <tr>
      <!-- AdversarialSEO with expanded categories -->
      <td colspan="7" style="padding: 8px;">
        <div style="margin-bottom: 4px; font-weight: bold;">AdversarialSEO(groq-llama3-8b: 7 categories)</div>
        <table border="1" style="width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 12px; line-height: 1.25;">
          <thead>
            <tr>
              <th style="width: 14%;">Model</th>
              <th style="width: 14%;">Category</th>
              <th style="width: 12%;">NRG</th>
              <th style="width: 12%;">Success@0.1</th>
              <th style="width: 12%;">Promote@0.1</th>
              <th style="width: 12%;">KVR</th>
              <th style="width: 12%;">MRR</th>
              <th style="width: 12%;">PPL-R</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>groq-llama3-8b</td>
              <td>cameras</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>books_and_media</td>
              <td>NA</td>
              <td>0.00</td>
              <td>0.00</td>
              <td>1.00</td>
              <td>0.1250</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>computing_hardware</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>home_furniture</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>kitchen_appliances</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>lenses</td>
              <td>NA</td>
              <td>0.00</td>
              <td>0.00</td>
              <td>1.00</td>
              <td>0.2500</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>accessories</td>
              <td>NA</td>
              <td>0.00</td>
              <td>0.00</td>
              <td>1.00</td>
              <td>0.5000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td><strong>groq-llama3-8b</strong></td>
              <td><strong>Overall</strong></td>
              <td><strong>NA</strong></td>
              <td><strong>0.57</strong></td>
              <td><strong>0.57</strong></td>
              <td><strong>1.00</strong></td>
              <td><strong>0.6964</strong></td>
              <td><strong>NA</strong></td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
    <tr>
      <!-- C-SEO with expanded categories -->
      <td colspan="7" style="padding: 8px;">
        <div style="margin-bottom: 4px; font-weight: bold;">C-SEO(groq-llama3-8b: 6 categories)</div>
        <table border="1" style="width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 12px; line-height: 1.25;">
          <thead>
            <tr>
              <th style="width: 14%;">Model</th>
              <th style="width: 14%;">Category</th>
              <th style="width: 12%;">NRG</th>
              <th style="width: 12%;">Success@0.1</th>
              <th style="width: 12%;">Promote@0.1</th>
              <th style="width: 12%;">KVR</th>
              <th style="width: 12%;">MRR</th>
              <th style="width: 12%;">PPL-R</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>groq-llama3-8b</td>
              <td>books</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>debate</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>news</td>
              <td>NA</td>
              <td>1.00</td>
              <td>0.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>retail</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>videogames</td>
              <td>NA</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.00</td>
              <td>1.0000</td>
              <td>NA</td>
            </tr>
            <tr>
              <td>groq-llama3-8b</td>
              <td>web</td>
              <td>NA</td>
              <td>0.00</td>
              <td>0.00</td>
              <td>1.00</td>
              <td>0.1111</td>
              <td>NA</td>
            </tr>
            <tr>
              <td><strong>groq-llama3-8b</strong></td>
              <td><strong>Overall</strong></td>
              <td><strong>NA</strong></td>
              <td><strong>0.83</strong></td>
              <td><strong>0.67</strong></td>
              <td><strong>1.00</strong></td>
              <td><strong>0.8519</strong></td>
              <td><strong>NA</strong></td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
    <tr>
      <td colspan="7" style="padding: 8px;">
        <div style="margin-bottom: 4px; font-weight: bold;">Ragdoll(groq-llama3-8b: 50 categories)</div>
        <table border="1" style="width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 12px; line-height: 1.25;">
          <thead>
            <tr>
              <th style="width: 14%;">Model</th>
              <th style="width: 14%;">Category</th>
              <th style="width: 12%;">NRG</th>
              <th style="width: 12%;">Success@0.1</th>
              <th style="width: 12%;">Promote@0.1</th>
              <th style="width: 12%;">KVR</th>
              <th style="width: 12%;">MRR</th>
              <th style="width: 12%;">PPL-R</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>groq-llama3-8b</td>
              <td>All categories</td>
              <td>NA</td>
              <td>0.38</td>
              <td>0.38</td>
              <td>0.60</td>
              <td>0.4053</td>
              <td>NA</td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>

  </tbody>
</table>
