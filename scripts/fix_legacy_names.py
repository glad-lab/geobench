"""One-off: the pre-sidecar evaluator named outputs by the `method` column, so the
Vicuna-optimised RAF set was scored as per_instance/<ranker>/raf.csv, while the
current evaluator names it raf__opt-vicuna-7b.csv.  Where both exist keep the
newer one; where only raf.csv exists rename it, and rewrite its method column.
"""
import sys, pandas as pd
from pathlib import Path
root = Path(sys.argv[1] if len(sys.argv) > 1 else "results/unified/per_instance")
for d in sorted(root.iterdir()):
    old, new = d / "raf.csv", d / "raf__opt-vicuna-7b.csv"
    if not old.exists():
        continue
    if new.exists():
        old.unlink(); print(f"{d.name}: removed duplicate raf.csv (kept raf__opt-vicuna-7b.csv)")
    else:
        df = pd.read_csv(old); df["method"] = "raf__opt-vicuna-7b"
        if "base_method" in df: df["base_method"] = "raf"
        df.to_csv(new, index=False); old.unlink(); print(f"{d.name}: renamed raf.csv -> raf__opt-vicuna-7b.csv")
