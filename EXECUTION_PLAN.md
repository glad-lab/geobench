# GEO-Bench — execution plan for the ARR October 2026 cycle (deadline Oct 12)

Everything below is run by you (Juice) on CARC Endeavour, plus one CPU-only
API step that needs an OpenAI key. Zhe runs nothing. All jobs are resumable:
if a job dies (TIMEOUT, node failure), re-run the *same* submit command and it
continues from its checkpoint.

State of the results tree on `revision` @ `0f596228` (checked Sept 15):

| instance set | llama-3.1-8b | qwen2.5-14b | mistral-7b | gpt-4o-mini | note |
|---|---|---|---|---|---|
| clean, stealthrank, raf__opt-vicuna-7b, 10 C-SEO strategies, zero_shot__att-gpt4omini | done | 7/15 done (simple_language 570/729; statistics, technical_terms, unique_words, zero_shot__att-gpt4omini missing) | done | done | qwen finishes in step A3 |
| zero_shot (regenerated 9/7, Llama attacker) | done | done | done | **stale** (scored on the old file) | re-score in step D |
| tap__att-llama8b (489/729), tap__att-qwen14b (363/729) | — | — | — | — | generation resumes in A4; scored in C |
| stealthrank / raf / sts `__opt-llama-3.1-8b` | — | — | — | — | produced by Stage 3 (A6) |
| ablation: zero_shot__att-qwen1.5b, zero_shot__att-qwen14b, cseo `rw-qwen14b` (3 strategies) | — | — | — | — | produced by A7 |

Conventions used in every block:

```bash
# login-node preamble (run once per shell)
cd /scratch1/nimase/geobench/geobench-rev
source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate geobench
export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1
```

---

## A. Today (Sept 15) — launch everything that can run in parallel

**A0. Confirm the CARC checkout is current.** The 13 Stage-3 files are in commit
`0f596228` and it is on `origin/revision`. If `git log` does not show it,
`submit_stage3.sh`, `10_branch_envs.sh`, `submit_ablation.sh` do not exist yet.

```bash
git pull origin revision
git log --oneline -1          # must print 0f596228 ...
ls scripts/slurm/submit_stage3.sh scripts/10_branch_envs.sh scripts/11_prefetch_models.sh
```

**A1. Legacy RAF rename (CPU, seconds; idempotent).**

```bash
python scripts/fix_legacy_names.py
```

**A2. Branch environments + branch data (login node, 10–25 min).** This is the
step you asked about: it downloads `torch==2.5.1` (~900 MB) plus the CUDA 12.x
runtime wheels (`nvidia-cublas`, `nvidia-cudnn`, … ≈ 2.5 GB) for *two* envs
(`env` for Stealth-Rank/RAF, `env-sts` for STS with `transformers==4.48`).
pip resolves, downloads, then unpacks; the long silent stretches are the
unpacking of the CUDA wheels. It is normal. Re-running the script is safe — pip
answers "Requirement already satisfied" for everything installed (about a
minute), then `prepare_branch_data.py` re-writes the branch data (seconds).
Run it inside `tmux` so a dropped SSH session does not kill pip. The script
must finish before A6.

```bash
bash scripts/10_branch_envs.sh
# success looks like:  "stealth env ok: torch 2.5.1 ..."  "sts env ok: torch ... transformers 4.48..."  then the branch-data summary
```

**A3. Finish the Qwen2.5-14B evaluation (1 GPU, resumes; ~10–14 h).**

```bash
RANKERS="qwen2.5-14b" bash scripts/slurm/submit_eval.sh
```

**A4. Resume the two open-attacker TAP runs (1 GPU + 2 GPUs; 48 h limit; resume).**

```bash
bash scripts/slurm/submit_attacks.sh
```

**A5. Prefetch Qwen2.5-1.5B for the ablation (login node, ~3 GB, once).**

```bash
bash scripts/11_prefetch_models.sh
```

**A6. Stage 3 — white-box re-optimisation against Llama-3.1-8B under the
unified prompt.** Three Slurm arrays (Stealth-Rank per catalog, RAF per
catalog, STS per (catalog, target) with `%25` concurrency). Only after A2 says
both envs are ok.

```bash
bash scripts/slurm/submit_stage3.sh llama-3.1-8b
```

