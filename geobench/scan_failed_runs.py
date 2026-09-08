"""Flag instances whose raw output is missing or degenerate.

    python -m geobench.scan_failed_runs results/unified/instances/*.csv

Signatures (all found in the submitted STS C-SEO news/retail rows, which
reported NRG 0.000, KVR 0.00, PPL-R 1.00 +- 0.00 = no suffix ever applied):
  * adv_text == orig_text            (no manipulation applied)
  * empty / whitespace-only suffix
  * suffix is a single token or only punctuation
  * a whole category with identical adv_text for every target
Also reports coverage against the manifest so N per (method, dataset) is explicit.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .data import load_manifest


def scan(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["adv_suffix"] = d["adv_suffix"].fillna("").astype(str)
    d["flag_no_change"] = d.adv_text.astype(str).str.strip() == d.orig_text.astype(str).str.strip()
    d["flag_empty_suffix"] = d.adv_suffix.str.strip().str.len() == 0
    d["flag_tiny_suffix"] = d.adv_suffix.str.strip().str.len().between(1, 3)
    d["flag_missing_src"] = d.source_path.fillna("").astype(str).str.len() == 0
    d["any_flag"] = d[[c for c in d.columns if c.startswith("flag_")]].any(axis=1)
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("instances", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    reports = []
    for p in a.instances:
        try:
            raw = pd.read_csv(p)
        except pd.errors.EmptyDataError:
            print(f"[scan] {p} is empty; skipping"); continue
        if raw.empty:
            print(f"[scan] {p} has no rows; skipping"); continue
        df = scan(raw)
        m = df.method.iloc[0]
        if m == "clean":                      # baseline is *supposed* to be unchanged; report coverage only
            df["any_flag"] = False
        for ds, g in df.groupby("dataset"):
            man = load_manifest(ds)
            reports.append({"method": m, "dataset": ds, "manifest_N": len(man), "collected_N": len(g),
                            "coverage": round(len(g) / len(man), 3),
                            "no_change": int(g.flag_no_change.sum()), "empty_suffix": int(g.flag_empty_suffix.sum()),
                            "tiny_suffix": int(g.flag_tiny_suffix.sum()), "flagged": int(g.any_flag.sum())})
        bad = df[df.any_flag]
        if len(bad):
            print(f"\n== {m}: {len(bad)} flagged instances ==")
            print(bad[["dataset", "category", "target_idx", "flag_no_change", "flag_empty_suffix", "flag_tiny_suffix", "source_path"]]
                  .to_string(index=False, max_colwidth=60))
    rep = pd.DataFrame(reports)
    print("\n== coverage / failure report ==")
    print(rep.to_string(index=False))
    if a.out:
        rep.to_csv(a.out, index=False)


if __name__ == "__main__":
    main()
