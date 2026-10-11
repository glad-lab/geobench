"""Regenerate the paper's Table 4 (main results), the cross-ranker table and
Figure 1 from results/unified/summary/*.csv.

    python -m geobench.make_tables --rankers llama-3.1-8b qwen2.5-7b mistral-7b gpt-4o-mini

Writes results/unified/tables/{table_main_<ranker>.tex, table_rankers.tex, fig_tradeoff_<ranker>.pdf}.
Rows are grouped by threat model (white-box gradient / black-box adversarial /
white-hat rewrite) and the best value is bolded *within each block* — the
per-paradigm sub-ranking reviewers asked for — with the cross-block best
underlined.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from .config import METHOD_GROUPS, METHOD_LABELS, PAPER_DATASETS, RESULTS_ROOT
from .run_state import base_method


def method_label(name, latex=False):
    base, _, tag = name.partition("__")
    label = METHOD_LABELS.get(base, base) + (f" [{tag}]" if tag else "")
    return label.replace("_", r"\_") if latex else label


def ordered_methods(available):
    return [name for methods in METHOD_GROUPS.values() for base in methods
            for name in sorted(set(available)) if base_method(name) == base]

DS_LABEL = {"ragroll": "Ragroll", "ragroll_sub": "Ragroll", "stsdata": "STSData", "rewrite_to_rank": "R2R",
            "llm_rank_optimizer": "LLM R. Opt.", "cseo": "C-SEO Bench", "llmrank": "LLMRank"}
MET_LABEL = {"nrg": "NRG", "success@0.1": "S@0.1", "promote@0.1": "P@0.1", "kvr": "KVR", "ppl_r": "PPL-R"}
HIGHER_BETTER = {"nrg": True, "success@0.1": True, "promote@0.1": True, "kvr": False, "ppl_r": None}


def _fmt(mean, lo, hi, metric):
    if np.isnan(mean):
        return "--"
    if metric in ("success@0.1", "promote@0.1"):
        return f"{mean:.2f}"
    return f"{mean:.2f} [{lo:.2f},{hi:.2f}]"


def _best_masks(vals: Dict[str, float], metric: str, groups: Dict[str, List[str]]):
    """Return (bold set, underline set) of method keys."""
    hb = HIGHER_BETTER[metric]
    if hb is None:      # PPL-R: closest to 1
        score = {m: -abs(v - 1) for m, v in vals.items() if not np.isnan(v)}
    else:
        score = {m: (v if hb else -v) for m, v in vals.items() if not np.isnan(v)}
    bold, under = set(), set()
    for g, ms in groups.items():
        cand = {m: score[m] for m in ms if m in score}
        if cand:
            bold.add(max(cand, key=cand.get))
    if score:
        under.add(max(score, key=score.get))
    return bold, under


def table_main(ranker: str, methods: List[str], datasets: List[str], out_dir: Path) -> Path:
    s = pd.read_csv(RESULTS_ROOT / "summary" / f"{ranker}_summary.csv")
    groups = {g: [m for m in methods if base_method(m) in ms] for g, ms in METHOD_GROUPS.items()}
    groups = {g: ms for g, ms in groups.items() if ms}
    cols = [m for ms in groups.values() for m in ms]
    lines = [r"\begin{tabular}{ll" + "c" * len(cols) + "}", r"\toprule",
             "Dataset & Metric & " + " & ".join(method_label(m, latex=True) for m in cols) + r" \\", r"\midrule"]
    for ds in datasets:
        sub = s[s.dataset == ds]
        if sub.empty:
            continue
        first = True
        for met in ["nrg", "success@0.1", "promote@0.1", "kvr", "ppl_r"]:
            vals = {m: sub[(sub.method == m) & (sub.metric == met)] for m in cols}
            means = {m: (float(v["mean"].iloc[0]) if len(v) else np.nan) for m, v in vals.items()}
            bold, under = _best_masks(means, met, groups)
            cells = []
            for m in cols:
                v = vals[m]
                txt = _fmt(means[m], float(v.ci_lo.iloc[0]) if len(v) else np.nan, float(v.ci_hi.iloc[0]) if len(v) else np.nan, met)
                if m in bold:
                    txt = r"\textbf{" + txt + "}"
                if m in under:
                    txt = r"\underline{" + txt + "}"
                cells.append(txt)
            n = int(sub[sub.metric == met]["n"].max()) if len(sub[sub.metric == met]) else 0
            lab = (DS_LABEL.get(ds, ds) + f" ($N$={n})") if first else ""
            first = False
            lines.append(f"{lab} & {MET_LABEL[met]} & " + " & ".join(cells) + r" \\")
        lines.append(r"\midrule")
    lines[-1] = r"\bottomrule"
    lines.append(r"\end{tabular}")
    out = out_dir / f"table_main_{ranker}.tex"
    out.write_text("\n".join(lines))
    return out


def table_rankers(rankers: List[str], methods: List[str], out_dir: Path) -> Path:
    """Method x ranker: mean NRG [CI] pooled over datasets, plus KVR."""
    frames = []
    for r in rankers:
        p = RESULTS_ROOT / "summary" / f"{r}_overall.csv"
        if p.exists():
            df = pd.read_csv(p); df["ranker"] = r; frames.append(df)
    if not frames:
        raise SystemExit("no overall summaries found; run geobench.stats per ranker first")
    o = pd.concat(frames)
    lines = [r"\begin{tabular}{l" + "c" * len(rankers) + "}", r"\toprule",
             "Method & " + " & ".join(rankers) + r" \\", r"\midrule"]
    for m in methods:
        cells = []
        for r in rankers:
            v = o[(o.method == m) & (o.ranker == r) & (o.metric == "nrg")]
            cells.append(_fmt(float(v["mean"].iloc[0]), float(v.ci_lo.iloc[0]), float(v.ci_hi.iloc[0]), "nrg") if len(v) else "--")
        lines.append(method_label(m, latex=True) + " & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    # Spearman correlation of method orderings between rankers (does the leaderboard flip?)
    piv = o[o.metric == "nrg"].pivot(index="method", columns="ranker", values="mean")
    corr = piv.corr(method="spearman")
    (out_dir / "ranker_order_spearman.csv").write_text(corr.to_csv())
    out = out_dir / "table_rankers.tex"
    out.write_text("\n".join(lines))
    return out


def fig_tradeoff(ranker: str, methods: List[str], out_dir: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    o = pd.read_csv(RESULTS_ROOT / "summary" / f"{ranker}_overall.csv")
    piv = o.pivot(index="method", columns="metric", values="mean")
    lo = o.pivot(index="method", columns="metric", values="ci_lo")
    hi = o.pivot(index="method", columns="metric", values="ci_hi")
    color = {"white_box_gradient": "#d62728", "black_box_adversarial": "#1f77b4", "white_hat_rewrite": "#2ca02c"}
    inv = {m: g for g, ms in METHOD_GROUPS.items() for m in ms}
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for m in methods:
        if m not in piv.index:
            continue
        x, y = piv.loc[m, "nrg"], piv.loc[m, "kvr"]
        size = 40 + 60 * float(np.clip(piv.loc[m].get("ppl_r", 1.0), 0, 8))
        ax.errorbar(x, y, xerr=[[x - lo.loc[m, "nrg"]], [hi.loc[m, "nrg"] - x]],
                    yerr=[[y - lo.loc[m, "kvr"]], [hi.loc[m, "kvr"] - y]], fmt="none", ecolor="#999", lw=0.8, zorder=1)
        ax.scatter(x, y, s=size, color=color.get(inv.get(base_method(m)), "#333"), alpha=0.8, edgecolor="k", lw=0.5, zorder=2)
        ax.annotate(method_label(m), (x, y), xytext=(5, 4), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Effectiveness: mean NRG (higher = stronger promotion)")
    ax.set_ylabel("Keyword violation rate (lower = stealthier)")
    ax.set_title(f"Effectiveness-stealth trade-off, ranker = {ranker}; marker size = PPL-R; bars = 95% CI", fontsize=8)
    ax.grid(alpha=0.3)
    out = out_dir / f"fig_tradeoff_{ranker}.pdf"
    fig.tight_layout(); fig.savefig(out); plt.close(fig)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rankers", nargs="+", default=["llama-3.1-8b"])
    ap.add_argument("--methods", nargs="+", default=None)
    ap.add_argument("--datasets", nargs="+", default=PAPER_DATASETS)
    a = ap.parse_args()
    out_dir = RESULTS_ROOT / "tables"; out_dir.mkdir(parents=True, exist_ok=True)
    for r in a.rankers:
        s = pd.read_csv(RESULTS_ROOT / "summary" / f"{r}_summary.csv")
        methods = a.methods or ordered_methods(s.method)
        print("wrote", table_main(r, methods, a.datasets, out_dir))
        print("wrote", fig_tradeoff(r, methods, out_dir))
    if len(a.rankers) > 1:
        s = pd.read_csv(RESULTS_ROOT / "summary" / f"{a.rankers[0]}_summary.csv")
        methods = a.methods or ordered_methods(s.method)
        print("wrote", table_rankers(a.rankers, methods, out_dir))


if __name__ == "__main__":
    main()
