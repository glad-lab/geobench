import argparse
import os

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


def calculate_diffs(df_baseline: pd.DataFrame, df_method: pd.DataFrame, max_citations: int = 5):
    diffs = []
    n = min(len(df_baseline), len(df_method))
    b = df_baseline.reset_index(drop=True)
    m = df_method.reset_index(drop=True)

    for i in range(n):
        base_order = b.loc[i, "Citation Order"]
        meth_order = m.loc[i, "Citation Order"]
        if isinstance(base_order, np.ndarray):
            base_order = base_order.tolist()[:max_citations]
        if isinstance(meth_order, np.ndarray):
            meth_order = meth_order.tolist()[:max_citations]

        boosted_items = m.loc[i, "Boost Product Index"]
        if not isinstance(boosted_items, list):
            boosted_items = [boosted_items]

        for item in boosted_items:
            if (item in base_order) and (item in meth_order):
                diffs.append(base_order.index(item) - meth_order.index(item))
            elif (item in base_order) and (item not in meth_order):
                diffs.append(base_order.index(item) - len(meth_order))
            elif (item not in base_order) and (item in meth_order):
                diffs.append(len(base_order) - meth_order.index(item))
            else:
                diffs.append(0)
    return diffs


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate no-query C-SEO using Wilcoxon test")
    ap.add_argument("--domain", default="books")
    ap.add_argument("--method", default="Statistics")
    ap.add_argument("--llm_name", default="gpt-5-nano-2025-08-07")
    args = ap.parse_args()

    base_path = os.path.join("experiments", "results", args.domain, "Original", args.llm_name, "AdoptionMode.NONE")
    meth_path = os.path.join("experiments", "results", args.domain, args.method, args.llm_name, "AdoptionMode.UNILATERAL")

    df_base = pd.read_parquet(os.path.join(base_path, "responses.parquet"))
    df_meth = pd.read_parquet(os.path.join(meth_path, "responses.parquet"))

    diffs = calculate_diffs(df_base, df_meth)
    if len(diffs) == 0:
        print("No diffs found.")
        return
    stat, p = wilcoxon(diffs, alternative="greater")
    mean = float(np.mean(diffs))
    std = float(np.std(diffs))
    print({"statistic": float(stat), "pvalue": float(p), "Delta Rank": (mean, std), "count": len(diffs)})


if __name__ == "__main__":
    main()


