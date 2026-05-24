## Project & Local Experiment Overview

This repository is used to reproduce experiments on GEO / StealthRank and related ranking datasets, and to apply **adversarial rank optimization** on LLM-generated recommendations using the GCG (Greedy Coordinate Gradient) method.  
The current local experiments are mainly run on `datasets_5` (a small, filtered subset), and all results are written into the unified directory `results_datasets_5`.

This document is an **intermediate summary**: not all datasets and products have finished running yet, but several categories under `StealthRank` already have reasonably complete curves (`rank.png`) and logs, so we summarize the partial results here and will refine later.

---

## Directory Layout Relevant to This Experiment

- `datasets_5/`  
  - Filtered product datasets for each algorithm, with **≤ 5 categories per algorithm and ≤ 6 products per category**.  
  - In this round we mainly use:
    - `StealthRank/air_compressor.jsonl`
    - `StealthRank/air_purifier.jsonl`
    - `StealthRank/automatic_garden_watering_system.jsonl`

- `iterate_datasets_5.sh`  
  - Main traversal script (sequential execution to avoid OOM). Current logic:
    - Algorithm order: `StealthRank → llm-rank-optimizer → AdversarialSEO → GEO`, skipping `RewriteToRank`
    - For each category file:
      - First check whether in the result directory this category already has **≥ 3 target products with `done.txt`**; if so, skip the whole category
      - Otherwise only take the **first 3 products** as targets and run them sequentially
    - All outputs are written into the fixed directory `results_datasets_5`

- `run_iterate_datasets_5.sh`  
  - Wrapper script that launches `iterate_datasets_5.sh` via `nohup` in the background, managing PID and the log `run_iterate_datasets_5.log`.

- `rank_opt.py`  
  - Core rank optimization script:
    - Supports `--catalog` pointing to arbitrary `data/{catalog}.jsonl`
    - Uses `--target_product_idx` to specify the current target product
    - Runs GCG optimization and outputs:
      - `rank.png`: rank trajectory of the target product over iterations
      - `loss.png`: loss curve
      - `rank_opt_background.log`: detailed log
      - `state_dict.pth`: checkpoint for resuming experiments
    - Key hyperparameters (current version):
      - `num_iter = 1600`
      - `batch_size = 120`
      - `num_samples = 256`
      - `max_length = 4096`
      - `repetition_penalty = 1.2`
    - Model configuration:
      - Mode: `self`
      - Target LLM: `llama` (`/media/volume/v4/Llama-2-7b-chat-hf`)

- `results_datasets_5/`  
  - Unified local result directory (including migrated historical results), with the structure:

  ```text
  results_datasets_5/
    StealthRank/
      air_compressor/
        self/llama/default/product{1..3}/run1/
          rank.png
          loss.png
          rank_opt_background.log
          state_dict.pth
          done.txt
      air_purifier/
      automatic_garden_watering_system/
    ...
  ```

---

## Experimental Setup (This Round)

### Model & Mode

- Model: Llama-2-7b-chat-hf (referred to as `llama`)
- Mode: `self` (optimize only against this single model)
- Device: single A100 40GB, `CUDA_VISIBLE_DEVICES=0`

### GCG Hyperparameters (in `rank_opt.py`)

- `num_iter = 1600`: up to 1600 optimization steps per target product  
- `batch_size = 120`: relatively large batch to saturate GPU memory  
- `num_samples = 256`: 256 adversarial sequences sampled per iteration  
- Evaluation interval: `test_iter = 50`  
- Generation-related:
  - Context limit: `max_length = 4096`
  - Repetition control: `repetition_penalty = 1.2`

### Prompt Constraints (Already Implemented)

The system prompt explicitly enforces:

- The assistant **must include all products** that appear in the product list, without omission
- Each product must appear **exactly once** in the numbered recommendations
- When mentioning products, the assistant must ensure that the product **names exactly match** those given in the list

---

## Observations from Partial Results (StealthRank)

So far, completed results are mainly concentrated in:

- `results_datasets_5/StealthRank/air_compressor/self/llama/default/product{1..3}/run1`
- `results_datasets_5/StealthRank/air_purifier/self/llama/default/product{1..3}/run1`
- `results_datasets_5/StealthRank/automatic_garden_watering_system/self/llama/default/product{1..3}/run1`

The main signal is in `rank.png` plus the log entries for **Target Product Rank**, so we summarize qualitatively based on these.

### 1. Overall Rank Improvement

- **General trend**:  
  - For most target products, the initial rank is in the **middle-to-tail** of the list (e.g., 5–7);  
  - After ~1600 GCG steps, the **final evaluated Target Product Rank typically improves to top-1 to top-3**;  
  - In several runs, `Best top count` in the logs indicates the target product hit **rank = 1** multiple times, even if the final evaluation settles at rank 2.

