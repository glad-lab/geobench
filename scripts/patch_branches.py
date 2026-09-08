"""One-shot, idempotent patches to the method branches (run from repo root):

  python scripts/patch_branches.py          # apply
  python scripts/patch_branches.py --check  # report only

1. Chat template: Stealth-Rank, zero-shot and RAF wrapped Llama-3.1-8B-Instruct
   in the Llama-2 `[INST] <<SYS>>` format; the model visibly echoed `<<SYS>>` in
   its answers (see any results_new/.../generated_result).  Replace with the
   Llama-3 header template.  STS already used it but also hard-coded
   `<|begin_of_text|>` while the tokenizer adds BOS -> double BOS; remove it.
2. Multi-ranker: add Qwen2.5-7B-Instruct (ChatML) to every MODEL_PATH_DICT /
   SYSTEM_PROMPT / argparse choices; STS `--model` accepts the same keys.
3. Tokenizer pad token: Llama-3 has no <unk>; fall back to eos.
4. StealthRank C-SEO config used batch_size=2/ngram=2/target=20 while every
   other dataset used 5/5/50 (contradicts the rebuttal).  Write a
   `..._cseo_uniform.yaml` with the common values; the original is kept and
   documented as the memory-constrained variant.
Files are rewritten in place (no unlink), so this works on read-only-delete mounts.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
B = ROOT / "branches"

L3_HEAD = "<|start_header_id|>system<|end_header_id|>\\n\\n{ASSSISTANT_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>\\n\\n"
L3_TAIL = "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\\n\\n"
QWEN_HEAD = "<|im_start|>system\\n{ASSSISTANT_PROMPT}<|im_end|>\\n<|im_start|>user\\n"
QWEN_TAIL = "<|im_end|>\\n<|im_start|>assistant\\n"

MODEL_LINE = "'llama-3.1-8b': 'meta-llama/Meta-Llama-3.1-8B-Instruct',"
MODEL_LINE_NEW = MODEL_LINE + "\n    'qwen2.5-7b': 'Qwen/Qwen2.5-7B-Instruct',\n    'qwen2.5-14b': 'Qwen/Qwen2.5-14B-Instruct',"

EDITS = []  # (path, old, new, required)


def add(path, old, new, required=True):
    EDITS.append((path, old, new, required))


# ---- Stealth-Rank & zero-shot (same codebase) --------------------------------
for br in ("Stealth-Rank", "zero-shot"):
    for f in ("experiment/run_no_wandb.py", "experiment/main.py", "experiment/zero_shot_baseline.py"):
        p = B / br / f
        if not p.exists():
            continue
        # single-line dict style (run_no_wandb.py, zero_shot_baseline.py)
        add(p, "'llama': {'head': f'[INST] <<SYS>>\\n{ASSSISTANT_PROMPT}\\n<<SYS>>\\n\\n', 'tail': ' [/INST]'},",
            f"'llama': {{'head': f'{L3_HEAD}', 'tail': '{L3_TAIL}'}},\n    'qwen2.5': {{'head': f'{QWEN_HEAD}', 'tail': '{QWEN_TAIL}'}},", required=False)
        # multi-line dict style (main.py)
        add(p, "SYSTEM_PROMPT = {'llama': {'head': f'[INST] <<SYS>>\\n{ASSSISTANT_PROMPT}\\n<<SYS>>\\n\\n', \n                            'tail': ' [/INST]'},",
            f"SYSTEM_PROMPT = {{'llama': {{'head': f'{L3_HEAD}',\n                            'tail': '{L3_TAIL}'}},\n                'qwen2.5': {{'head': f'{QWEN_HEAD}', 'tail': '{QWEN_TAIL}'}},", required=False)
        add(p, MODEL_LINE, MODEL_LINE_NEW, required=False)
        add(p, "choices=['llama-3.1-8b', 'llama-2-7b', 'vicuna-7b', 'mistral-7b', 'deepseek-7b']",
            "choices=['llama-3.1-8b', 'llama-2-7b', 'vicuna-7b', 'mistral-7b', 'deepseek-7b', 'qwen2.5-7b', 'qwen2.5-14b']", required=False)
    add(B / br / "experiment/get.py", "tokenizer.pad_token = tokenizer.unk_token",
        "tokenizer.pad_token = tokenizer.unk_token if tokenizer.unk_token is not None else tokenizer.eos_token")

# ---- RAF ---------------------------------------------------------------------
p = B / "RAF/experiment/main.py"
add(p, "SYSTEM_PROMPT = {'llama': {'head': f'<<SYS>>\\n{ASSSISTANT_PROMPT}\\n<<SYS>>\\n\\n', \n                            'tail': ' [/INST] {\"ranked_products\": [\"'},",
    f"SYSTEM_PROMPT = {{'llama': {{'head': f'{L3_HEAD}',\n                            'tail': '{L3_TAIL}{{\"ranked_products\": [\"'}},\n"
    f"                'qwen2.5': {{'head': f'{QWEN_HEAD}', 'tail': '{QWEN_TAIL}{{\"ranked_products\": [\"'}},")
add(p, "SRP_SYSTEM_PROMPT = {'llama': {'head': f'[INST] <<SYS>>\\n{SRP_ASSSISTANT_PROMPT}\\n<<SYS>>\\n\\n', \n                            'tail': ' [/INST]'},",
    "SRP_SYSTEM_PROMPT = {'llama': {'head': f'<|start_header_id|>system<|end_header_id|>\\n\\n{SRP_ASSSISTANT_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>\\n\\n',\n                            'tail': '" + L3_TAIL + "'},")
add(p, MODEL_LINE, MODEL_LINE_NEW)
add(p, "choices=['llama-3.1-8b', 'llama-2-7b', 'vicuna-7b', 'mistral-7b', 'deepseek-7b', 'qwen-4b', 'phi-2.7b']",
    "choices=['llama-3.1-8b', 'llama-2-7b', 'vicuna-7b', 'mistral-7b', 'deepseek-7b', 'qwen-4b', 'phi-2.7b', 'qwen2.5-7b', 'qwen2.5-14b']")
add(B / "RAF/experiment/get.py", "tokenizer.pad_token = tokenizer.unk_token",
    "tokenizer.pad_token = tokenizer.unk_token if tokenizer.unk_token is not None else tokenizer.eos_token")

# ---- STS ---------------------------------------------------------------------
p = B / "STS/rank_opt.py"
add(p, "MODEL_PATH_DICT = {'llama-3.1-8b': 'NousResearch/Meta-Llama-3.1-8B-Instruct'}",
    "MODEL_PATH_DICT = {'llama-3.1-8b': 'NousResearch/Meta-Llama-3.1-8B-Instruct',\n"
    "                       'mistral-7b': 'mistralai/Mistral-7B-Instruct-v0.3',\n"
    "                       'vicuna-7b': 'lmsys/vicuna-7b-v1.5',\n"
    "                       'qwen2.5-7b': 'Qwen/Qwen2.5-7B-Instruct',\n                       'qwen2.5-14b': 'Qwen/Qwen2.5-14B-Instruct'}")
add(p, "SYSTEM_PROMPT = {'llama': {'head': f'<|begin_of_text|><|start_header_id|>system<|end_header_id|>\\n\\n{ASSSISTANT_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>\\n\\nProducts:\\n',\n"
       "                            'tail': '<|eot_id|><|start_header_id|>assistant<|end_header_id|>\\n\\n'}}",
    "SYSTEM_PROMPT = {'llama': {'head': f'<|start_header_id|>system<|end_header_id|>\\n\\n{ASSSISTANT_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>\\n\\nProducts:\\n',\n"
    "                            'tail': '<|eot_id|><|start_header_id|>assistant<|end_header_id|>\\n\\n'},\n"
    "                     'mistral': {'head': f'[INST] {ASSSISTANT_PROMPT}\\n\\nProducts:\\n', 'tail': ' [/INST]'},\n"
    "                     'vicuna': {'head': f'{ASSSISTANT_PROMPT}\\n\\nUser: Products:\\n', 'tail': '\\n\\nAssistant: '},\n"
    "                     'qwen2.5': {'head': f'<|im_start|>system\\n{ASSSISTANT_PROMPT}<|im_end|>\\n<|im_start|>user\\nProducts:\\n', 'tail': '<|im_end|>\\n<|im_start|>assistant\\n'}}")
add(p, 'choices=["llama-3.1-8b"]', 'choices=["llama-3.1-8b", "mistral-7b", "vicuna-7b", "qwen2.5-7b", "qwen2.5-14b"]')


def apply(check_only: bool) -> int:
    failures = 0
    for path, old, new, required in EDITS:
        if not path.exists():
            if required:
                print(f"MISSING  {path}"); failures += 1
            continue
        txt = path.read_text(encoding="utf-8")
        if new in txt:
            print(f"ok       {path.relative_to(ROOT)}  (already patched)")
            continue
        if old not in txt:
            if required:
                print(f"NOMATCH  {path.relative_to(ROOT)}: {old[:60]!r}"); failures += 1
            continue
        if not check_only:
            path.write_text(txt.replace(old, new, 1), encoding="utf-8")   # in-place overwrite, no unlink
        print(f"patched  {path.relative_to(ROOT)}: {old[:50]!r}")
    return failures


def write_uniform_cseo_config(check_only: bool):
    src = B / "Stealth-Rank/configs/suffix_llama-3.1-8b_cseo.yaml"
    dst = B / "Stealth-Rank/configs/suffix_llama-3.1-8b_cseo_uniform.yaml"
    if not src.exists():
        return
    txt = src.read_text()
    txt = re.sub(r"batch_size:\n    value: 2\b", "batch_size:\n    value: 5", txt)
    txt = re.sub(r"ngram:\n    value: 2\b", "ngram:\n    value: 5", txt)
    txt = re.sub(r"target:\n    value: 20\b", "target:\n    value: 50", txt)
    txt = txt.replace('comment:\n    value: "main experiment"',
                      'comment:\n    value: "C-SEO with the SAME hyper-parameters as the other datasets (batch 5 / ngram 5 / target 50); use --config to select"')
    if not check_only:
        dst.write_text(txt)
    print(f"wrote    {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    n = apply(a.check)
    write_uniform_cseo_config(a.check)
    sys.exit(1 if n else 0)