Expected wall-clock with nlp_hiprio queueing: Stealth-Rank 1–2 days,
RAF 2–4 days, STS 1–3 days (~200 GPU-h total).

**A7. Attacker-strength ablation (3 × 1-GPU jobs; `cseo_qwen14b` needs 2 GPUs
worth of memory — it fits on one A6000 in bf16).**

```bash
bash scripts/slurm/submit_ablation.sh
```

**A8. Check the queue.**

```bash
squeue -u nimase -o "%.10i %.34j %.8T %.10M %.4D %R"
```

You should see: `geo_eval_qwen2p5-14b`, `geo_tap_att_llama8b`,
`geo_tap_att_qwen14b`, `geo_zs_qwen1p5b`, `geo_zs_qwen14b`, `geo_cseo_qwen14b`,
and the three arrays `geo_sr_llama-3.1-8b_*`, `geo_raf_llama-3.1-8b_*`,
`geo_sts_llama-3.1-8b_*` (names as printed by the submitters).

---

## A′. Thursday Sept 17 — status check, push, and the /scratch1 → /scratch2 move

Everything the jobs read or write lives under `/scratch1/nimase/geobench`
(repo `geobench-rev`, branch envs `env` and `env-sts`) and
`/scratch1/nimase/hf_cache`. The Stage-3 raw outputs are *inside the repo's
branch folders* (`branches/Stealth-Rank/results_new`, `branches/RAF/result`,
`branches/STS/results`) and are not git-tracked, so a `git push` alone does
not save them — copy the whole directory. Do this Thursday afternoon; each
rsync is incremental, so re-running it later only copies what changed.

```bash
# A′1. status (see B1) and push what git tracks
sacct -u nimase -S $(date -d '-3 days' +%F) -X -o JobID%14,JobName%34,State%10,Elapsed | grep -vE "RUNNING|PENDING"
git add -A results/unified logs && git commit -q -m "CARC results $(date +%F)" -c user.email=ojuicen@users.noreply.github.com --author="Ojas Nimase <ojuicen@users.noreply.github.com>" || true
git push origin revision

# A′2. copy models, envs, repo and branch results (30–60 min the first time; run in tmux)
mkdir -p /scratch2/nimase
rsync -a --info=progress2 /scratch1/nimase/hf_cache /scratch2/nimase/
rsync -a --info=progress2 /scratch1/nimase/geobench /scratch2/nimase/
du -sh /scratch2/nimase/hf_cache /scratch2/nimase/geobench
```

`_common.sh` already prefers `/scratch2/nimase/hf_cache` when it exists, so
new jobs read models from there automatically. Do **not** re-submit anything
from `/scratch2` while jobs on `/scratch1` are still running — the pending
array tasks have `/scratch1` paths baked into their scripts and would race
the copy.

**After the purge (Sept 18), two cases:**

* `/scratch1/nimase/geobench` still exists and jobs are still RUNNING →
  nothing to do; keep working in `/scratch1`, and repeat A′2 every evening so
  `/scratch2` stays current.
* `/scratch1` was wiped (jobs show FAILED / NODE_FAIL, directory gone) →
  switch to the copy and re-submit; every task that already has a result
  exits immediately, so only the unfinished ones run:

```bash
cd /scratch2/nimase/geobench/geobench-rev && git pull origin revision
export CONDA_BIN_STEALTH=/scratch2/nimase/geobench/env/bin CONDA_BIN_STS=/scratch2/nimase/geobench/env-sts/bin
# (put those two exports in ~/.bashrc so later shells have them)
RANKERS="qwen2.5-14b" bash scripts/slurm/submit_eval.sh
bash scripts/slurm/submit_attacks.sh
bash scripts/slurm/submit_stage3.sh llama-3.1-8b
bash scripts/slurm/submit_ablation.sh
```

The conda env `geobench` is in `/home1`, so it is unaffected either way.

---

## B. Daily while jobs run (Sept 16 → ~Sept 22)

**B1. Status.**

```bash
sacct -u nimase -S $(date -d '-2 days' +%F) -X -o JobID%14,JobName%34,State%10,Elapsed,ExitCode | grep -v RUNNING | grep -v PENDING
tail -n 3 logs/*.err | grep -iE "error|Traceback|CUDA out of memory" -B2 | head -40
```

