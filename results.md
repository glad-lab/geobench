# C-SEO Benchmark - All Datasets Metrics Results

> Comprehensive metrics evaluation across all datasets

## Table of Contents

- [Ragroll](#ragroll)
- [Ragdoll](#ragdoll)
- [STSData](#stsdata)
- [RewriteToRank](#rewritetorank)
- [LLM Rank Optimizer](#llm-rank-optimizer)
- [LLM Rank](#llm-rank)
- [AdversarialSEO](#adversarialseo)
- [C-SEO](#c-seo)
- [Cross-Dataset Comparison](#cross-dataset-method-comparison)

---

*Large-scale product review dataset*

## Ragroll

**Overall Statistics:**
- Total Categories: 53
- Total Samples: 2150
- Model: llama-3.1-8b-instant

<table>
  <thead>
    <tr>
      <th align="left">Method</th>
      <th align="center">Avg ΔRank</th>
      <th align="center">Avg NRG</th>
      <th align="center">Categories</th>
      <th align="center">Success Rate</th>
      <th align="center">Sig. Count</th>
      <th align="center">Total Samples</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Quotes</td>
      <td align="center"><strong>0.9075</strong></td>
      <td align="center">0.1815</td>
      <td align="center">53</td>
      <td align="center">96.23%</td>
      <td align="center">2</td>
      <td align="center">215</td>
    </tr>
    <tr>
      <td>Statistics</td>
      <td align="center"><strong>0.8170</strong></td>
      <td align="center">0.1634</td>
      <td align="center">53</td>
      <td align="center">92.45%</td>
      <td align="center">1</td>
      <td align="center">215</td>
    </tr>
    <tr>
      <td>Authoritative</td>
      <td align="center"><strong>0.6623</strong></td>
      <td align="center">0.1325</td>
      <td align="center">53</td>
      <td align="center">81.13%</td>
      <td align="center">1</td>
      <td align="center">215</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center">0.6245</td>
      <td align="center">0.1249</td>
      <td align="center">53</td>
      <td align="center">73.58%</td>
      <td align="center">1</td>
      <td align="center">215</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center">0.6226</td>
      <td align="center">0.1245</td>
      <td align="center">53</td>
      <td align="center">86.79%</td>
      <td align="center">2</td>
      <td align="center">215</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center">0.5434</td>
      <td align="center">0.1087</td>
      <td align="center">53</td>
      <td align="center">79.25%</td>
      <td align="center">0</td>
      <td align="center">215</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center">0.1491</td>
      <td align="center">0.0298</td>
      <td align="center">53</td>
      <td align="center">49.06%</td>
      <td align="center">0</td>
      <td align="center">215</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">0.0981</td>
      <td align="center">0.0196</td>
      <td align="center">53</td>
      <td align="center">47.17%</td>
      <td align="center">1</td>
      <td align="center">215</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">0.0509</td>
      <td align="center">0.0102</td>
      <td align="center">53</td>
      <td align="center">35.85%</td>
      <td align="center">0</td>
      <td align="center">215</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">53</td>
      <td align="center">41.51%</td>
      <td align="center">0</td>
      <td align="center">215</td>
    </tr>
  </tbody>
</table>

---

*Product review dataset*

## Ragdoll

**Overall Statistics:**
- Total Categories: 18
- Total Samples: 0
- Model: N/A

<table>
  <thead>
    <tr>
      <th align="left">Method</th>
      <th align="center">Avg ΔRank</th>
      <th align="center">Avg NRG</th>
      <th align="center">Categories</th>
      <th align="center">Success Rate</th>
      <th align="center">Sig. Count</th>
      <th align="center">Total Samples</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Authoritative</td>
      <td align="center"><strong>0.0000</strong></td>
      <td align="center">0.0000</td>
      <td align="center">18</td>
      <td align="center">0.00%</td>
      <td align="center">0</td>
      <td align="center">0</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center"><strong>0.0000</strong></td>
      <td align="center">0.0000</td>
      <td align="center">18</td>
      <td align="center">0.00%</td>
      <td align="center">0</td>
      <td align="center">0</td>
    </tr>
    <tr>
      <td>Statistics</td>
      <td align="center"><strong>0.0000</strong></td>
      <td align="center">0.0000</td>
      <td align="center">18</td>
      <td align="center">0.00%</td>
      <td align="center">0</td>
      <td align="center">0</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">18</td>
      <td align="center">0.00%</td>
      <td align="center">0</td>
      <td align="center">0</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">18</td>
      <td align="center">0.00%</td>
      <td align="center">0</td>
      <td align="center">0</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">18</td>
      <td align="center">0.00%</td>
      <td align="center">0</td>
      <td align="center">0</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">18</td>
      <td align="center">0.00%</td>
      <td align="center">0</td>
      <td align="center">0</td>
    </tr>
    <tr>
      <td>Quotes</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">18</td>
      <td align="center">0.00%</td>
      <td align="center">0</td>
      <td align="center">0</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">18</td>
      <td align="center">0.00%</td>
      <td align="center">0</td>
      <td align="center">0</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">18</td>
      <td align="center">0.00%</td>
      <td align="center">0</td>
      <td align="center">0</td>
    </tr>
  </tbody>
</table>

---

*Scientific text dataset*

## STSData

**Overall Statistics:**
- Total Categories: 3
- Total Samples: 15
- Model: llama-3.1-8b-instant

<table>
  <thead>
    <tr>
      <th align="left">Method</th>
      <th align="center">Avg ΔRank</th>
      <th align="center">Avg NRG</th>
      <th align="center">Categories</th>
      <th align="center">Success Rate</th>
      <th align="center">Sig. Count</th>
      <th align="center">Total Samples</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>LLMstxt</td>
      <td align="center"><strong>3.0000</strong></td>
      <td align="center">0.6000</td>
      <td align="center">1</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">1</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center"><strong>3.0000</strong></td>
      <td align="center">0.6000</td>
      <td align="center">1</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">1</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center"><strong>3.0000</strong></td>
      <td align="center">0.6000</td>
      <td align="center">1</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">1</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center">2.5000</td>
      <td align="center">0.5000</td>
      <td align="center">2</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center">2.5000</td>
      <td align="center">0.5000</td>
      <td align="center">2</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td>Quotes</td>
      <td align="center">2.5000</td>
      <td align="center">0.5000</td>
      <td align="center">2</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td>Authoritative</td>
      <td align="center">2.0000</td>
      <td align="center">0.4000</td>
      <td align="center">2</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td>Statistics</td>
      <td align="center">2.0000</td>
      <td align="center">0.4000</td>
      <td align="center">3</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">3</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">1.0000</td>
      <td align="center">0.2000</td>
      <td align="center">1</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">1</td>
    </tr>
  </tbody>
</table>

---

*Text rewriting dataset*

## RewriteToRank

**Overall Statistics:**
- Total Categories: 42
- Total Samples: 16500
- Model: llama-3.1-8b-instant

<table>
  <thead>
    <tr>
      <th align="left">Method</th>
      <th align="center">Avg ΔRank</th>
      <th align="center">Avg NRG</th>
      <th align="center">Categories</th>
      <th align="center">Success Rate</th>
      <th align="center">Sig. Count</th>
      <th align="center">Total Samples</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Statistics</td>
      <td align="center"><strong>0.5690</strong></td>
      <td align="center">0.1138</td>
      <td align="center">42</td>
      <td align="center">100.00%</td>
      <td align="center">41</td>
      <td align="center">1650</td>
    </tr>
    <tr>
      <td>Quotes</td>
      <td align="center"><strong>0.3702</strong></td>
      <td align="center">0.0740</td>
      <td align="center">42</td>
      <td align="center">97.62%</td>
      <td align="center">35</td>
      <td align="center">1650</td>
    </tr>
    <tr>
      <td>Authoritative</td>
      <td align="center"><strong>0.3476</strong></td>
      <td align="center">0.0695</td>
      <td align="center">42</td>
      <td align="center">95.24%</td>
      <td align="center">32</td>
      <td align="center">1650</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center">0.3458</td>
      <td align="center">0.0692</td>
      <td align="center">42</td>
      <td align="center">97.62%</td>
      <td align="center">34</td>
      <td align="center">1650</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center">0.3089</td>
      <td align="center">0.0618</td>
      <td align="center">42</td>
      <td align="center">100.00%</td>
      <td align="center">31</td>
      <td align="center">1650</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center">0.2911</td>
      <td align="center">0.0582</td>
      <td align="center">42</td>
      <td align="center">97.62%</td>
      <td align="center">29</td>
      <td align="center">1650</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">0.1101</td>
      <td align="center">0.0220</td>
      <td align="center">42</td>
      <td align="center">71.43%</td>
      <td align="center">7</td>
      <td align="center">1650</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center">0.1101</td>
      <td align="center">0.0220</td>
      <td align="center">42</td>
      <td align="center">78.57%</td>
      <td align="center">8</td>
      <td align="center">1650</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">0.1095</td>
      <td align="center">0.0219</td>
      <td align="center">42</td>
      <td align="center">73.81%</td>
      <td align="center">4</td>
      <td align="center">1650</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">0.0417</td>
      <td align="center">0.0083</td>
      <td align="center">42</td>
      <td align="center">59.52%</td>
      <td align="center">2</td>
      <td align="center">1650</td>
    </tr>
  </tbody>
</table>

---

*LLM ranking optimization dataset*

## LLM Rank Optimizer

**Overall Statistics:**
- Total Categories: 4
- Total Samples: 29
- Model: llama-3.1-8b-instant

<table>
  <thead>
    <tr>
      <th align="left">Method</th>
      <th align="center">Avg ΔRank</th>
      <th align="center">Avg NRG</th>
      <th align="center">Categories</th>
      <th align="center">Success Rate</th>
      <th align="center">Sig. Count</th>
      <th align="center">Total Samples</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Authoritative</td>
      <td align="center"><strong>1.0000</strong></td>
      <td align="center">0.2000</td>
      <td align="center">2</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center"><strong>1.0000</strong></td>
      <td align="center">0.2000</td>
      <td align="center">3</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">3</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center"><strong>1.0000</strong></td>
      <td align="center">0.2000</td>
      <td align="center">2</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td>Quotes</td>
      <td align="center">1.0000</td>
      <td align="center">0.2000</td>
      <td align="center">2</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td>Statistics</td>
      <td align="center">1.0000</td>
      <td align="center">0.2000</td>
      <td align="center">3</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">3</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center">1.0000</td>
      <td align="center">0.2000</td>
      <td align="center">2</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">0.5000</td>
      <td align="center">0.1000</td>
      <td align="center">4</td>
      <td align="center">75.00%</td>
      <td align="center">0</td>
      <td align="center">4</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">0.0000</td>
      <td align="center">0.0000</td>
      <td align="center">4</td>
      <td align="center">50.00%</td>
      <td align="center">0</td>
      <td align="center">4</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center">-0.2500</td>
      <td align="center">-0.0500</td>
      <td align="center">4</td>
      <td align="center">75.00%</td>
      <td align="center">0</td>
      <td align="center">4</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">-0.3333</td>
      <td align="center">-0.0667</td>
      <td align="center">3</td>
      <td align="center">66.67%</td>
      <td align="center">0</td>
      <td align="center">3</td>
    </tr>
  </tbody>
</table>

---

*LLM ranking dataset*

## LLM Rank

**Overall Statistics:**
- Total Categories: 5
- Total Samples: 32
- Model: llama-3.1-8b-instant

<table>
  <thead>
    <tr>
      <th align="left">Method</th>
      <th align="center">Avg ΔRank</th>
      <th align="center">Avg NRG</th>
      <th align="center">Categories</th>
      <th align="center">Success Rate</th>
      <th align="center">Sig. Count</th>
      <th align="center">Total Samples</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Fluency</td>
      <td align="center"><strong>2.5000</strong></td>
      <td align="center">0.5000</td>
      <td align="center">2</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td>Authoritative</td>
      <td align="center"><strong>2.0000</strong></td>
      <td align="center">0.4000</td>
      <td align="center">4</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">4</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center"><strong>2.0000</strong></td>
      <td align="center">0.4000</td>
      <td align="center">3</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">3</td>
    </tr>
    <tr>
      <td>Quotes</td>
      <td align="center">2.0000</td>
      <td align="center">0.4000</td>
      <td align="center">4</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">4</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center">2.0000</td>
      <td align="center">0.4000</td>
      <td align="center">4</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">4</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center">1.7500</td>
      <td align="center">0.3500</td>
      <td align="center">4</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">4</td>
    </tr>
    <tr>
      <td>Statistics</td>
      <td align="center">1.7500</td>
      <td align="center">0.3500</td>
      <td align="center">4</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">4</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center">1.5000</td>
      <td align="center">0.3000</td>
      <td align="center">2</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">1.5000</td>
      <td align="center">0.3000</td>
      <td align="center">2</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">1.3333</td>
      <td align="center">0.2667</td>
      <td align="center">3</td>
      <td align="center">100.00%</td>
      <td align="center">0</td>
      <td align="center">3</td>
    </tr>
  </tbody>
</table>

---

*Adversarial SEO dataset*

## AdversarialSEO

**Overall Statistics:**
- Total Categories: 7
- Total Samples: 670
- Model: llama-3.1-8b-instant

<table>
  <thead>
    <tr>
      <th align="left">Method</th>
      <th align="center">Avg ΔRank</th>
      <th align="center">Avg NRG</th>
      <th align="center">Categories</th>
      <th align="center">Success Rate</th>
      <th align="center">Sig. Count</th>
      <th align="center">Total Samples</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Quotes</td>
      <td align="center"><strong>0.4405</strong></td>
      <td align="center">0.0881</td>
      <td align="center">7</td>
      <td align="center">85.71%</td>
      <td align="center">1</td>
      <td align="center">67</td>
    </tr>
    <tr>
      <td>Authoritative</td>
      <td align="center"><strong>0.2286</strong></td>
      <td align="center">0.0457</td>
      <td align="center">7</td>
      <td align="center">71.43%</td>
      <td align="center">0</td>
      <td align="center">67</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center"><strong>0.2167</strong></td>
      <td align="center">0.0433</td>
      <td align="center">7</td>
      <td align="center">57.14%</td>
      <td align="center">0</td>
      <td align="center">67</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">0.2000</td>
      <td align="center">0.0400</td>
      <td align="center">7</td>
      <td align="center">71.43%</td>
      <td align="center">0</td>
      <td align="center">67</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center">0.1524</td>
      <td align="center">0.0305</td>
      <td align="center">7</td>
      <td align="center">71.43%</td>
      <td align="center">0</td>
      <td align="center">67</td>
    </tr>
    <tr>
      <td>Statistics</td>
      <td align="center">0.1405</td>
      <td align="center">0.0281</td>
      <td align="center">7</td>
      <td align="center">71.43%</td>
      <td align="center">0</td>
      <td align="center">67</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center">0.0714</td>
      <td align="center">0.0143</td>
      <td align="center">7</td>
      <td align="center">28.57%</td>
      <td align="center">0</td>
      <td align="center">67</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">-0.1071</td>
      <td align="center">-0.0214</td>
      <td align="center">7</td>
      <td align="center">28.57%</td>
      <td align="center">0</td>
      <td align="center">67</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center">-0.1190</td>
      <td align="center">-0.0238</td>
      <td align="center">7</td>
      <td align="center">14.29%</td>
      <td align="center">0</td>
      <td align="center">67</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">-0.1619</td>
      <td align="center">-0.0324</td>
      <td align="center">7</td>
      <td align="center">14.29%</td>
      <td align="center">0</td>
      <td align="center">67</td>
    </tr>
  </tbody>
</table>

---

*Conversational SEO dataset*

## C-SEO

**Overall Statistics:**
- Total Categories: 6
- Total Samples: 3600
- Model: llama-3.1-8b-instant

<table>
  <thead>
    <tr>
      <th align="left">Method</th>
      <th align="center">Avg ΔRank</th>
      <th align="center">Avg NRG</th>
      <th align="center">Categories</th>
      <th align="center">Success Rate</th>
      <th align="center">Sig. Count</th>
      <th align="center">Total Samples</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Quotes</td>
      <td align="center"><strong>0.1500</strong></td>
      <td align="center">0.0300</td>
      <td align="center">6</td>
      <td align="center">83.33%</td>
      <td align="center">2</td>
      <td align="center">360</td>
    </tr>
    <tr>
      <td>Statistics</td>
      <td align="center"><strong>0.1333</strong></td>
      <td align="center">0.0267</td>
      <td align="center">6</td>
      <td align="center">100.00%</td>
      <td align="center">2</td>
      <td align="center">360</td>
    </tr>
    <tr>
      <td>Citations</td>
      <td align="center"><strong>0.1194</strong></td>
      <td align="center">0.0239</td>
      <td align="center">6</td>
      <td align="center">83.33%</td>
      <td align="center">3</td>
      <td align="center">360</td>
    </tr>
    <tr>
      <td>ContentImprovement</td>
      <td align="center">0.1139</td>
      <td align="center">0.0228</td>
      <td align="center">6</td>
      <td align="center">83.33%</td>
      <td align="center">2</td>
      <td align="center">360</td>
    </tr>
    <tr>
      <td>TechnicalTerms</td>
      <td align="center">0.1000</td>
      <td align="center">0.0200</td>
      <td align="center">6</td>
      <td align="center">66.67%</td>
      <td align="center">2</td>
      <td align="center">360</td>
    </tr>
    <tr>
      <td>Authoritative</td>
      <td align="center">0.0611</td>
      <td align="center">0.0122</td>
      <td align="center">6</td>
      <td align="center">66.67%</td>
      <td align="center">1</td>
      <td align="center">360</td>
    </tr>
    <tr>
      <td>UniqueWords</td>
      <td align="center">0.0417</td>
      <td align="center">0.0083</td>
      <td align="center">6</td>
      <td align="center">66.67%</td>
      <td align="center">0</td>
      <td align="center">360</td>
    </tr>
    <tr>
      <td>Fluency</td>
      <td align="center">0.0361</td>
      <td align="center">0.0072</td>
      <td align="center">6</td>
      <td align="center">66.67%</td>
      <td align="center">0</td>
      <td align="center">360</td>
    </tr>
    <tr>
      <td>LLMstxt</td>
      <td align="center">0.0250</td>
      <td align="center">0.0050</td>
      <td align="center">6</td>
      <td align="center">66.67%</td>
      <td align="center">0</td>
      <td align="center">360</td>
    </tr>
    <tr>
      <td>SimpleLanguage</td>
      <td align="center">0.0028</td>
      <td align="center">0.0006</td>
      <td align="center">6</td>
      <td align="center">33.33%</td>
      <td align="center">0</td>
      <td align="center">360</td>
    </tr>
  </tbody>
</table>

---

## 🏆 Cross-Dataset Method Comparison

<table>
  <thead>
    <tr>
      <th align="left">Rank</th>
      <th align="left">Method</th>
      <th align="center">Avg ΔRank (All Datasets)</th>
      <th align="center">Datasets Tested</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🥇 1</td>
      <td><strong>Quotes</strong></td>
      <td align="center"><strong>0.9210</strong></td>
      <td align="center">8</td>
    </tr>
    <tr>
      <td>🥈 2</td>
      <td><strong>ContentImprovement</strong></td>
      <td align="center"><strong>0.8430</strong></td>
      <td align="center">8</td>
    </tr>
    <tr>
      <td>🥉 3</td>
      <td><strong>LLMstxt</strong></td>
      <td align="center"><strong>0.8061</strong></td>
      <td align="center">8</td>
    </tr>
    <tr>
      <td> 4</td>
      <td><strong>Statistics</strong></td>
      <td align="center">0.8012</td>
      <td align="center">8</td>
    </tr>
    <tr>
      <td> 5</td>
      <td><strong>Authoritative</strong></td>
      <td align="center">0.7874</td>
      <td align="center">8</td>
    </tr>
    <tr>
      <td> 6</td>
      <td><strong>TechnicalTerms</strong></td>
      <td align="center">0.7800</td>
      <td align="center">8</td>
    </tr>
    <tr>
      <td> 7</td>
      <td><strong>Citations</strong></td>
      <td align="center">0.6553</td>
      <td align="center">8</td>
    </tr>
    <tr>
      <td> 8</td>
      <td><strong>SimpleLanguage</strong></td>
      <td align="center">0.5270</td>
      <td align="center">8</td>
    </tr>
    <tr>
      <td> 9</td>
      <td><strong>Fluency</strong></td>
      <td align="center">0.4071</td>
      <td align="center">8</td>
    </tr>
    <tr>
      <td> 10</td>
      <td><strong>UniqueWords</strong></td>
      <td align="center">0.3499</td>
      <td align="center">7</td>
    </tr>
  </tbody>
</table>

> **Note:**
> - **ΔRank**: Delta Rank - Average change in ranking position (higher is better)
> - **NRG**: Normalized Ranking Gain
> - **Success Rate**: Percentage of categories with positive ΔRank
> - **Sig. Count**: Number of statistically significant results (p < 0.05)