- **Example: `StealthRank/air_compressor`, product5**  
  - Initial evaluation:
    - `Target Product Rank: 7` (last among 6 candidates, because one is effectively ignored in ranking)  
  - Later evaluation in the same run:
    - `Target Product Rank: 2`, with `Top count: 1, Best top count: 2`  
  - This suggests the target product reached the top position more than once during training, then stabilized around rank 2.

- **Other categories like automatic watering / air purifiers** show similar patterns:  
  - The loss curve (`loss.png`) decreases overall with noise;  
  - The rank curve (`rank.png`) improves in a **step-like fashion**: rank jumps at certain key iterations and then oscillates near a better position.

### 2. Prompt Constraints & Output Quality

- **“Include all products” constraint is essentially satisfied**:  
  - Sampled LLM RESPONSE blocks from the logs show that:
    - The recommendation list covers all products from the input list;
    - There are no missing or duplicated entries.

- **Name matching**:  
  - In current examples, the model mostly preserves the product names as given in the product list;  
  - Some tails of the descriptions can be corrupted by adversarial tokens, but the core product names remain recognizable.

- **Style & adversarial noise**:  
  - As optimization progresses, the STS (strategic text sequence) accumulates a large amount of apparently meaningless tokens;  
  - These tokens are clearly not human-friendly, but they do change the model’s internal representation and hence the ranking, which is the objective here.

### 3. Convergence Speed & Resource Usage

- **Per-step cost**:  
  - Later iterations typically take **9–12 seconds per step**, driven by `batch_size=120` and `num_samples=256`;  
  - A full 1600-step run thus remains a multi-hour job for a single target product.

- **Convergence pattern**:  
  - The loss decreases fastest in the first few hundred steps, where rank improvements are also most pronounced;  
  - In the later phase (~1000 steps and beyond), both loss and rank improvements slow down and sometimes oscillate, suggesting **diminishing returns and noise accumulation**;  
  - This implies that **running the full 1600 steps may not be necessary**, and future experiments could explore early stopping between 800–1200 steps.

---

## Intermediate Conclusions

Based on the StealthRank categories and products that have completed so far, we can state the following **interim conclusions**:

1. **GCG-based adversarial optimization can significantly improve the target product’s rank in LLM recommendations.**  
   - In most tested cases, the target product moves from a tail position (e.g., rank 6–7) to the top-1–3 positions;  
   - `Best top count` shows multiple evaluation steps where the target product achieves rank 1.

2. **The optimization remains effective under strict prompt constraints (include all products, exact name matching).**  
   - This indicates that rank manipulation does not rely on removing competitors, but rather on modifying textual patterns to bias the model’s internal ranking;  
   - The exact-name constraint is largely respected, with only minor corruption at the fringes of adversarial text.

3. **Adversarial sequences substantially degrade human readability.**  
   - The injected STS tokens make the prompt hard to interpret, yet still succeed in manipulating the ranking;  
   - In practical applications, if one needs both “good ranking” and “human-readable text”, further regularization or additional constraints in the objective will be necessary.

4. **The current configuration is compute-heavy; early stopping and hyperparameter search are promising directions.**  
   - With `num_iter=1600, batch_size=120, num_samples=256`, each run is expensive;  
   - From the curves, the first 30–50% of iterations contribute most of the rank gains, while later iterations show diminishing returns, suggesting substantial room for cost reduction.

---

## Suggested Next Steps

1. **Finish running all remaining categories in `datasets_5` for StealthRank and other algorithms.**  
   - Use the current logic in `iterate_datasets_5.sh` (up to 3 targets per category, skip if ≥3 targets already finished) to maximize category coverage under fixed compute budget;  
   - Afterwards, build a unified parsing script over `results_datasets_5` to summarize rank improvements per algorithm and per category.

2. **Systematically analyze `rank.png` and `loss.png`.**  
   - For each category, plot the distribution of initial vs final target ranks;  
   - Combine with loss curves to identify which iteration window contributes most of the improvement, and design principled early-stopping rules.

3. **Add stronger readability / safety constraints.**  
   - Incorporate penalties on output length, special-token frequency, or gibberish patterns into the loss;  
   - Experiment with adding explicit prompt instructions such as “avoid meaningless noise or excessive emojis”, and measure impact on rank optimization.

4. **Extend to other base models and modes.**  
   - Re-evaluate `llama32` (1B) and other long-context models under carefully tuned `num_samples` and `batch_size`;  
   - Compare:
     - Magnitude of rank improvement;
     - Readability of outputs;
     - OOM behavior and speed.

This English document summarizes **intermediate findings** based on the current `results_datasets_5` for StealthRank. As more experiments complete (more algorithms, more categories, or new models), we can extend and refine these conclusions.


