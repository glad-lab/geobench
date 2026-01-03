# C-SEO Benchmark - Comprehensive Metrics Analysis

> Detailed evaluation results across multiple datasets with comprehensive metrics

## Table of Contents

- [AdversarialSEO](#adversarialseo)
- [LLMRank](#llmrank)
- [Ragroll](#ragroll)
- [STSData](#stsdata)
- [llm-rank-optimizer](#llm-rank-optimizer)
- [rewrite to rank](#rewrite-to-rank)
- [Cross-Dataset Comparison](#cross-dataset-comparison)
- [Metrics Explanation](#metrics-explanation)


---

## Metrics Explanation

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| **Delta-Rank (ΔRank)** | Average change in ranking position | Higher is better. Positive values indicate ranking improvement |
| **NRG** | Normalized Ranking Gain (ΔRank/cohort_size) | Range: 0-1, higher is better |
| **Success@0.1** | Percentage of cases achieving ΔRank ≥ 0.1 | Indicates consistency of small improvements |
| **Success@0.2** | Percentage of cases achieving ΔRank ≥ 0.2 | Indicates consistency of moderate improvements |
| **Promote@0.1** | Percentage of cases promoted by ≥ 0.1 positions | Similar to Success@0.1 |
| **KVR** | K-Value Ratio - ratio of top-K results | Indicates robustness |
| **MRR** | Mean Reciprocal Rank | Range: 0-1, higher is better |
| **P-value** | Statistical significance indicator | Lower is better (p < 0.05 = significant) |

> **Note:** ↑ indicates "higher is better", ↓ indicates "lower is better"

---


## AdversarialSEO

**Dataset Statistics:**
- Total Categories: 7
- Total Samples: 70

### Method Performance Overview

| Method | Delta-Rank ↑ | NRG ↑ | Success@0.1 ↑ | Success@0.2 ↑ | Promote@0.1 ↑ | KVR ↑ | MRR ↑ | P-value ↓ | Categories | Samples |
|--------|--------------|-------|----------------|----------------|----------------|-------|-------|-----------|------------|---------|
| **Quotes** | 0.4405 | 0.0881 | 85.7% | 85.7% | 85.7% | 0.4286 | 0.3704 | 0.3158 | 7 | 7 |
| **Authoritative** | 0.2286 | 0.0457 | 71.4% | 71.4% | 71.4% | 0.4286 | 0.3704 | 0.4479 | 7 | 7 |
| **ContentImprovement** | 0.2167 | 0.0433 | 57.1% | 57.1% | 57.1% | 0.4286 | 0.3704 | 0.5596 | 7 | 7 |
| UniqueWords | 0.2000 | 0.0400 | 71.4% | 42.9% | 71.4% | 0.4286 | 0.3704 | 0.4929 | 7 | 7 |
| Citations | 0.1524 | 0.0305 | 71.4% | 42.9% | 71.4% | 0.4286 | 0.3704 | 0.5070 | 7 | 7 |
| Statistics | 0.1405 | 0.0281 | 71.4% | 42.9% | 71.4% | 0.4286 | 0.3704 | 0.5038 | 7 | 7 |
| LLMstxt | 0.0714 | 0.0143 | 28.6% | 14.3% | 28.6% | 0.4286 | 0.3704 | 0.6659 | 7 | 7 |
| Fluency | -0.1071 | -0.0214 | 14.3% | 0.0% | 14.3% | 0.4286 | 0.3704 | 0.7989 | 7 | 7 |
| TechnicalTerms | -0.1190 | -0.0238 | 14.3% | 14.3% | 14.3% | 0.4286 | 0.3704 | 0.7328 | 7 | 7 |
| SimpleLanguage | -0.1619 | -0.0324 | 14.3% | 14.3% | 14.3% | 0.4286 | 0.3704 | 0.7686 | 7 | 7 |

### Category-Level Breakdown

<details>
<summary>Click to expand category details</summary>

| Category | Method | Delta-Rank | NRG | P-value | Samples |
|----------|--------|------------|-----|---------|---------|
| accessories | Quotes | 0.3333 | 0.0667 | 0.5000 | 3 |
| accessories | Statistics | 0.3333 | 0.0667 | 0.5000 | 3 |
| accessories | Authoritative | 0.0000 | 0.0000 | 1.0000 | 3 |
| accessories | Fluency | 0.0000 | 0.0000 | 1.0000 | 3 |
| accessories | LLMstxt | 0.0000 | 0.0000 | 1.0000 | 3 |
| accessories | UniqueWords | 0.0000 | 0.0000 | 1.0000 | 3 |
| accessories | Citations | -0.3333 | -0.0667 | 1.0000 | 3 |
| accessories | ContentImprovement | -0.3333 | -0.0667 | 1.0000 | 3 |
| accessories | SimpleLanguage | -0.3333 | -0.0667 | 1.0000 | 3 |
| accessories | TechnicalTerms | -0.3333 | -0.0667 | 1.0000 | 3 |
| books_and_media | Quotes | 0.6000 | 0.1200 | 0.2500 | 10 |
| books_and_media | Authoritative | 0.5000 | 0.1000 | 0.3750 | 10 |
| books_and_media | ContentImprovement | 0.5000 | 0.1000 | 0.5000 | 10 |
| books_and_media | UniqueWords | 0.5000 | 0.1000 | 0.3750 | 10 |
| books_and_media | TechnicalTerms | 0.2000 | 0.0400 | 0.5000 | 10 |
| books_and_media | Statistics | 0.1000 | 0.0200 | 0.5000 | 10 |
| books_and_media | Citations | 0.0000 | 0.0000 | 0.6875 | 10 |
| books_and_media | LLMstxt | -0.2000 | -0.0400 | 0.8438 | 10 |
| books_and_media | Fluency | -0.3000 | -0.0600 | 1.0000 | 10 |
| books_and_media | SimpleLanguage | -0.3000 | -0.0600 | 1.0000 | 10 |
| cameras | Authoritative | 0.5000 | 0.1000 | 0.0625 | 10 |
| cameras | SimpleLanguage | 0.3000 | 0.0600 | 0.2656 | 10 |
| cameras | Quotes | 0.2000 | 0.0400 | 0.3125 | 10 |
| cameras | Citations | 0.1000 | 0.0200 | 0.5000 | 10 |
| cameras | LLMstxt | 0.0000 | 0.0000 | 0.7500 | 10 |
| cameras | Statistics | 0.0000 | 0.0000 | 0.6875 | 10 |
| cameras | TechnicalTerms | 0.0000 | 0.0000 | 0.6250 | 10 |
| cameras | UniqueWords | 0.0000 | 0.0000 | 0.3906 | 10 |
| cameras | ContentImprovement | -0.1000 | -0.0200 | 1.0000 | 10 |
| cameras | Fluency | -0.1000 | -0.0200 | 1.0000 | 10 |
| computing_hardware | Quotes | 0.7500 | 0.1500 | 0.0233 | 20 |
| computing_hardware | ContentImprovement | 0.6000 | 0.1200 | 0.1046 | 20 |
| computing_hardware | Citations | 0.5000 | 0.1000 | 0.1116 | 20 |
| computing_hardware | UniqueWords | 0.4500 | 0.0900 | 0.1848 | 20 |
| computing_hardware | Authoritative | 0.3500 | 0.0700 | 0.2135 | 20 |
| computing_hardware | Fluency | 0.0500 | 0.0100 | 0.4676 | 20 |
| computing_hardware | TechnicalTerms | -0.1000 | -0.0200 | 0.8171 | 20 |
| computing_hardware | LLMstxt | -0.1500 | -0.0300 | 0.6928 | 20 |
| computing_hardware | SimpleLanguage | -0.3000 | -0.0600 | 0.7476 | 20 |
| computing_hardware | Statistics | -0.4000 | -0.0800 | 0.7455 | 20 |
| home_furniture | Quotes | 0.2000 | 0.0400 | 0.2500 | 10 |
| home_furniture | Citations | 0.1000 | 0.0200 | 0.5000 | 10 |
| home_furniture | Fluency | 0.1000 | 0.0200 | 0.5000 | 10 |
| home_furniture | Statistics | 0.1000 | 0.0200 | 0.5000 | 10 |
| home_furniture | UniqueWords | 0.1000 | 0.0200 | 0.5000 | 10 |
| home_furniture | ContentImprovement | 0.0000 | 0.0000 | 0.7500 | 10 |
| home_furniture | LLMstxt | 0.0000 | 0.0000 | 0.7500 | 10 |
| home_furniture | SimpleLanguage | 0.0000 | 0.0000 | 1.0000 | 10 |
| home_furniture | TechnicalTerms | -0.1000 | -0.0200 | 0.7500 | 10 |
| home_furniture | Authoritative | -0.3000 | -0.0600 | 0.7344 | 10 |
| kitchen_appliances | ContentImprovement | 0.6000 | 0.1200 | 0.0625 | 10 |
| kitchen_appliances | Statistics | 0.6000 | 0.1200 | 0.0938 | 10 |
| kitchen_appliances | Authoritative | 0.3000 | 0.0600 | 0.2500 | 10 |
| kitchen_appliances | Citations | 0.2000 | 0.0400 | 0.5000 | 10 |
| kitchen_appliances | LLMstxt | 0.1000 | 0.0200 | 0.5000 | 10 |
| kitchen_appliances | UniqueWords | 0.1000 | 0.0200 | 0.5000 | 10 |
| kitchen_appliances | Fluency | 0.0000 | 0.0000 | 0.7500 | 10 |
| kitchen_appliances | Quotes | 0.0000 | 0.0000 | 0.7500 | 10 |
| kitchen_appliances | SimpleLanguage | 0.0000 | 0.0000 | 0.6172 | 10 |
| kitchen_appliances | TechnicalTerms | 0.0000 | 0.0000 | 0.6875 | 10 |
| lenses | Quotes | 1.0000 | 0.2000 | 0.1250 | 4 |
| lenses | LLMstxt | 0.7500 | 0.1500 | 0.1250 | 4 |
| lenses | Citations | 0.5000 | 0.1000 | 0.2500 | 4 |
| lenses | Authoritative | 0.2500 | 0.0500 | 0.5000 | 4 |
| lenses | ContentImprovement | 0.2500 | 0.0500 | 0.5000 | 4 |
| lenses | Statistics | 0.2500 | 0.0500 | 0.5000 | 4 |
| lenses | UniqueWords | 0.2500 | 0.0500 | 0.5000 | 4 |
| lenses | Fluency | -0.5000 | -0.1000 | 0.8750 | 4 |
| lenses | SimpleLanguage | -0.5000 | -0.1000 | 0.7500 | 4 |
| lenses | TechnicalTerms | -0.5000 | -0.1000 | 0.7500 | 4 |

</details>

---

## LLMRank

**Dataset Statistics:**
- Total Categories: 5
- Total Samples: 32

### Method Performance Overview

| Method | Delta-Rank ↑ | NRG ↑ | Success@0.1 ↑ | Success@0.2 ↑ | Promote@0.1 ↑ | KVR ↑ | MRR ↑ | P-value ↓ | Categories | Samples |
|--------|--------------|-------|----------------|----------------|----------------|-------|-------|-----------|------------|---------|
| **Fluency** | 2.5000 | 0.5000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.7500 | 0.5000 | 2 | 2 |
| **Authoritative** | 2.0000 | 0.4000 | 100.0% | 100.0% | 100.0% | 0.7500 | 0.5208 | 0.5000 | 4 | 4 |
| **ContentImprovement** | 2.0000 | 0.4000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.6111 | 0.5000 | 3 | 3 |
| Quotes | 2.0000 | 0.4000 | 100.0% | 100.0% | 100.0% | 0.7500 | 0.5208 | 0.5000 | 4 | 4 |
| TechnicalTerms | 2.0000 | 0.4000 | 100.0% | 100.0% | 100.0% | 0.7500 | 0.5208 | 0.5000 | 4 | 4 |
| Citations | 1.7500 | 0.3500 | 100.0% | 100.0% | 100.0% | 0.7500 | 0.5208 | 0.5000 | 4 | 4 |
| Statistics | 1.7500 | 0.3500 | 100.0% | 100.0% | 100.0% | 0.7500 | 0.5208 | 0.5000 | 4 | 4 |
| LLMstxt | 1.5000 | 0.3000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.7500 | 0.5000 | 2 | 2 |
| UniqueWords | 1.5000 | 0.3000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.7500 | 0.5000 | 2 | 2 |
| SimpleLanguage | 1.3333 | 0.2667 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.6111 | 0.5000 | 3 | 3 |

### Category-Level Breakdown

<details>
<summary>Click to expand category details</summary>

| Category | Method | Delta-Rank | NRG | P-value | Samples |
|----------|--------|------------|-----|---------|---------|
| automotive | Authoritative | 1.0000 | 0.2000 | 0.5000 | 1 |
| automotive | Citations | 1.0000 | 0.2000 | 0.5000 | 1 |
| automotive | ContentImprovement | 1.0000 | 0.2000 | 0.5000 | 1 |
| automotive | LLMstxt | 1.0000 | 0.2000 | 0.5000 | 1 |
| automotive | Quotes | 1.0000 | 0.2000 | 0.5000 | 1 |
| automotive | SimpleLanguage | 1.0000 | 0.2000 | 0.5000 | 1 |
| automotive | Statistics | 1.0000 | 0.2000 | 0.5000 | 1 |
| automotive | TechnicalTerms | 1.0000 | 0.2000 | 0.5000 | 1 |
| baby | Authoritative | 2.0000 | 0.4000 | 0.5000 | 1 |
| baby | Citations | 2.0000 | 0.4000 | 0.5000 | 1 |
| baby | LLMstxt | 2.0000 | 0.4000 | 0.5000 | 1 |
| baby | Quotes | 2.0000 | 0.4000 | 0.5000 | 1 |
| baby | Statistics | 2.0000 | 0.4000 | 0.5000 | 1 |
| baby | TechnicalTerms | 2.0000 | 0.4000 | 0.5000 | 1 |
| baby | UniqueWords | 2.0000 | 0.4000 | 0.5000 | 1 |
| books | Authoritative | 2.0000 | 0.4000 | 0.5000 | 1 |
| books | ContentImprovement | 2.0000 | 0.4000 | 0.5000 | 1 |
| books | Fluency | 2.0000 | 0.4000 | 0.5000 | 1 |
| books | Statistics | 2.0000 | 0.4000 | 0.5000 | 1 |
| books | SimpleLanguage | 1.0000 | 0.2000 | 0.5000 | 1 |
| computers | Authoritative | 3.0000 | 0.6000 | 0.5000 | 1 |
| computers | Citations | 3.0000 | 0.6000 | 0.5000 | 1 |
| computers | ContentImprovement | 3.0000 | 0.6000 | 0.5000 | 1 |
| computers | Fluency | 3.0000 | 0.6000 | 0.5000 | 1 |
| computers | Quotes | 3.0000 | 0.6000 | 0.5000 | 1 |
| computers | TechnicalTerms | 3.0000 | 0.6000 | 0.5000 | 1 |
| software | Quotes | 2.0000 | 0.4000 | 0.5000 | 1 |
| software | SimpleLanguage | 2.0000 | 0.4000 | 0.5000 | 1 |
| software | Statistics | 2.0000 | 0.4000 | 0.5000 | 1 |
| software | TechnicalTerms | 2.0000 | 0.4000 | 0.5000 | 1 |
| software | Citations | 1.0000 | 0.2000 | 0.5000 | 1 |
| software | UniqueWords | 1.0000 | 0.2000 | 0.5000 | 1 |

</details>

---

## Ragroll

**Dataset Statistics:**
- Total Categories: 53
- Total Samples: 530

### Method Performance Overview

| Method | Delta-Rank ↑ | NRG ↑ | Success@0.1 ↑ | Success@0.2 ↑ | Promote@0.1 ↑ | KVR ↑ | MRR ↑ | P-value ↓ | Categories | Samples |
|--------|--------------|-------|----------------|----------------|----------------|-------|-------|-----------|------------|---------|
| **Quotes** | 0.9075 | 0.1815 | 96.2% | 96.2% | 96.2% | 0.0566 | 0.0860 | 0.2182 | 53 | 53 |
| **Statistics** | 0.8170 | 0.1634 | 92.5% | 92.5% | 92.5% | 0.0566 | 0.0860 | 0.2412 | 53 | 53 |
| **Authoritative** | 0.6623 | 0.1325 | 81.1% | 81.1% | 81.1% | 0.0566 | 0.0860 | 0.3485 | 53 | 53 |
| Citations | 0.6245 | 0.1249 | 73.6% | 73.6% | 73.6% | 0.0566 | 0.0860 | 0.3909 | 53 | 53 |
| ContentImprovement | 0.6226 | 0.1245 | 86.8% | 86.8% | 86.8% | 0.0566 | 0.0860 | 0.3726 | 53 | 53 |
| LLMstxt | 0.5434 | 0.1087 | 79.2% | 79.2% | 79.2% | 0.0566 | 0.0860 | 0.4163 | 53 | 53 |
| TechnicalTerms | 0.1491 | 0.0298 | 49.1% | 49.1% | 49.1% | 0.0566 | 0.0860 | 0.6474 | 53 | 53 |
| UniqueWords | 0.0981 | 0.0196 | 47.2% | 47.2% | 47.2% | 0.0566 | 0.0860 | 0.6445 | 53 | 53 |
| Fluency | 0.0509 | 0.0102 | 35.8% | 35.8% | 35.8% | 0.0566 | 0.0860 | 0.7075 | 53 | 53 |
| SimpleLanguage | 0.0000 | 0.0000 | 41.5% | 41.5% | 41.5% | 0.0566 | 0.0860 | 0.7064 | 53 | 53 |

---

## STSData

**Dataset Statistics:**
- Total Categories: 3
- Total Samples: 15

### Method Performance Overview

| Method | Delta-Rank ↑ | NRG ↑ | Success@0.1 ↑ | Success@0.2 ↑ | Promote@0.1 ↑ | KVR ↑ | MRR ↑ | P-value ↓ | Categories | Samples |
|--------|--------------|-------|----------------|----------------|----------------|-------|-------|-----------|------------|---------|
| **LLMstxt** | 3.0000 | 0.6000 | 100.0% | 100.0% | 100.0% | 1.0000 | 1.0000 | 0.5000 | 1 | 1 |
| **SimpleLanguage** | 3.0000 | 0.6000 | 100.0% | 100.0% | 100.0% | 1.0000 | 1.0000 | 0.5000 | 1 | 1 |
| **TechnicalTerms** | 3.0000 | 0.6000 | 100.0% | 100.0% | 100.0% | 1.0000 | 1.0000 | 0.5000 | 1 | 1 |
| Citations | 2.5000 | 0.5000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.7500 | 0.5000 | 2 | 2 |
| ContentImprovement | 2.5000 | 0.5000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.7500 | 0.5000 | 2 | 2 |
| Quotes | 2.5000 | 0.5000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.7500 | 0.5000 | 2 | 2 |
| Authoritative | 2.0000 | 0.4000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.7500 | 0.5000 | 2 | 2 |
| Statistics | 2.0000 | 0.4000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.6111 | 0.5000 | 3 | 3 |
| Fluency | 1.0000 | 0.2000 | 100.0% | 100.0% | 100.0% | 1.0000 | 1.0000 | 0.5000 | 1 | 1 |

### Category-Level Breakdown

<details>
<summary>Click to expand category details</summary>

| Category | Method | Delta-Rank | NRG | P-value | Samples |
|----------|--------|------------|-----|---------|---------|
| books | Authoritative | 3.0000 | 0.6000 | 0.5000 | 1 |
| books | Citations | 3.0000 | 0.6000 | 0.5000 | 1 |
| books | ContentImprovement | 3.0000 | 0.6000 | 0.5000 | 1 |
| books | LLMstxt | 3.0000 | 0.6000 | 0.5000 | 1 |
| books | Quotes | 3.0000 | 0.6000 | 0.5000 | 1 |
| books | SimpleLanguage | 3.0000 | 0.6000 | 0.5000 | 1 |
| books | Statistics | 3.0000 | 0.6000 | 0.5000 | 1 |
| books | TechnicalTerms | 3.0000 | 0.6000 | 0.5000 | 1 |
| cameras | Authoritative | 1.0000 | 0.2000 | 0.5000 | 1 |
| cameras | Statistics | 1.0000 | 0.2000 | 0.5000 | 1 |
| coffee_machines | Citations | 2.0000 | 0.4000 | 0.5000 | 1 |
| coffee_machines | ContentImprovement | 2.0000 | 0.4000 | 0.5000 | 1 |
| coffee_machines | Quotes | 2.0000 | 0.4000 | 0.5000 | 1 |
| coffee_machines | Statistics | 2.0000 | 0.4000 | 0.5000 | 1 |
| coffee_machines | Fluency | 1.0000 | 0.2000 | 0.5000 | 1 |

</details>

---

## llm-rank-optimizer

**Dataset Statistics:**
- Total Categories: 4
- Total Samples: 29

### Method Performance Overview

| Method | Delta-Rank ↑ | NRG ↑ | Success@0.1 ↑ | Success@0.2 ↑ | Promote@0.1 ↑ | KVR ↑ | MRR ↑ | P-value ↓ | Categories | Samples |
|--------|--------------|-------|----------------|----------------|----------------|-------|-------|-----------|------------|---------|
| **Authoritative** | 1.0000 | 0.2000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.7500 | 0.5000 | 2 | 2 |
| **ContentImprovement** | 1.0000 | 0.2000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.6111 | 0.5000 | 3 | 3 |
| **LLMstxt** | 1.0000 | 0.2000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.7500 | 0.5000 | 2 | 2 |
| Quotes | 1.0000 | 0.2000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.7500 | 0.5000 | 2 | 2 |
| Statistics | 1.0000 | 0.2000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.6111 | 0.5000 | 3 | 3 |
| TechnicalTerms | 1.0000 | 0.2000 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.7500 | 0.5000 | 2 | 2 |
| UniqueWords | 0.5000 | 0.1000 | 75.0% | 75.0% | 75.0% | 0.7500 | 0.5208 | 0.6250 | 4 | 4 |
| SimpleLanguage | 0.0000 | 0.0000 | 50.0% | 50.0% | 50.0% | 0.7500 | 0.5208 | 0.7500 | 4 | 4 |
| Citations | -0.2500 | -0.0500 | 75.0% | 75.0% | 75.0% | 0.7500 | 0.5208 | 0.6250 | 4 | 4 |
| Fluency | -0.3333 | -0.0667 | 66.7% | 66.7% | 66.7% | 1.0000 | 0.6111 | 0.6667 | 3 | 3 |

### Category-Level Breakdown

<details>
<summary>Click to expand category details</summary>

| Category | Method | Delta-Rank | NRG | P-value | Samples |
|----------|--------|------------|-----|---------|---------|
| books | Authoritative | 1.0000 | 0.2000 | 0.5000 | 1 |
| books | Citations | 1.0000 | 0.2000 | 0.5000 | 1 |
| books | ContentImprovement | 1.0000 | 0.2000 | 0.5000 | 1 |
| books | Fluency | 1.0000 | 0.2000 | 0.5000 | 1 |
| books | LLMstxt | 1.0000 | 0.2000 | 0.5000 | 1 |
| books | Quotes | 1.0000 | 0.2000 | 0.5000 | 1 |
| books | SimpleLanguage | 1.0000 | 0.2000 | 0.5000 | 1 |
| books | Statistics | 1.0000 | 0.2000 | 0.5000 | 1 |
| books | TechnicalTerms | 1.0000 | 0.2000 | 0.5000 | 1 |
| books | UniqueWords | 1.0000 | 0.2000 | 0.5000 | 1 |
| cameras | SimpleLanguage | -1.0000 | -0.2000 | 1.0000 | 1 |
| cameras | UniqueWords | -1.0000 | -0.2000 | 1.0000 | 1 |
| cameras | Fluency | -3.0000 | -0.6000 | 1.0000 | 1 |
| cameras | Citations | -4.0000 | -0.8000 | 1.0000 | 1 |
| coffee_machines | Citations | 1.0000 | 0.2000 | 0.5000 | 1 |
| coffee_machines | ContentImprovement | 1.0000 | 0.2000 | 0.5000 | 1 |
| coffee_machines | LLMstxt | 1.0000 | 0.2000 | 0.5000 | 1 |
| coffee_machines | Statistics | 1.0000 | 0.2000 | 0.5000 | 1 |
| coffee_machines | UniqueWords | 1.0000 | 0.2000 | 0.5000 | 1 |
| coffee_machines | SimpleLanguage | -1.0000 | -0.2000 | 1.0000 | 1 |
| election_articles | Authoritative | 1.0000 | 0.2000 | 0.5000 | 1 |
| election_articles | Citations | 1.0000 | 0.2000 | 0.5000 | 1 |
| election_articles | ContentImprovement | 1.0000 | 0.2000 | 0.5000 | 1 |
| election_articles | Fluency | 1.0000 | 0.2000 | 0.5000 | 1 |
| election_articles | Quotes | 1.0000 | 0.2000 | 0.5000 | 1 |
| election_articles | SimpleLanguage | 1.0000 | 0.2000 | 0.5000 | 1 |
| election_articles | Statistics | 1.0000 | 0.2000 | 0.5000 | 1 |
| election_articles | TechnicalTerms | 1.0000 | 0.2000 | 0.5000 | 1 |
| election_articles | UniqueWords | 1.0000 | 0.2000 | 0.5000 | 1 |

</details>

---

## rewrite to rank

**Dataset Statistics:**
- Total Categories: 42
- Total Samples: 420

### Method Performance Overview

| Method | Delta-Rank ↑ | NRG ↑ | Success@0.1 ↑ | Success@0.2 ↑ | Promote@0.1 ↑ | KVR ↑ | MRR ↑ | P-value ↓ | Categories | Samples |
|--------|--------------|-------|----------------|----------------|----------------|-------|-------|-----------|------------|---------|
| **Statistics** | 0.5690 | 0.1138 | 100.0% | 100.0% | 100.0% | 0.0714 | 0.1030 | 0.0042 | 42 | 42 |
| **Quotes** | 0.3702 | 0.0740 | 95.2% | 88.1% | 95.2% | 0.0714 | 0.1030 | 0.0462 | 42 | 42 |
| **Authoritative** | 0.3476 | 0.0695 | 90.5% | 83.3% | 90.5% | 0.0714 | 0.1030 | 0.0556 | 42 | 42 |
| Citations | 0.3458 | 0.0692 | 95.2% | 83.3% | 95.2% | 0.0714 | 0.1030 | 0.0422 | 42 | 42 |
| LLMstxt | 0.3089 | 0.0618 | 92.9% | 81.0% | 92.9% | 0.0714 | 0.1030 | 0.0603 | 42 | 42 |
| ContentImprovement | 0.2911 | 0.0582 | 92.9% | 73.8% | 92.9% | 0.0714 | 0.1030 | 0.0756 | 42 | 42 |
| Fluency | 0.1101 | 0.0220 | 47.6% | 33.3% | 47.6% | 0.0714 | 0.1030 | 0.3016 | 42 | 42 |
| TechnicalTerms | 0.1101 | 0.0220 | 54.8% | 26.2% | 54.8% | 0.0714 | 0.1030 | 0.2879 | 42 | 42 |
| UniqueWords | 0.1095 | 0.0219 | 50.0% | 26.2% | 50.0% | 0.0714 | 0.1030 | 0.2803 | 42 | 42 |
| SimpleLanguage | 0.0417 | 0.0083 | 28.6% | 11.9% | 28.6% | 0.0714 | 0.1030 | 0.4086 | 42 | 42 |

---

## Cross-Dataset Comparison

Average performance of each method across all datasets.

| Rank | Method | Avg Delta-Rank | Avg NRG | Datasets Tested |
|------|--------|----------------|---------|-----------------|
| 🥇 1 | **Quotes** | 1.2030 | 0.2406 | 6 |
| 🥈 2 | **ContentImprovement** | 1.1051 | 0.2210 | 6 |
| 🥉 3 | **LLMstxt** | 1.0706 | 0.2141 | 6 |
|  4 | Statistics | 1.0461 | 0.2092 | 6 |
|  5 | Authoritative | 1.0397 | 0.2079 | 6 |
|  6 | TechnicalTerms | 1.0234 | 0.2047 | 6 |
|  7 | Citations | 0.8538 | 0.1708 | 6 |
|  8 | SimpleLanguage | 0.7022 | 0.1404 | 6 |
|  9 | Fluency | 0.5368 | 0.1074 | 6 |
|  10 | UniqueWords | 0.4815 | 0.0963 | 5 |


---

## Summary

- **Total Datasets Analyzed:** 6
- **Total Methods Evaluated:** 10
- **Total Categories:** 114
- **Total Samples:** 1096


---

*Generated automatically from benchmark results*
