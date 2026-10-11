#!/usr/bin/env python
"""Archive per-instance outputs that no longer match their instance file.

An output is stale when it was scored on a different version of the attack set:
different (dataset, category, target_idx) keys, or a different adv_text length on
any row (e.g. TAP scored while its generation was still running).  Stale files and
their .run.json move to results/unified/_stale/<ranker>/ so geobench.evaluate
re-scores them from scratch.  Outputs that match their instances are never touched.

  python scripts/archive_stale_eval.py llama-3.1-8b qwen2.5-14b mistral-7b [--dry-run]
"""
import argparse, os, time
import pandas as pd
from geobench.config import RESULTS_ROOT
from geobench.evaluate import read_instances

KEY = ["dataset", "category", "target_idx"]


def keys(df):
    return set(zip(df.dataset.astype(str), df.category.astype(str), df.target_idx.astype(int)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rankers", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    inst = {}
    for p in sorted((RESULTS_ROOT / "instances").glob("*.csv")):
        try:
            df = read_instances(p)
        except ValueError as e:
            print(f"[skip] {p.name}: {e}")
            continue
        for m, sub in df.groupby("method"):
            s = sub[KEY].copy()
            s["target_idx"] = s.target_idx.astype(int)
            s["_alen"] = sub.adv_text.str.len().values
            inst[m] = s
    ts = time.strftime("%Y%m%d-%H%M%S")
    n_stale = 0
    for r in a.rankers:
        d = RESULTS_ROOT / "per_instance" / r
        for out in sorted(d.glob("*.csv")):
            m = out.stem
            if m not in inst:
                continue
            P = pd.read_csv(out, keep_default_na=False)
            I = inst[m]
            reason = None
            if keys(P) != keys(I):
                reason = f"{len(P)} scored rows vs {len(I)} instances"
            elif "adv_len_chars" in P:
                Q = P[KEY + ["adv_len_chars"]].copy()
                Q["target_idx"] = Q.target_idx.astype(int)
                M = Q.merge(I, on=KEY)
                n = int((pd.to_numeric(M.adv_len_chars, errors="coerce") != M._alen).sum())
                if n:
                    reason = f"{n} rows scored on different text"
            if not reason:
                continue
            n_stale += 1
            print(f"[stale] {r}/{out.name}: {reason}")
            if a.dry_run:
                continue
            arch = RESULTS_ROOT / "_stale" / r
            arch.mkdir(parents=True, exist_ok=True)
            os.replace(out, arch / f"{m}.{ts}.csv")
            meta = out.with_suffix(".run.json")
            if meta.exists():
                os.replace(meta, arch / f"{m}.{ts}.run.json")
    print(f"{n_stale} stale outputs{' (dry run, nothing moved)' if a.dry_run else ' archived'}")


if __name__ == "__main__":
    main()
