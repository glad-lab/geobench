"""Write the manifest datasets into each white-box branch's data folder, in the
Name/Natural JSONL layout the branch runners read, so a re-optimisation covers
exactly the manifest instances (same categories, same items, same text).

    python scripts/prepare_branch_data.py            # all three branches
    python scripts/prepare_branch_data.py --only sts

Targets (relative to repo root):
  Stealth-Rank : data2/ragroll, data2/json (STSData), benchmark_data/{cseo,rewrite_to_rank,llm_rank_optimizer}_subsampled
  RAF          : data2/u_{ragroll,stsdata,llmrankoptim,rewrite_to_rank,cseo}     (fresh dirs; old data2/* untouched)
  STS          : benchmark_data/{ragroll,sts,cseo,rewrite_to_rank,llm_rank_optimizer}_subsampled  (rank_opt.py restricts names)
Existing files with the same name are overwritten; nothing else is deleted.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("GEOBENCH_ROOT", str(ROOT))
from geobench.config import PAPER_DATASETS          # noqa: E402
from geobench.data import list_categories, load_category   # noqa: E402

LAYOUT = {
    "stealthrank": (ROOT / "branches/Stealth-Rank", {"ragroll": "data2/ragroll", "stsdata": "data2/json",
                    "cseo": "benchmark_data/cseo_subsampled", "rewrite_to_rank": "benchmark_data/rewrite_to_rank_subsampled",
                    "llm_rank_optimizer": "benchmark_data/llm_rank_optimizer_subsampled"}),
    "raf":         (ROOT / "branches/RAF", {"ragroll": "data2/u_ragroll", "stsdata": "data2/u_stsdata",
                    "cseo": "data2/u_cseo", "rewrite_to_rank": "data2/u_rewrite_to_rank",
                    "llm_rank_optimizer": "data2/u_llmrankoptim"}),
    "sts":         (ROOT / "branches/STS", {"ragroll": "benchmark_data/ragroll_subsampled", "stsdata": "benchmark_data/sts_subsampled",
                    "cseo": "benchmark_data/cseo_subsampled", "rewrite_to_rank": "benchmark_data/rewrite_to_rank_subsampled",
                    "llm_rank_optimizer": "benchmark_data/llm_rank_optimizer_subsampled"}),
}


def write(branch: str):
    base, dirs = LAYOUT[branch]
    n_files = n_items = 0
    for ds in PAPER_DATASETS:
        out = base / dirs[ds]
        out.mkdir(parents=True, exist_ok=True)
        for cat in list_categories(ds):
            items = load_category(ds, cat)
            with open(out / f"{cat}.jsonl", "w", encoding="utf-8") as f:
                for it in items:
                    f.write(json.dumps({"Name": it.name, "Natural": it.text}, ensure_ascii=False) + "\n")
            n_files += 1; n_items += len(items)
    print(f"[{branch}] wrote {n_files} category files / {n_items} items under {base.relative_to(ROOT)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", choices=list(LAYOUT), nargs="*", default=list(LAYOUT))
    for b in ap.parse_args().only:
        write(b)
