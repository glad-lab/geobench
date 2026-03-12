import argparse
from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class MetricSpec:
    col: str
    mode: str  # "mean" or "meanpmstd"
    digits: int


METRICS = [
    MetricSpec("nrg", "meanpmstd", 3),
    MetricSpec("success@0.1", "mean", 3),
    MetricSpec("promote@0.1", "mean", 3),
    MetricSpec("kvr", "meanpmstd", 3),
    MetricSpec("ppl_r", "meanpmstd", 2),
]


def _fmt_mean(x: float, digits: int) -> str:
    if pd.isna(x):
        return "--"
    return f"{float(x):.{digits}f}"


def _fmt_mean_pm_std(mean: float, std: float, digits: int) -> str:
    if pd.isna(mean):
        return "--"
    if pd.isna(std):
        std = 0.0
    return f"{float(mean):.{digits}f} $\\pm$ {float(std):.{digits}f}"


def _safe_std(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    if len(s) <= 1:
        return float("nan")
    return float(s.std(ddof=1))


def _safe_mean(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    if len(s) == 0:
        return float("nan")
    return float(s.mean())


def _norm_dataset_name(alg: str) -> str:
    # Optional prettification for paper table naming
    mapping = {
        "llm-rank-optimizer": "LLM Rank Optimizer",
        "LLMRank": "LLM Rank",
        "RewriteToRank_Subsampled": "RewriteToRank",
    }
    return mapping.get(alg, alg)


def main() -> int:
    ap = argparse.ArgumentParser(description="Aggregate eval_matric/results_metrics.csv to LaTeX rows (mean ± std).")
    ap.add_argument("--csv", default="eval_matric/results_metrics.csv")
    ap.add_argument("--group_by", choices=["algorithm", "algorithm_dataset"], default="algorithm",
                    help="algorithm: aggregate over all categories per algorithm. "
                         "algorithm_dataset: treat algorithm as method and infer dataset from category (not recommended unless you have a convention).")
    ap.add_argument("--only_algorithm", default=None, help="Only output for a single algorithm name.")
    ap.add_argument("--tex_mode", choices=["rows", "tabular"], default="rows",
                    help="rows: print only body rows; tabular: print a full tabular environment snippet.")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    # Drop rows that are explicit failures
    if "error" in df.columns:
        df = df[df["error"].isna() | (df["error"].astype(str).str.strip() == "")]

    if args.only_algorithm:
        df = df[df["algorithm"] == args.only_algorithm]

    if len(df) == 0:
        raise SystemExit("No valid rows to aggregate (after filtering errors / algorithm).")

    group_cols = ["algorithm"]
    if args.group_by == "algorithm_dataset":
        # Placeholder: if you later add a dataset column, change this accordingly.
        group_cols = ["algorithm", "category"]

    lines: list[str] = []
    for keys, g in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        alg = str(keys[0])
        dataset = _norm_dataset_name(alg) if args.group_by == "algorithm" else str(keys[1])

        cells: list[str] = []
        for spec in METRICS:
            if spec.mode == "mean":
                cells.append(_fmt_mean(_safe_mean(g[spec.col]), spec.digits))
            else:
                m = _safe_mean(g[spec.col])
                s = _safe_std(g[spec.col])
                cells.append(_fmt_mean_pm_std(m, s, spec.digits))

        # This matches your paper.tex column order: NRG, Success@0.1, Promote@0.1, KVR, PPL-R
        line = f"{dataset} & " + " & ".join(cells) + r" \\"
        lines.append(line)

    lines = sorted(lines)

    if args.tex_mode == "tabular":
        header = r"\begin{tabular}{l|c|c|c|c|c}" + "\n" + r"\toprule" + "\n" + \
                 r"\textbf{Test Dataset} & \textbf{NRG} & \textbf{Success@0.1} & \textbf{Promote@0.1} & \textbf{KVR} & \textbf{PPL-R} \\" + "\n" + \
                 r"\midrule"
        footer = r"\bottomrule" + "\n" + r"\end{tabular}"
        print(header)
        for ln in lines:
            print(ln)
        print(footer)
    else:
        for ln in lines:
            print(ln)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

