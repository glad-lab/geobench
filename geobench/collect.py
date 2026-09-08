"""Collect the final adversarial text per instance from each method's raw
outputs into ONE flat table (results/unified/instances/<method>.csv):

    method, dataset, category, target_idx, target_name, L,
    orig_text, adv_suffix, adv_text, select_rule, source_path

`adv_text` is what the ranker sees for the target item; the unified evaluator
(evaluate.py) never looks at the raw method outputs again.

Selection rule for iterative optimizers (StealthRank, STS, RAF): the paper used
the best-ranked iteration (`best`).  `last` is also supported so the choice is
explicit and reported.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from .config import PAPER_DATASETS, REPO_ROOT, RESULTS_ROOT
from .data import load_category, load_manifest

SPAN_RE = re.compile(r"</?span[^>]*>", re.IGNORECASE)


def strip_span(s) -> str:
    if not isinstance(s, str):
        return ""
    return SPAN_RE.sub("", s).strip()


def _cands(category: str) -> List[str]:
    return list(dict.fromkeys([category, category.replace(" ", "_"), category.replace("_", " ")]))


def _first_existing(paths: List[Path]) -> Optional[Path]:
    for p in paths:
        if p.exists():
            return p
    return None


# Dataset key -> directory name used inside each branch's result tree.
DSDIR = {
    "stealthrank": {"ragroll": "ragroll", "stsdata": "json", "rewrite_to_rank": "rewrite_to_rank_subsampled",
                    "llm_rank_optimizer": "llm_rank_optimizer_subsampled", "cseo": "cseo_subsampled",
                    "llmrank": "llmrank_subsampled"},
    "zero_shot":   {"ragroll": "ragroll", "stsdata": "json", "rewrite_to_rank": "rewrite_to_rank_subsampled",
                    "llm_rank_optimizer": "llm_rank_optimizer_subsampled", "cseo": "cseo_subsampled",
                    "llmrank": "llmrank_subsampled"},
    "sts":         {"ragroll": "ragroll_subsampled", "stsdata": "sts_subsampled", "rewrite_to_rank": "rewrite_to_rank_subsampled",
                    "llm_rank_optimizer": "llm_rank_optimizer_subsampled", "cseo": "cseo_subsampled",
                    "llmrank": "llm_rank_subsampled"},
    "raf":         {"ragroll": "ragroll", "stsdata": "stsdata", "llm_rank_optimizer": "llmrankoptim",
                    "rewrite_to_rank": "rewrite_to_rank", "cseo": "cseo", "llmrank": "llmrank"},
}

DEFAULT_ROOTS = {
    "stealthrank": REPO_ROOT / "branches/Stealth-Rank/results_new/benchmark_results/suffix/v1",
    "zero_shot":   REPO_ROOT / "branches/zero-shot/results_new/benchmark_results/suffix/v1",
    "sts":         REPO_ROOT / "branches/STS/results/benchmark_results/sts/v1",
    "raf":         REPO_ROOT / "branches/RAF/result/raf",
}


def _select_row(df: pd.DataFrame, rule: str) -> pd.Series:
    df = df.copy()
    df["product_rank"] = pd.to_numeric(df["product_rank"], errors="coerce")
    df = df.dropna(subset=["product_rank"])
    if rule == "last":
        return df.iloc[-1]
    # best: minimum rank; ties -> latest iteration (most optimized)
    best = df["product_rank"].min()
    return df[df["product_rank"] == best].iloc[-1]


# --------------------------------------------------------------------------- #
# Adapters: each returns (adv_suffix, adv_text, source_path) or None
# --------------------------------------------------------------------------- #
def adapt_stealthrank_like(root: Path, model: str, dsdir: str, category: str, idx: int,
                           orig: str, rule: str, zero_shot: bool = False):
    p = _first_existing([root / model / dsdir / c / str(idx) / "random_inference=True.csv" for c in _cands(category)])
    if p is None:
        return None
    df = pd.read_csv(p)
    if zero_shot:
        rows = df[df["iter"] == 1]
        if rows.empty:
            return None
        suffix = strip_span(rows.iloc[0]["attack_prompt"])
    else:
        suffix = strip_span(_select_row(df, rule)["attack_prompt"])
    return suffix, (orig + " " + suffix).strip(), str(p)


def adapt_sts(root: Path, model: str, dsdir: str, category: str, idx: int, orig: str, rule: str):
    d = _first_existing([root / model / dsdir / c / str(idx) for c in _cands(category)])
    if d is None:
        return None
    sts = d / "sts.txt"
    if not sts.exists():
        return "", orig, str(d)          # run produced no STS -> flagged by scan_failed_runs
    text = sts.read_text(encoding="utf-8", errors="replace").strip()
    if text.startswith(orig):
        suffix = text[len(orig):].strip()
    elif orig and orig in text:
        suffix = text.split(orig, 1)[1].strip()
    else:                                 # STS file holds only the suffix
        suffix = text
    return suffix, (orig + " " + suffix).strip(), str(sts)


def adapt_raf(root: Path, model: str, dsdir: str, category: str, idx: int, orig: str, rule: str):
    p = _first_existing([root / model / dsdir / c / str(idx) / f for c in _cands(category)
                         for f in ("raf_results.csv", "autodan_results.csv")])
    if p is None:
        return None
    df = pd.read_csv(p)
    suffix = strip_span(_select_row(df, rule)["attack_prompt"])
    return suffix, (orig + " " + suffix).strip(), str(p)


ADAPTERS = {
    "stealthrank": lambda **k: adapt_stealthrank_like(zero_shot=False, **k),
    "zero_shot":   lambda **k: adapt_stealthrank_like(zero_shot=True, **k),
    "sts":         lambda **k: adapt_sts(**k),
    "raf":         lambda **k: adapt_raf(**k),
}


def collect(method: str, datasets: List[str], model: str, root: Optional[Path], rule: str,
            dsdir_override: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    root = root or DEFAULT_ROOTS[method]
    dsmap = dict(DSDIR[method])
    if dsdir_override:
        dsmap.update(dsdir_override)
    rows, missing = [], 0
    for ds in datasets:
        man = load_manifest(ds)
        for cat, grp in man.groupby("category", sort=True):
            items = load_category(ds, cat)
            for _, r in grp.iterrows():
                idx = int(r.target_idx)
                orig = items[idx - 1].text
                out = ADAPTERS[method](root=root, model=model, dsdir=dsmap.get(ds, ds),
                                       category=cat, idx=idx, orig=orig, rule=rule)
                if out is None:
                    missing += 1
                    continue
                suffix, adv, src = out
                rows.append({"method": method, "dataset": ds, "category": cat, "target_idx": idx,
                             "target_name": items[idx - 1].name, "L": len(items),
                             "orig_text": orig, "adv_suffix": suffix, "adv_text": adv,
                             "select_rule": rule if method not in ("zero_shot",) else "single",
                             "source_path": src})
    df = pd.DataFrame(rows)
    print(f"[collect] {method}: {len(df)} instances, {missing} missing raw outputs")
    return df


def from_csv(method: str, path: Path) -> pd.DataFrame:
    """Generic loader for methods whose runner already writes the unified schema
    (TAP, C-SEO rewrites).  Required columns: dataset, category, target_idx, adv_text.
    orig_text / target_name / L are filled from the manifest if absent."""
    df = pd.read_csv(path)
    need = {"dataset", "category", "target_idx", "adv_text"}
    if not need <= set(df.columns):
        raise ValueError(f"{path}: need columns {need}, got {list(df.columns)}")
    df["method"] = method
    if "orig_text" not in df.columns or "target_name" not in df.columns or "L" not in df.columns:
        fills = []
        for _, r in df.iterrows():
            items = load_category(r.dataset, r.category)
            it = items[int(r.target_idx) - 1]
            fills.append({"orig_text": it.text, "target_name": it.name, "L": len(items)})
        df = pd.concat([df.drop(columns=[c for c in ("orig_text", "target_name", "L") if c in df.columns]),
                        pd.DataFrame(fills)], axis=1)
    if "adv_suffix" not in df.columns:
        df["adv_suffix"] = [a[len(o):].strip() if isinstance(a, str) and a.startswith(o) else ""
                            for a, o in zip(df.adv_text, df.orig_text)]
    df["select_rule"] = df.get("select_rule", "single")
    df["source_path"] = str(path)
    return df


def clean_baseline(datasets: List[str]) -> pd.DataFrame:
    """Pseudo-method with adv_text == orig_text; evaluating it measures ranking
    noise (the NRG a method gets for doing nothing)."""
    rows = []
    for ds in datasets:
        man = load_manifest(ds)
        for cat, grp in man.groupby("category", sort=True):
            items = load_category(ds, cat)
            for _, r in grp.iterrows():
                it = items[int(r.target_idx) - 1]
                rows.append({"method": "clean", "dataset": ds, "category": cat, "target_idx": int(r.target_idx),
                             "target_name": it.name, "L": len(items), "orig_text": it.text,
                             "adv_suffix": "", "adv_text": it.text, "select_rule": "none", "source_path": ""})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("method", choices=list(ADAPTERS) + ["csv", "clean"])
    ap.add_argument("--datasets", nargs="+", default=PAPER_DATASETS)
    ap.add_argument("--model", default="llama-3.1-8b", help="ranker the raw outputs were optimized against")
    ap.add_argument("--root", type=Path, default=None, help="override raw result root")
    ap.add_argument("--select", choices=["best", "last"], default="best")
    ap.add_argument("--dsdir", nargs="*", default=[], metavar="DATASET=DIRNAME",
                    help="override dataset->result-dir mapping, e.g. stsdata=json")
    ap.add_argument("--csv", type=Path, help="(method=csv) unified-schema CSV from TAP / C-SEO runners")
    ap.add_argument("--name", help="(method=csv) method key, e.g. tap, authoritative")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()

    if a.method == "csv":
        if not (a.csv and a.name):
            ap.error("--csv and --name are required with method=csv")
        df = from_csv(a.name, a.csv)
        name = a.name
    elif a.method == "clean":
        df = clean_baseline(a.datasets)
        name = "clean"
    else:
        override = dict(kv.split("=", 1) for kv in a.dsdir)
        df = collect(a.method, a.datasets, a.model, a.root, a.select, override)
        name = a.method
    out = a.out or (RESULTS_ROOT / "instances" / f"{name}.csv")
    if df.empty:
        print(f"[collect] nothing collected for {name}; not writing {out}")
        if out.exists() and out.stat().st_size < 64:
            out.unlink()                      # remove a stale empty file from an earlier run
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"[collect] wrote {len(df)} rows -> {out}")


if __name__ == "__main__":
    main()
