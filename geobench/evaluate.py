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
import threading
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from .config import DEFAULT_K, PPL_MODEL, RESULTS_ROOT
from .data import load_category, query_noun
from .metrics import (Perplexity, aggregate_rank, instance_metrics, keyword_violation,
                      matched_keywords, ppl_ratio)
from .rankers import load_ranker, OpenAIRanker
from .run_state import atomic_text, base_method, bind_config, digest, experiment_name, run_lock, api_workers, completed_calls


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
        atomic_text(self.path, pd.DataFrame([
            {"key": k, "ranks": json.dumps(v)} for k, v in self.d.items()
        ]).to_csv(index=False))


def evaluate(instances: pd.DataFrame, ranker_key: str, K: int, agg: str, seed: int,
             ppl: Optional[Perplexity], out_path: Path, ranker=None, limit: Optional[int] = None):
    if K < 1:
        raise ValueError("K must be positive")
    ranker = ranker or load_ranker(ranker_key)
    identity = getattr(ranker, "identity", {"model": ranker.name})
    protocol = {"schema": 2, "ranker": identity, "K": K, "agg": agg, "seed": seed,
                "max_new_tokens": ranker.max_new_tokens,
                "code": digest([Path(__file__).with_name(f).read_text()
                                for f in ("evaluate.py", "rankers.py", "prompts.py", "metrics.py", "api.py")])}
    source = [[ds, cat, [[it.name, it.text] for it in load_category(ds, cat)]]
              for ds, cat in sorted(set(zip(instances.dataset, instances.category)))]
    config = dict(protocol, input=digest(instances.to_csv(index=False)), source=digest(source),
                  ppl=None if ppl is None else {"model": getattr(ppl.model.config, "_name_or_path", "unknown")})
    with run_lock(out_path.with_suffix(".lock")):
        bind_config(out_path, config)
        return _evaluate(instances, ranker_key, K, agg, seed, ppl, out_path, ranker,
                         limit, digest(protocol)[:20])


def _evaluate(instances, ranker_key, K, agg, seed, ppl, out_path, ranker, limit, cache_id):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    saved_rows = []
    if out_path.exists():
        prev = pd.read_csv(out_path, keep_default_na=False)
        saved_rows = prev.to_dict("records")
        done = {f"{r['method']}|{_ikey(r)}" for r in saved_rows}
        if len(done) != len(saved_rows):
            raise ValueError(f"Duplicate evaluation checkpoint rows: {out_path}")
    cache = CleanCache(RESULTS_ROOT / "clean_ranks" / f"{ranker_key}__{cache_id}.csv")

    n_done = 0
    t0 = time.time()
    cat_cache = {f"{ds}|{cat}": load_category(ds, cat)
                 for ds, cat in set(zip(instances.dataset, instances.category))}
    cache_lock = threading.Lock()
    pending = [r for r in instances.to_dict("records") if f"{r['method']}|{_ikey(r)}" not in done]
    if limit:
        pending = pending[:limit]
    def evaluate_one(r):
        key = _ikey(r)
        ck = f"{r['dataset']}|{r['category']}"
        items = cat_cache[ck]
        idx = int(r["target_idx"])
        names = [it.name for it in items]
        texts = [it.text for it in items]
        target = names[idx - 1]
        noun = query_noun(r["dataset"], r["category"])
        L = len(items)
        inst_seed = seed * 100003 + zlib.crc32(key.encode()) % 100003   # stable across runs

        clean_key = digest([key, noun, names, texts, K, inst_seed])
        with cache_lock:
            ranks_before = cache.get(clean_key)
        if ranks_before is None or len(ranks_before) != K:
            ranks_before = ranker.rank(noun, names, texts, target, K=K, seed=inst_seed)
            with cache_lock:
                cache.put(clean_key, ranks_before)

        adv_texts = list(texts)
        adv_texts[idx - 1] = str(r["adv_text"]) if isinstance(r["adv_text"], str) else texts[idx - 1]
        ranks_after = ranker.rank(noun, names, adv_texts, target, K=K, seed=inst_seed)

        rb = aggregate_rank(ranks_before, agg)
        ra = aggregate_rank(ranks_after, agg)
        row = {
            "method": r["method"], "base_method": base_method(r["method"]),
            "ranker": ranker_key, "dataset": r["dataset"],
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
        return row
    workers = api_workers() if isinstance(ranker, OpenAIRanker) and ppl is None else 1
    for row in completed_calls(evaluate_one, pending, workers):
        saved_rows.append(row)
        atomic_text(out_path, pd.DataFrame(saved_rows).to_csv(index=False))
        done.add(f"{row['method']}|{_ikey(row)}")
        n_done += 1
        if n_done % 10 == 0:
            print(f"[evaluate] {row['method']}@{ranker_key}: {n_done} done, {time.time() - t0:.0f}s", flush=True)
    print(f"[evaluate] {ranker_key}: wrote {n_done} new rows -> {out_path}")


def read_instances(path: Path) -> pd.DataFrame:
    meta = path.with_suffix(".run.json")
    if meta.exists() and not json.loads(meta.read_text()).get("complete"):
        raise ValueError(f"Generation incomplete: {path}; resume generation before evaluation")
    df = pd.read_csv(path, keep_default_na=False)
    required = {"method", "dataset", "category", "target_idx", "orig_text", "adv_text"}
    if not required <= set(df.columns) or df.empty:
        raise ValueError(f"Missing instance columns or empty file: {path}")
    # Legacy runners put the variant only in the filename. Normalize at ingestion.
    if "__" in path.stem:
        base = base_method(path.stem)
        if not df.method.isin([base, path.stem]).all():
            raise ValueError(f"Variant filename conflicts with method column: {path}")
        df["method"] = experiment_name(path.stem)
    for name in df.method.unique():
        experiment_name(name)
    df["base_method"] = df.method.map(base_method)
    if df.duplicated(["method", "dataset", "category", "target_idx"]).any():
        raise ValueError(f"Duplicate instance identities: {path}")
    if not df.adv_text.map(lambda value: isinstance(value, str) and bool(value.strip())).all():
        raise ValueError(f"Empty/non-text attack: {path}")
    return df


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
    ap.add_argument("--preflight", action="store_true", help="validate input files without loading a model or credentials")
    a = ap.parse_args()

    if a.K < 1:
        ap.error("--K must be positive")
    frames = []
    for p in a.instances:
        df = read_instances(p)
        if a.datasets:
            df = df[df.dataset.isin(a.datasets)]
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    if combined.empty or combined.duplicated(["method", "dataset", "category", "target_idx"]).any():
        raise ValueError("Empty selection or overlapping instance identities across input files")
    if a.preflight:
        print(f"[preflight] {len(combined)} rows, {combined.method.nunique()} experiments, K={a.K}; no API calls")
        return
    with run_lock(RESULTS_ROOT / "per_instance" / a.ranker / ".evaluation.lock"):
        ppl = None if a.no_ppl else Perplexity(a.ppl_model)
        ranker = load_ranker(a.ranker, batch_size=a.batch_size)
        for method, sub in combined.groupby("method"):
            out = RESULTS_ROOT / "per_instance" / a.ranker / f"{method}.csv"
            evaluate(sub, a.ranker, a.K, a.agg, a.seed, ppl, out, ranker=ranker, limit=a.limit)


if __name__ == "__main__":
    main()
