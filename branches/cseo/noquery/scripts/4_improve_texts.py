import argparse
import json
import os
import sys
import time
from pathlib import Path

# Make noquery.src importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import shared utilities
from noquery.src.llms import OpenAIHelper
from noquery.src.utils import (
    load_changed_json,
    load_need_improve,
    setup_api_keys,
    create_method_instance,
    list_available_methods,
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Improve target descriptions and save as {doc_id: improved_text}")
    ap.add_argument("--changed_json", required=True)
    ap.add_argument("--need_improve_json", required=True)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--llm_name", default="gpt-4o-2024-11-20")
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--method", default="ContentImprovement")
    ap.add_argument("--poll_interval", type=float, default=5.0)
    ap.add_argument("--max_wait_seconds", type=float, default=3600.0)
    args = ap.parse_args()

    # Set up API keys using shared utility
    setup_api_keys(args.config)

    # Load data using shared utilities
    need_ids = load_need_improve(args.need_improve_json)
    id2text = load_changed_json(args.changed_json, return_as_dict=True)

    # Validate method name
    available_methods = list_available_methods()
    if args.method not in available_methods:
        raise ValueError(
            f"Unsupported method: {args.method}. "
            f"Available methods: {', '.join(available_methods)}"
        )

    # prepare inputs ordered by need_ids and keep mapping index->doc_id
    idx_map = []
    list_texts = []
    for did in need_ids:
        original = id2text.get(did)
        if not original:
            continue
        list_texts.append(original)
        idx_map.append(did)

    # Build batch via method class to reuse prompt templates and post_processing
    helper = OpenAIHelper(args.llm_name)
    method_inst = create_method_instance(args.method, helper)

    out_dir = Path("experiments") / "running" / "improve" / args.method / args.llm_name
    out_dir.mkdir(parents=True, exist_ok=True)
    batch_id = method_inst.improve_texts(list_texts, str(out_dir))
    print(f"Submitted batch: {batch_id}")

    # Poll until completion (legacy style)
    start_time = time.monotonic()
    last_status = None
    while True:
        status = helper.get_status(batch_id)
        if status != last_status:
            print(f"Status for {args.method}: {status}")
            last_status = status
        s = str(status).lower()
        if s in ("completed", "succeeded", "success"):
            break
        if s in ("failed", "error", "canceled", "cancelled"):
            raise RuntimeError(f"Batch {batch_id} ended with status: {status}")
        if time.monotonic() - start_time > args.max_wait_seconds:
            raise TimeoutError(
                f"Timed out after {args.max_wait_seconds}s waiting for batch {batch_id}. Last status: {status}"
            )
        time.sleep(args.poll_interval)

    # Fetch results when completed
    results, total_cost = helper.retrieve_results(batch_id)

    # Apply method-specific post-processing if any (skip failed/missing)
    improved = {}
    failed = []
    max_i = min(len(results), len(idx_map))
    for i in range(max_i):
        txt = results[i]
        did = idx_map[i]
        if isinstance(txt, str) and len(txt) > 0:
            improved[did] = method_inst.post_processing(txt)
        else:
            failed.append({"index": i, "doc_id": did})

    Path(args.out_json).write_text(json.dumps(improved, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved improved texts to {args.out_json}")

    # write a brief summary for observability
    summary = {
        "batch_id": batch_id,
        "method": args.method,
        "llm_name": args.llm_name,
        "num_requests": len(list_texts),
        "num_success": len(improved),
        "num_failed": len(failed),
        "total_cost": total_cost,
        "out_json": str(args.out_json),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    if failed:
        (out_dir / "failed.json").write_text(json.dumps(failed, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Warning: {len(failed)} items failed or missing. Details saved to failed.json")


if __name__ == "__main__":
    main()


