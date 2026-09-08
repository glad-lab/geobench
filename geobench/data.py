"""Dataset loading and instance manifests.

An *instance* is (dataset, category, target_idx): one target item inside one
candidate list.  The manifest freezes the exact set of instances every method
is scored on, so N is identical across methods and paired tests are valid.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

import pandas as pd

from .config import DATASETS, DATA_ROOT, MANIFEST_ROOT, QUERY_NOUN_OVERRIDES


@dataclass
class Item:
    name: str
    text: str            # natural-language description used in the ranking prompt
    raw: dict            # original JSON record


def item_text(rec: dict) -> str:
    """Description shown to the ranker.

    `Natural` when present (Ragroll, STSData, RewriteToRank, C-SEO); otherwise
    flatten the remaining fields (llm-rank-optimizer catalogs have Author/
    Description/Price/... and no Natural) — same fallback STS/rank_opt.py uses.
    """
    if "Natural" in rec and isinstance(rec["Natural"], str) and rec["Natural"].strip():
        return rec["Natural"].strip()
    if "description" in rec and isinstance(rec["description"], str) and rec["description"].strip():
        return rec["description"].strip()
    parts = [f"{k}: {v}" for k, v in rec.items() if k not in ("Name", "name")]
    return "; ".join(parts)


def item_name(rec: dict) -> str:
    return str(rec.get("Name", rec.get("name", ""))).strip()


def dataset_dir(dataset: str) -> Path:
    if dataset not in DATASETS:
        raise KeyError(f"unknown dataset {dataset!r}; known: {sorted(DATASETS)}")
    return DATA_ROOT / DATASETS[dataset][0]


def list_categories(dataset: str) -> List[str]:
    return sorted(p.stem for p in dataset_dir(dataset).glob("*.jsonl"))


def load_category(dataset: str, category: str) -> List[Item]:
    path = dataset_dir(dataset) / f"{category}.jsonl"
    items: List[Item] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            items.append(Item(name=item_name(rec), text=item_text(rec), raw=rec))
    return items


def query_noun(dataset: str, category: str) -> str:
    noun = DATASETS[dataset][1]
    if noun:
        return noun
    if category in QUERY_NOUN_OVERRIDES:
        return QUERY_NOUN_OVERRIDES[category]
    return category.replace("_", " ").strip()


# --------------------------------------------------------------------------- #
# Manifests
# --------------------------------------------------------------------------- #
def build_manifest(dataset: str) -> pd.DataFrame:
    rows = []
    for cat in list_categories(dataset):
        items = load_category(dataset, cat)
        for idx, it in enumerate(items, start=1):     # 1-based, matches every branch
            rows.append({
                "dataset": dataset, "category": cat, "target_idx": idx,
                "target_name": it.name, "L": len(items),
                "query_noun": query_noun(dataset, cat),
            })
    return pd.DataFrame(rows)


def manifest_path(dataset: str) -> Path:
    return MANIFEST_ROOT / f"{dataset}.csv"


def write_manifest(dataset: str) -> Path:
    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    df = build_manifest(dataset)
    out = manifest_path(dataset)
    df.to_csv(out, index=False)
    return out


def load_manifest(dataset: str) -> pd.DataFrame:
    p = manifest_path(dataset)
    if not p.exists():
        write_manifest(dataset)
    return pd.read_csv(p)


def instance_key(dataset: str, category: str, target_idx: int) -> str:
    return f"{dataset}|{category}|{int(target_idx)}"


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Write instance manifests (one CSV per dataset).")
    ap.add_argument("datasets", nargs="*", default=list(DATASETS))
    a = ap.parse_args()
    for d in a.datasets:
        p = write_manifest(d)
        df = pd.read_csv(p)
        print(f"{d:20s} {df.category.nunique():3d} categories {len(df):4d} instances -> {p}")
