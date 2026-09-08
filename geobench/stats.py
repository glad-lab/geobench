"""Bootstrap confidence intervals and paired significance tests.

    python -m geobench.stats --ranker llama-3.1-8b

Reads results/unified/per_instance/<ranker>/*.csv and writes
  results/unified/summary/<ranker>_summary.csv     mean + 95% CI per (method, dataset, metric)
  results/unified/summary/<ranker>_overall.csv     per method, pooled over datasets
  results/unified/summary/<ranker>_pairwise.csv    paired Wilcoxon signed-rank on per-instance
                                                   NRG for every method pair (shared instances only)
  results/unified/summary/<ranker>_groups.csv      black-box vs white-box vs white-hat group tests

Why Wilcoxon: NRG is bounded in [-1,1] and heavily tied/non-normal on 8-10 item
lists; a paired rank test on the per-instance differences is the appropriate
test and is what C-SEO Bench also used.  Effect size = matched-pairs rank-
biserial correlation r = 1 - 2*W_minus/(n(n+1)/2)... reported as `rbc`.
"""
from __future__ import annotations

import argparse
import itertools
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy import stats as sps

from .config import METHOD_GROUPS, RESULTS_ROOT

METRICS = ["nrg", "success@0.1", "promote@0.1", "kvr", "ppl_r"]


def bootstrap_ci(x: np.ndarray, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return np.nan, np.nan, np.nan, 0
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    means = x[idx].mean(axis=1)
    return float(x.mean()), float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2)), int(len(x))


def load_per_instance(ranker: str) -> pd.DataFrame:
    d = RESULTS_ROOT / "per_instance" / ranker
    frames = [pd.read_csv(p) for p in sorted(d.glob("*.csv"))]
    if not frames:
        raise SystemExit(f"no per-instance files under {d}")
    df = pd.concat(frames, ignore_index=True)
    df["key"] = df.dataset + "|" + df.category + "|" + df.target_idx.astype(str)
    return df


def summarize(df: pd.DataFrame, n_boot: int) -> pd.DataFrame:
    rows = []
    for (m, ds), g in df.groupby(["method", "dataset"]):
        for met in METRICS:
            if met not in g:
                continue
            mean, lo, hi, n = bootstrap_ci(g[met].values, n_boot)
            rows.append({"method": m, "dataset": ds, "metric": met, "n": n, "mean": mean, "ci_lo": lo, "ci_hi": hi})
    return pd.DataFrame(rows)


def overall(df: pd.DataFrame, n_boot: int) -> pd.DataFrame:
    """Pooled over datasets with equal dataset weight (mean of per-dataset means,
    bootstrapped over instances within each dataset)."""
    rows = []
    for m, g in df.groupby("method"):
        for met in METRICS:
            if met not in g:
                continue
            per_ds = {ds: gg[met].dropna().values for ds, gg in g.groupby("dataset")}
            per_ds = {k: v for k, v in per_ds.items() if len(v)}
            if not per_ds:
                continue
            rng = np.random.default_rng(0)
            boots = []
            for _ in range(n_boot):
                boots.append(np.mean([rng.choice(v, size=len(v), replace=True).mean() for v in per_ds.values()]))
            rows.append({"method": m, "metric": met, "n_datasets": len(per_ds), "n": int(sum(map(len, per_ds.values()))),
                         "mean": float(np.mean([v.mean() for v in per_ds.values()])),
                         "ci_lo": float(np.quantile(boots, 0.025)), "ci_hi": float(np.quantile(boots, 0.975))})
    return pd.DataFrame(rows)


def paired_test(a: np.ndarray, b: np.ndarray) -> Dict[str, float]:
    d = a - b
    n = int(len(d))
    if n < 5 or np.all(d == 0):
        return {"n": n, "W": np.nan, "p": np.nan, "rbc": np.nan, "mean_diff": float(d.mean()) if n else np.nan}
    res = sps.wilcoxon(a, b, zero_method="wilcox", alternative="two-sided")
    nz = d[d != 0]
    ranks = sps.rankdata(np.abs(nz))
    w_plus = ranks[nz > 0].sum()
    w_minus = ranks[nz < 0].sum()
    rbc = (w_plus - w_minus) / (w_plus + w_minus)     # matched-pairs rank-biserial correlation
    return {"n": n, "W": float(res.statistic), "p": float(res.pvalue), "rbc": float(rbc), "mean_diff": float(d.mean())}


