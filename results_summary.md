# StealthRank Replication Results

<h2>Original Paper Results (Table 1)</h2>

<table style="border-collapse:collapse; font-variant-numeric: tabular-nums;">
  <thead>
    <tr>
      <th style="padding:6px 10px; text-align:left; border:1px solid #888; border-top:3px solid #000; border-left:3px solid #000;">Dataset</th>
      <th style="padding:6px 10px; text-align:left; border:1px solid #888; border-top:3px solid #000; border-right:3px solid #000;">Model</th>
      <th colspan="3" style="padding:6px 10px; text-align:center; border:1px solid #888; border-top:3px solid #000;">Rank ↓</th>
      <th colspan="3" style="padding:6px 10px; text-align:center; border:1px solid #888; border-top:3px solid #000;">Perplexity ↓</th>
      <th colspan="3" style="padding:6px 10px; text-align:center; border:1px solid #888; border-top:3px solid #000; border-right:3px solid #000;">Bad Word Ratio (Last) ↓</th>
    </tr>
    <tr>
      <th style="padding:6px 10px; border:1px solid #888; border-left:3px solid #000; border-bottom:3px solid #000;"></th>
      <th style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000; border-bottom:3px solid #000;"></th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">SRP</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">TAP</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000; border-right:3px solid #000;">STS</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">SRP</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">TAP</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000; border-right:3px solid #000;">STS</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">SRP</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">TAP</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000; border-right:3px solid #000;">STS</th>
    </tr>
  </thead>
  <tbody>
    <!-- STSData -->
    <tr>
      <td rowspan="4" style="padding:6px 10px; border:1px solid #888; border-left:3px solid #000;"><strong>STSData</strong></td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">deepseek-7b</td>
      <td style="padding:6px 10px; border:1px solid #888;">2.10</td>
      <td style="padding:6px 10px; border:1px solid #888;">2.10</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">4.50</td>
      <td style="padding:6px 10px; border:1px solid #888;">58.04</td>
      <td style="padding:6px 10px; border:1px solid #888;">20.24</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">16712.84</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.20</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.63</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.16</td>
    </tr>
    <tr>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">llama-3.1-8b</td>
      <td style="padding:6px 10px; border:1px solid #888;">1.46</td>
      <td style="padding:6px 10px; border:1px solid #888;">4.00</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">3.50</td>
      <td style="padding:6px 10px; border:1px solid #888;">75.58</td>
      <td style="padding:6px 10px; border:1px solid #888;">35.11</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">2449.29</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.43</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.73</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.03</td>
    </tr>
    <tr>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">mistral-7b</td>
      <td style="padding:6px 10px; border:1px solid #888;">1.46</td>
      <td style="padding:6px 10px; border:1px solid #888;">4.30</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">5.40</td>
      <td style="padding:6px 10px; border:1px solid #888;">109.70</td>
      <td style="padding:6px 10px; border:1px solid #888;">19.97</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">21955.89</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.13</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.60</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.10</td>
    </tr>
    <tr>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">vicuna-7b</td>
      <td style="padding:6px 10px; border:1px solid #888;">2.50</td>
      <td style="padding:6px 10px; border:1px solid #888;">2.40</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">5.80</td>
      <td style="padding:6px 10px; border:1px solid #888;">51.05</td>
      <td style="padding:6px 10px; border:1px solid #888;">14.03</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">142747.13</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.10</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.63</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.30</td>
    </tr>
    <tr>
      <td rowspan="4" style="padding:6px 10px; border:1px solid #888; border-left:3px solid #000; border-top:3px solid #000;"><strong>Ragroll</strong></td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000; border-top:3px solid #000;">deepseek-7b</td>
      <td style="padding:6px 10px; border:1px solid #888; border-top:3px solid #000;">2.15</td>
      <td style="padding:6px 10px; border:1px solid #888; border-top:3px solid #000;">2.44</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000; border-top:3px solid #000;">3.64</td>
      <td style="padding:6px 10px; border:1px solid #888; border-top:3px solid #000;">56.03</td>
      <td style="padding:6px 10px; border:1px solid #888; border-top:3px solid #000;">15.91</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000; border-top:3px solid #000;">10273.82</td>
      <td style="padding:6px 10px; border:1px solid #888; border-top:3px solid #000;">0.29</td>
      <td style="padding:6px 10px; border:1px solid #888; border-top:3px solid #000;">0.67</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000; border-top:3px solid #000;">0.07</td>
    </tr>
    <tr>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">llama-3.1-8b</td>
      <td style="padding:6px 10px; border:1px solid #888;">1.98</td>
      <td style="padding:6px 10px; border:1px solid #888;">2.84</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">5.18</td>
      <td style="padding:6px 10px; border:1px solid #888;">83.95</td>
      <td style="padding:6px 10px; border:1px solid #888;">32.58</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">1725.85</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.48</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.66</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.01</td>
    </tr>
    <tr>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">mistral-7b</td>
      <td style="padding:6px 10px; border:1px solid #888;">1.87</td>
      <td style="padding:6px 10px; border:1px solid #888;">2.07</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">4.29</td>
      <td style="padding:6px 10px; border:1px solid #888;">96.24</td>
      <td style="padding:6px 10px; border:1px solid #888;">12.62</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">15865.91</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.13</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.50</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.04</td>
    </tr>
    <tr>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">vicuna-7b</td>
      <td style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">2.39</td>
      <td style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">2.21</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000; border-bottom:3px solid #000;">4.59</td>
      <td style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">96.42</td>
      <td style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">18.99</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000; border-bottom:3px solid #000;">195939.70</td>
      <td style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">0.15</td>
      <td style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">0.76</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000; border-bottom:3px solid #000;">0.08</td>
    </tr>
  </tbody>
