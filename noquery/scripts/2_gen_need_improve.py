import argparse
import json
import math
import os
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Use local implementation to avoid import issues
def load_changed_json_with_ids(changed_json_path: str):
    """Load changed_json and return records with integer IDs."""
    obj = json.loads(Path(changed_json_path).read_text(encoding="utf-8"))

    if isinstance(obj, list):
        data = obj
    elif isinstance(obj, dict):
        arr_keys = [k for k, v in obj.items() if isinstance(v, list)]
        if len(arr_keys) == 1:
            data = obj[arr_keys[0]]
        elif "books" in obj and isinstance(obj["books"], list):
            data = obj["books"]
        else:
            raise ValueError(
                "Unsupported changed_json structure: expected a list or a single array field."
            )
    else:
        raise ValueError("Unsupported changed_json structure: expected list or dict.")

    out = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        desc = item.get("description")
        if not isinstance(desc, str):
            continue
        did = item.get("id", i)
        try:
            did_int = int(did)
        except (ValueError, TypeError):
            did_int = i
        out.append((did_int, desc))

    return out


def _sample_ids(
    records: List[Tuple[int, str]],
    num: int | None,
    ratio: float,
    strategy: str,
    seed: int,
    min_chars: int,
) -> List[int]:
    random.seed(seed)
    # 预筛：可选长度阈值
    eligible = [(did, desc) for did, desc in records if len(desc) >= min_chars]
    if len(eligible) == 0:
        eligible = records[:]  # 若全被过滤，退化为全量

    n = len(eligible)
    k = num if (num is not None and num > 0) else max(1, min(n, int(math.ceil(n * ratio))))

    if strategy == "random":
        ids = [did for did, _ in eligible]
        if k >= len(ids):
            return ids
        return random.sample(ids, k)

    if strategy == "length_short":
        eligible.sort(key=lambda x: len(x[1]))
        return [did for did, _ in eligible[:k]]

    if strategy == "length_long":
        eligible.sort(key=lambda x: len(x[1]), reverse=True)
        return [did for did, _ in eligible[:k]]

    raise ValueError(f"Unsupported strategy: {strategy}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate need_improve json from changed_json")
    ap.add_argument("--changed_json", required=True)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--num", type=int, default=None, help="采样数量（与 ratio 二选一；优先 num）")
    ap.add_argument("--ratio", type=float, default=0.1, help="采样比例 [0,1]")
    ap.add_argument(
        "--strategy",
        choices=["random", "length_short", "length_long"],
        default="random",
        help="抽样策略：随机/优先短文本/优先长文本",
    )
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--min_chars", type=int, default=50, help="最小字符数过滤（仅用于初筛，不改变排序策略）")
    args = ap.parse_args()

    records = load_changed_json_with_ids(args.changed_json)
    doc_ids = _sample_ids(
        records,
        num=args.num,
        ratio=args.ratio,
        strategy=args.strategy,
        seed=args.seed,
        min_chars=args.min_chars,
    )

    out_obj: Dict[str, List[int]] = {"doc_ids": doc_ids}
    Path(args.out_json).write_text(json.dumps(out_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(doc_ids)} doc_ids to {args.out_json}")


if __name__ == "__main__":
    main()


