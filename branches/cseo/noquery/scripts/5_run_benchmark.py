import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd

# make noquery/src and legacy src importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
NOQUERY_SRC = os.path.join(PROJECT_ROOT, "noquery", "src")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if NOQUERY_SRC not in sys.path:
    sys.path.insert(0, NOQUERY_SRC)

from noquery.src.benchmark.engine import EngineNoQuery
from noquery.src.config.keys import OPENAI_API_KEY_FALLBACK


def _read_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_changed_texts(changed_json_path: str) -> dict[str, str]:
    obj = _read_json(changed_json_path)
    if isinstance(obj, list):
        data = obj
    elif isinstance(obj, dict):
        arr_keys = [k for k, v in obj.items() if isinstance(v, list)]
        if len(arr_keys) == 1:
            data = obj[arr_keys[0]]
        elif "books" in obj and isinstance(obj["books"], list):
            data = obj["books"]
        else:
            raise ValueError("Unsupported changed_json structure: expected a list or a single array field.")
    else:
        raise ValueError("Unsupported changed_json structure.")

    id2text: dict[str, str] = {}
    for i, item in enumerate(data):
        desc = item.get("description")
        if not isinstance(desc, str):
            continue
        did = item.get("id")
        if did is None:
            did = i
        id2text[str(did)] = desc
    return id2text


def main() -> None:
    ap = argparse.ArgumentParser(description="Run no-query benchmark using cohorts and boosted sets")
    ap.add_argument("--domain", default="books")
    ap.add_argument("--changed_json", required=True)
    ap.add_argument("--cohorts", required=True)
    ap.add_argument("--boosted", required=True)
    ap.add_argument("--improved_json", default=None, help="{doc_id: improved_text} mapping; omit for baseline")
    ap.add_argument("--method", default="baseline", help="baseline or method name")
    ap.add_argument("--llm_name", default="gpt-4o-2024-11-20")
    ap.add_argument("--developer_prompt", default=(
        "You are a book recommender. Answer strictly based on provided descriptions. "
        "After each sentence, immediately cite supporting items using [index] like [1][2]."
    ))
    ap.add_argument("--poll_interval", type=float, default=5.0)
    ap.add_argument("--max_wait_seconds", type=float, default=3600.0)
    ap.add_argument("--config", default="config.json")
    args = ap.parse_args()

    # API keys：环境变量 > config.json > 代码兜底
    cfg = _read_json(args.config)
    env_key = os.environ.get("OPENAI_API_KEY")
    file_key = cfg.get("OPENAI_API_KEY") if isinstance(cfg, dict) else None
    final_key = env_key or (file_key if file_key else OPENAI_API_KEY_FALLBACK)
    if final_key:
        os.environ["OPENAI_API_KEY"] = final_key

    from noquery.src.llms import OpenAIHelper  # late import, ensures env set

    # IO paths
    method_dir = "Original" if args.method == "baseline" else args.method
    adoption_dir = "AdoptionMode.NONE" if args.method == "baseline" else "AdoptionMode.UNILATERAL"
    running_folder = os.path.join(
        "experiments", "running", args.domain, method_dir, args.llm_name, adoption_dir
    )
    results_folder = running_folder.replace("running", "results")
    os.makedirs(results_folder, exist_ok=True)

    # Load inputs
    cohorts = _read_json(args.cohorts)
    boosted = _read_json(args.boosted)
    id2text = _load_changed_texts(args.changed_json)
    improved = None
    if args.improved_json:
        improved = _read_json(args.improved_json)

    # Run benchmark
    engine = EngineNoQuery(doc_type="Book Description")
    llm = OpenAIHelper(args.llm_name)
    batch_id = engine.run(
        cohorts=cohorts,
        boosted=boosted,
        id2text=id2text,
        improved=improved,
        method_name=args.method,
        developer_prompt=args.developer_prompt,
        llm=llm,
        running_folder=running_folder,
    )
    print(f"Submitted batch: {batch_id}")

    # Poll status
    start_time = time.monotonic()
    last = None
    while True:
        status = llm.get_status(batch_id)
        if status != last:
            print(f"Status: {status}")
            last = status
        if isinstance(status, str) and status.lower() in ("completed", "succeeded", "success"):
            break
        if isinstance(status, str) and status.lower() in ("failed", "error", "canceled", "cancelled"):
            raise RuntimeError(f"Batch {batch_id} ended with status: {status}")
        if time.monotonic() - start_time > args.max_wait_seconds:
            raise TimeoutError(f"Timed out after {args.max_wait_seconds}s waiting for batch {batch_id}")
        time.sleep(args.poll_interval)

    # Retrieve results and save parquet
    results, cost = llm.retrieve_results(batch_id)
    df = engine.process(results, results_folder)
    df.to_parquet(os.path.join(results_folder, "responses.parquet"), index=False)
    print(f"Saved to {results_folder}; Cost: {cost}")


if __name__ == "__main__":
    main()