**B2. Progress counters (CPU).**

```bash
for f in results/unified/instances/tap__att-*.csv results/unified/instances/zero_shot__att-*.csv results/unified/instances/*rw-qwen14b*.csv; do [[ -f $f ]] && echo "$(($(wc -l < $f)-1))  $f"; done
ls results/unified/per_instance/qwen2.5-14b | wc -l      # 15 csv + run.json files when done
ls branches/Stealth-Rank/results_new/benchmark_results/suffix/v2_unified/llama-3.1-8b 2>/dev/null | head
find branches/RAF/result/raf/llama-3.1-8b -name autodan_results.csv | wc -l
find branches/STS/results/benchmark_results/sts/v1/llama-3.1-8b -name sts.txt | wc -l   # target 729
```

**B3. Push results every evening (so nothing is lost to the purge or a node).**

```bash
git add -A results/unified logs && git commit -q -m "CARC results $(date +%F)" -c user.email=ojuicen@users.noreply.github.com --author="Ojas Nimase <ojuicen@users.noreply.github.com>" || true
git push origin revision
```

**B4. Re-submit anything that ended TIMEOUT / NODE_FAIL / FAILED with the same
command from A3–A7.** Array tasks: re-running `submit_stage3.sh` re-submits all
three arrays; each task exits immediately when its result already exists, so
that is cheap. For a single failed array task you can instead do
`bash scripts/slurm/submit_sts.sh llama-3.1-8b <dataset>` (per-dataset).

---

## C. When the three Stage-3 arrays are done (~Sept 22)

**C1. Collect the white-box outputs into unified instance files (CPU, seconds).**

```bash
bash scripts/slurm/submit_collect_whitebox.sh llama-3.1-8b
wc -l results/unified/instances/*__opt-llama-3.1-8b.csv         # expect 730 lines each (729 + header)
```

The `scan_failed_runs` printout at the end lists (method, dataset) coverage
and degenerate rows (`adv_text == orig_text`). Anything below 729 → check the
matching array task's `.err`, re-submit per B4, re-run C1.

**C2. Score every instance set on the three open rankers (3 × 1-GPU jobs,
each resumes and skips complete sets).** This covers TAP, the `__opt-llama`
sets (white-box on Llama, transfer on Qwen/Mistral) and the ablation sets.

```bash
RANKERS="llama-3.1-8b qwen2.5-14b mistral-7b" bash scripts/slurm/submit_eval.sh
```

~6–12 h per ranker for the new sets (K=10 orderings × ~3,600 new instances).

**C3. Detectability + relevance + reranker + stats (1 GPU, ~8 h).**

```bash
bash scripts/slurm/submit_detect.sh
```

Runs the Qwen2.5-14B judge, bge-large drift, bge-reranker-v2-m3 ranking and
`stats` for every ranker present. Re-runnable.

**C4. Push (B3).**

---

## D. GPT-4o-mini transfer evaluation (needs an OpenAI key; CPU; no Slurm)

Zhe's gpt-4o-mini scores cover the 15 old sets. Still missing on gpt-4o-mini:
`zero_shot` (stale: scored on the pre-9/7 file), `tap__att-*`,
`*__opt-llama-3.1-8b`, and the three ablation sets. Cost: ~7,300 calls ×
~1.3k input tokens per set ≈ $1.5–2 per set → **≈ $20 for all nine sets**
(gpt-4o-mini, $0.15/M input). Budget $40.

Get a key (platform.openai.com → API keys; put $25 of credit on the account).
Do **not** commit it anywhere.

```bash
# D1. retire the stale zero_shot scores (git-tracked, so use git mv)
mkdir -p results/unified/_stale/gpt-4o-mini
git mv results/unified/per_instance/gpt-4o-mini/zero_shot.csv      results/unified/_stale/gpt-4o-mini/
git mv results/unified/per_instance/gpt-4o-mini/zero_shot.run.json results/unified/_stale/gpt-4o-mini/

# D2. run on the login node (internet is available there); the script nohups itself and logs to logs/eval_gpt-4o-mini_*.out
export OPENAI_API_KEY='sk-...'
CONDA_BIN=/home1/nimase/.conda/envs/geobench/bin GEOBENCH_API_PROVIDER=openai RANKERS=gpt-4o-mini bash scripts/slurm/submit_eval_api.sh
tail -f logs/eval_gpt-4o-mini_*.out     # Ctrl-C to stop watching; the run continues
```