def pairwise(df: pd.DataFrame, metric: str = "nrg") -> pd.DataFrame:
    rows = []
    methods = sorted(df.method.unique())
    piv = df.pivot_table(index="key", columns="method", values=metric, aggfunc="first")
    for m1, m2 in itertools.combinations(methods, 2):
        both = piv[[m1, m2]].dropna()
        if both.empty:
            continue
        r = paired_test(both[m1].values, both[m2].values)
        rows.append({"metric": metric, "method_a": m1, "method_b": m2, **r})
    # per-dataset too
    for ds, g in df.groupby("dataset"):
        piv = g.pivot_table(index="key", columns="method", values=metric, aggfunc="first")
        for m1, m2 in itertools.combinations([m for m in methods if m in piv], 2):
            both = piv[[m1, m2]].dropna()
            if both.empty:
                continue
            r = paired_test(both[m1].values, both[m2].values)
            rows.append({"metric": metric, "dataset": ds, "method_a": m1, "method_b": m2, **r})
    out = pd.DataFrame(rows)
    if len(out) and "p" in out:
        if "dataset" not in out:
            out["dataset"] = np.nan
        out["family"] = out["dataset"].fillna("all")
        out["p_holm"] = np.nan
        for _, idx in out.groupby(["metric", "family"]).groups.items():
            out.loc[idx, "p_holm"] = holm(out.loc[idx, "p"].values)
        out = out.drop(columns=["family"])
    return out


def holm(p: np.ndarray) -> np.ndarray:
    """Holm step-down adjusted p-values (NaNs ignored)."""
    p = np.asarray(p, dtype=float)
    adj = np.full_like(p, np.nan)
    valid = np.where(~np.isnan(p))[0]
    m = len(valid)
    if m == 0:
        return adj
    order = valid[np.argsort(p[valid])]
    running = 0.0
    for i, oi in enumerate(order):
        running = max(running, (m - i) * p[oi])
        adj[oi] = min(1.0, running)
    return adj


def group_tests(df: pd.DataFrame, metric: str = "nrg") -> pd.DataFrame:
    """Best-in-group vs best-in-group on shared instances, plus group means."""
    rows = []
    inv = {m: g for g, ms in METHOD_GROUPS.items() for m in ms}
    df = df[df.method.isin(inv)].copy()
    df["group"] = df.method.map(inv)
    gm = df.groupby(["group", "method"])[metric].mean().reset_index()
    best = gm.sort_values(metric, ascending=False).groupby("group").head(1)
    best_of = dict(zip(best.group, best.method))
    piv = df.pivot_table(index="key", columns="method", values=metric, aggfunc="first")
    for g1, g2 in itertools.combinations(sorted(best_of), 2):
        m1, m2 = best_of[g1], best_of[g2]
        both = piv[[m1, m2]].dropna()
        if both.empty:
            continue
        rows.append({"metric": metric, "group_a": g1, "best_a": m1, "group_b": g2, "best_b": m2,
                     **paired_test(both[m1].values, both[m2].values)})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ranker", default="llama-3.1-8b")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--exclude", nargs="*", default=["clean"], help="methods to drop (default: clean baseline)")
    a = ap.parse_args()
    df = load_per_instance(a.ranker)
    df = df[~df.method.isin(a.exclude)]
    out = RESULTS_ROOT / "summary"
    out.mkdir(parents=True, exist_ok=True)
    s = summarize(df, a.n_boot); s.to_csv(out / f"{a.ranker}_summary.csv", index=False)
    o = overall(df, a.n_boot); o.to_csv(out / f"{a.ranker}_overall.csv", index=False)
    p = pd.concat([pairwise(df, "nrg"), pairwise(df, "kvr")], ignore_index=True); p.to_csv(out / f"{a.ranker}_pairwise.csv", index=False)
    g = group_tests(df, "nrg"); g.to_csv(out / f"{a.ranker}_groups.csv", index=False)
    print(o.pivot(index="method", columns="metric", values="mean").round(3).to_string())
    print(f"\n[stats] wrote 4 files under {out}")


if __name__ == "__main__":
    main()