</table>

Only replicated SRP because that's the paper's contribution method, TAP and STS are baselines.
<h2>Replicated Results: STSData (json)</h2>

<table style="border-collapse:collapse; font-variant-numeric: tabular-nums;">
  <thead>
    <tr>
      <th rowspan="2" style="padding:6px 10px; text-align:left; border:1px solid #888; border-top:3px solid #000; border-left:3px solid #000; border-right:3px solid #000;">Model</th>
      <th colspan="3" style="padding:6px 10px; text-align:center; border:1px solid #888; border-top:3px solid #000;">Rank ↓</th>
      <th colspan="3" style="padding:6px 10px; text-align:center; border:1px solid #888; border-top:3px solid #000;">Perplexity ↓</th>
      <th colspan="3" style="padding:6px 10px; text-align:center; border:1px solid #888; border-top:3px solid #000; border-right:3px solid #000;">Bad Word Ratio ↓</th>
    </tr>
    <tr>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">Replicated</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">Paper</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000; border-right:3px solid #000;">Δ</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">Replicated</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">Paper</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000; border-right:3px solid #000;">Δ</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">Replicated</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000;">Paper</th>
      <th style="padding:6px 10px; border:1px solid #888; border-bottom:3px solid #000; border-right:3px solid #000;">Δ</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:6px 10px; border:1px solid #888; border-left:3px solid #000; border-right:3px solid #000;">deepseek-7b</td>
      <td style="padding:6px 10px; border:1px solid #888;">2.29</td>
      <td style="padding:6px 10px; border:1px solid #888;">2.10</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.19</td>
      <td style="padding:6px 10px; border:1px solid #888;">66.95</td>
      <td style="padding:6px 10px; border:1px solid #888;">58.04</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">8.91</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.29</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.20</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.09</td>
    </tr>
    <tr>
      <td style="padding:6px 10px; border:1px solid #888; border-left:3px solid #000; border-right:3px solid #000;">llama-3.1-8b</td>
      <td style="padding:6px 10px; border:1px solid #888;">1.62</td>
      <td style="padding:6px 10px; border:1px solid #888;">1.46</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.16</td>
      <td style="padding:6px 10px; border:1px solid #888;">77.08</td>
      <td style="padding:6px 10px; border:1px solid #888;">75.58</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">1.50</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.54</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.43</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.11</td>
    </tr>
    <tr>
      <td style="padding:6px 10px; border:1px solid #888; border-left:3px solid #000; border-right:3px solid #000;">mistral-7b</td>
      <td style="padding:6px 10px; border:1px solid #888;">1.71</td>
      <td style="padding:6px 10px; border:1px solid #888;">1.46</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.25</td>
      <td style="padding:6px 10px; border:1px solid #888;">113.96</td>
      <td style="padding:6px 10px; border:1px solid #888;">109.70</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">4.26</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.29</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.13</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.16</td>
    </tr>
    <tr>
      <td style="padding:6px 10px; border:1px solid #888; border-left:3px solid #000; border-right:3px solid #000;">vicuna-7b</td>
      <td style="padding:6px 10px; border:1px solid #888;">2.67</td>
      <td style="padding:6px 10px; border:1px solid #888;">2.50</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">0.17</td>
      <td style="padding:6px 10px; border:1px solid #888;">67.18</td>
      <td style="padding:6px 10px; border:1px solid #888;">51.05</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">16.13</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.08</td>
      <td style="padding:6px 10px; border:1px solid #888;">0.10</td>
      <td style="padding:6px 10px; border:1px solid #888; border-right:3px solid #000;">-0.02</td>
    </tr>
  </tbody>
</table>


## Per-Category Breakdown (Replicated)

### Books
| Model | Rank ± Std | Perplexity ± Std | Bad Word ± Std |
|-------|------------|------------------|----------------|
| deepseek-7b | 2.75 ± 2.31 | 40.29 ± 11.72 | 0.12 ± 0.35 |
| llama-3.1-8b | 1.75 ± 1.49 | 81.68 ± 35.97 | 0.75 ± 0.46 |
| mistral-7b | 3.12 ± 3.36 | 95.22 ± 83.45 | 0.25 ± 0.46 |
| vicuna-7b | 4.88 ± 2.90 | 107.49 ± 156.60 | 0.12 ± 0.35 |

### Cameras
| Model | Rank ± Std | Perplexity ± Std | Bad Word ± Std |
|-------|------------|------------------|----------------|
| deepseek-7b | 1.88 ± 2.10 | 82.03 ± 39.56 | 0.50 ± 0.53 |
| llama-3.1-8b | 1.00 ± 0.00 | 77.19 ± 27.82 | 0.38 ± 0.52 |
| mistral-7b | 1.00 ± 0.00 | 110.95 ± 52.19 | 0.38 ± 0.52 |
| vicuna-7b | 1.00 ± 0.00 | 34.35 ± 7.13 | 0.00 ± 0.00 |

### Coffee Machines
| Model | Rank ± Std | Perplexity ± Std | Bad Word ± Std |
|-------|------------|------------------|----------------|
| deepseek-7b | 2.25 ± 2.12 | 78.53 ± 38.67 | 0.25 ± 0.46 |
| llama-3.1-8b | 2.12 ± 1.64 | 72.37 ± 16.03 | 0.50 ± 0.53 |
| mistral-7b | 1.00 ± 0.00 | 135.70 ± 54.56 | 0.25 ± 0.46 |
| vicuna-7b | 2.12 ± 2.23 | 59.71 ± 38.41 | 0.12 ± 0.35 |

---

**Notes:**
- Lower values indicate better performance across all metrics
- Minor differences maybe attributed to random seed variation and hardware differences