The preflight pass (first thing the script does) refuses any instance file
that is still incomplete — so run D only after C1 and after both TAP jobs have
finished. Sets already complete on gpt-4o-mini are skipped, so the old 14 sets
cost nothing. If the login node kills long processes, run the same command
from your Mac instead (`.venv-geobench` is already set up there; drop the
`CONDA_BIN=` prefix).

If you decide not to spend on this: the paper reports gpt-4o-mini only for the
15 sets Zhe scored, and the transfer row for the `__opt-llama` attacks becomes
"three open rankers" — state this in the reproducibility appendix.

---

## E. Optional: Stage 3 against Mistral-7B (decide by Sept 24)

Adds a second white-box ranker to the ranker-specific-vulnerability claim.
Another ~200 GPU-h; only if the Llama arrays finished by Sept 22 and the queue
is moving. Identical sequence with `mistral-7b`:

```bash
bash scripts/slurm/submit_stage3.sh mistral-7b            # A6
bash scripts/slurm/submit_collect_whitebox.sh mistral-7b  # C1, when done
RANKERS="llama-3.1-8b qwen2.5-14b mistral-7b" bash scripts/slurm/submit_eval.sh   # C2 (skips complete sets)
bash scripts/slurm/submit_detect.sh                        # C3
```

If not done by Oct 3, drop it — the Llama-only Stage 3 already answers the
reviewers' white-box concern.

---

## F. Freeze and tables (target: Oct 3; hard stop Oct 6)

```bash
git pull origin revision            # on the Mac, after the final CARC push
RANKERS="llama-3.1-8b qwen2.5-14b mistral-7b gpt-4o-mini" bash scripts/05_tables.sh
ls results/unified/tables           # table_main_<ranker>.tex, table_rankers.tex, ranker_order_spearman.csv, fig_tradeoff_<ranker>.pdf, appendix_repro.tex
```

`05_tables.sh` only uses rankers whose `summary/<ranker>_summary.csv` exists,
so it works with whatever finished.

---

## Calendar

| date | what |
|---|---|
| Sept 15 | A0–A8 |
| Sept 16 | B daily |
| Sept 17 (Thu) | A′: status, push, rsync everything to /scratch2 |
| Sept 18 | purge — check `/scratch1` and `squeue`; if wiped, the A′ "after the purge" block |
| ~Sept 20 | TAP + ablation + qwen eval done → C2 can already start for those (`submit_eval.sh` is safe to run early; re-run later for the `__opt` sets) |
| ~Sept 22 | Stage-3 arrays done → C1, C2, C3, push |
| Sept 24 | decide E |
| ~Sept 25 | D (gpt-4o-mini, after TAP finished) |
| Oct 3 | results freeze; F; start writing with final numbers (draft sections can start now — story is fixed: evaluation optimism, ranker-specific vulnerability, ≈0 transfer) |
| Oct 6 | hard stop for any late job; whatever is missing is stated in the appendix |
| Oct 10 | full draft to Zhao/Xiyang; author list updated (Gengpei removed with his written consent) |
| Oct 12 | ARR submission |

## If something breaks

* `OSError: … not found in cache` in a job log → the model is not in
  `hf_cache`; run `bash scripts/11_prefetch_models.sh` (login node, has
  internet) or `HF_HUB_OFFLINE=0 python -c "from huggingface_hub import snapshot_download as s; s('<repo-id>')"`.
* `CUDA out of memory` in `zs_qwen14b` or `cseo_qwen14b` → give the job two
  GPUs: in `scripts/slurm/submit_attacks.sh` append `; GPUS[zs_qwen14b]=2` (or
  `GPUS[cseo_qwen14b]=2`) to that job's `JOBS[...]=` line, exactly like the
  `tap_att_qwen14b` line, then re-run `bash scripts/slurm/submit_ablation.sh`
  (it resumes; the finished jobs exit at once).
* Stage-3 task dies with an import error → the branch env is broken; re-run
  A2 (it re-installs only the failing env) and re-submit.
* `Generation incomplete` from the evaluator → an attack set is still being
  produced; wait or re-run C2 later (it is safe to run repeatedly).
