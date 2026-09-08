"""Unified evaluator.

    python -m geobench.evaluate --instances results/unified/instances/*.csv \
        --ranker llama-3.1-8b --K 10

For every instance row it
  1. ranks the CLEAN candidate list K times (K seeded random orderings) -> r_before
     (cached per ranker/dataset/category/target so all methods share it),
  2. ranks the list with the target's adv_text substituted, SAME K orderings -> r_after,
  3. aggregates the K ranks (median by default),
  4. computes NRG / Success@a / Promote@a / KVR / PPL-R,
and appends one row to results/unified/per_instance/<ranker>/<method>.csv.
Re-running resumes (rows already present are skipped).
"""
from __future__ import annotations

import argparse
import json
import math
import time
import zlib
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from .config import DEFAULT_K, PPL_MODEL, RESULTS_ROOT
from .data import load_category, query_noun
from .metrics import (Perplexity, aggregate_rank, instance_metrics, keyword_violation,
                      matched_keywords, ppl_ratio)
from .rankers import load_ranker


def _ikey(r) -> str:
    return f"{r['dataset']}|{r['category']}|{int(r['target_idx'])}"


class CleanCache:
    def __init__(self, path: Path):
        self.path = path
        self.d: Dict[str, List[int]] = {}
        if path.exists():
            df = pd.read_csv(path)
            for _, r in df.iterrows():
                self.d[r["key"]] = json.loads(r["ranks"])

    def get(self, key):
        return self.d.get(key)

    def put(self, key, ranks):
        self.d[key] = list(map(int, ranks))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a") as f:
            if f.tell() == 0:
                f.write("key,ranks\n")
            f.write(f'{key},"{json.dumps(self.d[key])}"\n')


def evaluate(instances: pd.DataFrame, ranker_key: str, K: int, agg: str, seed: int,
             ppl: Optional[Perplexity], out_path: Path, ranker=None, limit: Optional[int] = None):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out_path.exists():
        prev = pd.read_csv(out_path)
        done = {f"{r['method']}|{_ikey(r)}" for r in prev.to_dict("records")}
    cache = CleanCache(RESULTS_ROOT / "clean_ranks" / f"{ranker_key}.csv")
    ranker = ranker or load_ranker(ranker_key)

    n_done = 0
    t0 = time.time()
    cat_cache: Dict[str, list] = {}
    for _, r in instances.iterrows():
        key = _ikey(r)
        if f"{r['method']}|{key}" in done:
            continue
        ck = f"{r['dataset']}|{r['category']}"
        if ck not in cat_cache:
            cat_cache[ck] = load_category(r["dataset"], r["category"])
        items = cat_cache[ck]
        idx = int(r["target_idx"])
        names = [it.name for it in items]
        texts = [it.text for it in items]
        target = names[idx - 1]
        noun = query_noun(r["dataset"], r["category"])
        L = len(items)
        inst_seed = seed * 100003 + zlib.crc32(key.encode()) % 100003   # stable across runs

        ranks_before = cache.get(key)
        if ranks_before is None or len(ranks_before) != K:
            ranks_before = ranker.rank(noun, names, texts, target, K=K, seed=inst_seed)
            cache.put(key, ranks_before)

        adv_texts = list(texts)
        adv_texts[idx - 1] = str(r["adv_text"]) if isinstance(r["adv_text"], str) else texts[idx - 1]
        ranks_after = ranker.rank(noun, names, adv_texts, target, K=K, seed=inst_seed)

        rb = aggregate_rank(ranks_before, agg)
        ra = aggregate_rank(ranks_after, agg)
        row = {
            "method": r["method"], "ranker": ranker_key, "dataset": r["dataset"],
            "category": r["category"], "target_idx": idx, "target_name": target, "L": L,
            "K": K, "agg": agg, "r_before": rb, "r_after": ra,
            "ranks_before": json.dumps(ranks_before), "ranks_after": json.dumps(ranks_after),
            **instance_metrics(rb, ra, L),
            "kvr": keyword_violation(r["adv_text"]),
            "kvr_hits": "|".join(matched_keywords(r["adv_text"])),
            "kvr_suffix_only": keyword_violation(r.get("adv_suffix", "")),
            "kvr_orig": keyword_violation(r["orig_text"]),      # base rate of the clean description
            "adv_len_chars": len(str(r["adv_text"])),
            "suffix_len_chars": len(str(r.get("adv_suffix", "") or "")),
            "select_rule": r.get("select_rule", ""),
        }
        if ppl is not None:
            po, pa = ppl(r["orig_text"]), ppl(r["adv_text"])
            row.update({"ppl_orig": po, "ppl_adv": pa, "ppl_r": ppl_ratio(po, pa)})
        pd.DataFrame([row]).to_csv(out_path, mode="a", header=not out_path.exists() or out_path.stat().st_size == 0, index=False)
        n_done += 1
        if n_done % 10 == 0:
            print(f"[evaluate] {r['method']}@{ranker_key}: {n_done} done, {time.time() - t0:.0f}s")
        if limit and n_done >= limit:
            break
    print(f"[evaluate] {ranker_key}: wrote {n_done} new rows -> {out_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--instances", nargs="+", type=Path, required=True)
    ap.add_argument("--ranker", default="llama-3.1-8b")
    ap.add_argument("--K", type=int, default=DEFAULT_K)
    ap.add_argument("--agg", choices=["median", "mean", "min"], default="median")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--no-ppl", action="store_true", help="skip perplexity (e.g. API-ranker runs; PPL is ranker-independent)")
    ap.add_argument("--ppl-model", default=PPL_MODEL)
    ap.add_argument("--batch-size", type=int, default=10)
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=None, help="debug: stop after N instances")
    a = ap.parse_args()

    ppl = None if a.no_ppl else Perplexity(a.ppl_model)
    ranker = load_ranker(a.ranker, batch_size=a.batch_size)
    for p in a.instances:
        df = pd.read_csv(p)
        if a.datasets:
            df = df[df.dataset.isin(a.datasets)]
        for method, sub in df.groupby("method"):
            out = RESULTS_ROOT / "per_instance" / a.ranker / f"{method}.csv"
            evaluate(sub, a.ranker, a.K, a.agg, a.seed, ppl, out, ranker=ranker, limit=a.limit)


if __name__ == "__main__":
    main()
