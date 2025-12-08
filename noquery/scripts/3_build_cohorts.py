import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import random

import numpy as np

# make noquery/src importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
NOQUERY_SRC = os.path.join(PROJECT_ROOT, "noquery", "src")
if NOQUERY_SRC not in sys.path:
    sys.path.insert(0, NOQUERY_SRC)

import importlib.util
module_path = os.path.join(NOQUERY_SRC, "embeddings", "provider.py")
spec = importlib.util.spec_from_file_location("embeddings_provider", module_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot locate provider module at {module_path}")
embeddings_provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(embeddings_provider)
EmbeddingProvider = embeddings_provider.EmbeddingProvider
EmbeddingProviderConfig = embeddings_provider.EmbeddingProviderConfig


def _read_changed_json(path: str) -> List[Dict]:
    """
    Accepts either:
      - a top-level list of items
      - a top-level object with a single array field (e.g., {"books": [...]})
    Each item should contain a "description" string. If no id exists, we assign a sequential integer id.
    """
    obj = json.loads(Path(path).read_text(encoding="utf-8"))

    if isinstance(obj, list):
        data = obj
    elif isinstance(obj, dict):
        # prefer the only list field if possible
        arr_keys = [k for k, v in obj.items() if isinstance(v, list)]
        if len(arr_keys) == 1:
            data = obj[arr_keys[0]]
        elif "books" in obj and isinstance(obj["books"], list):
            data = obj["books"]
        else:
            raise ValueError("Unsupported changed_json structure: expected a list or a single array field.")
    else:
        raise ValueError("Unsupported changed_json structure: expected list or dict.")

    # normalize schema
    norm: List[Dict] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError("Each item must be an object with at least a 'description' field.")
        desc = item.get("description")
        if not isinstance(desc, str):
            raise ValueError("Each item must have a string field 'description'.")
        doc_id = item.get("id")
        if doc_id is None:
            doc_id = i
        norm.append({"doc_id": str(doc_id), "description": desc})
    return norm


def _read_need_improve(path: str) -> List[str]:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(obj, dict):
        if "doc_ids" in obj and isinstance(obj["doc_ids"], list):
            return [str(x) for x in obj["doc_ids"]]
        if "ids" in obj and isinstance(obj["ids"], list):
            return [str(x) for x in obj["ids"]]
    if isinstance(obj, list):
        return [str(x) for x in obj]
    raise ValueError("Unsupported need_improve format. Use {\"doc_ids\":[...]} or a list.")


def _build_hnsw_index(X: np.ndarray):
    try:
        import hnswlib  # type: ignore
    except Exception as exc:  # pragma: no cover
        return None

    dim = X.shape[1]
    idx = hnswlib.Index(space="cosine", dim=dim)
    idx.init_index(max_elements=X.shape[0], ef_construction=200, M=32)
    idx.add_items(X, np.arange(X.shape[0]))
    idx.set_ef(128)
    return idx


def _knn_query(index, X: np.ndarray, i: int, k: int) -> Tuple[np.ndarray, np.ndarray]:
    if index is not None:
        # hnswlib returns (labels, distances) for multiple queries
        labels, dists = index.knn_query(X[i : i + 1], k=k)
        # convert cosine distance -> similarity
        sims = 1.0 - dists[0]
        return labels[0], sims
    # fallback to sklearn
    from sklearn.neighbors import NearestNeighbors

    nn = NearestNeighbors(n_neighbors=k, metric="cosine")
    nn.fit(X)
    dists, labels = nn.kneighbors(X[i : i + 1], n_neighbors=k, return_distance=True)
    sims = 1.0 - dists[0]
    return labels[0], sims


def build_cohorts(
    docs: List[Dict],
    X: np.ndarray,
    need_improve_ids: List[str],
    cohort_size: int = 10,
    cohorts_per_doc: int = 2,
    tau_pos: float = 0.65,
    tau_dup: float = 0.95,
    tau_neg_low: float = 0.35,
    tau_neg_high: float = 0.50,
    seed: int = 42,
):
    rng = np.random.RandomState(seed)
    py_rng = random.Random(seed)
    id2idx = {d["doc_id"]: i for i, d in enumerate(docs)}
    idx2id = {i: d["doc_id"] for i, d in enumerate(docs)}

    index = _build_hnsw_index(X)

    cohorts: Dict[str, List[str]] = {}
    boosted: Dict[str, List[str]] = {}
    cohort_id = 0

    for doc_id in need_improve_ids:
        if doc_id not in id2idx:
            continue
        anchor = id2idx[doc_id]
        labels, sims = _knn_query(index, X, anchor, k=min(X.shape[0], 200))

        # remove self and near-duplicates
        candidates = [(int(lbl), float(sim)) for lbl, sim in zip(labels, sims) if int(lbl) != anchor and float(sim) < tau_dup]
        candidates.sort(key=lambda x: x[1], reverse=True)

        pos_pool = [j for j, s in candidates if s >= tau_pos]
        neg_pool = [j for j, s in candidates if tau_neg_low <= s <= tau_neg_high]

        # build multiple unique cohorts per target
        seen_groups: set[Tuple[str, ...]] = set()
        max_attempts = max(5, 3 * cohorts_per_doc)
        attempts = 0
        built = 0
        while built < cohorts_per_doc and attempts < max_attempts:
            attempts += 1
            group = [anchor]

            # 1) sample positives randomly without replacement
            pos_needed = max(0, cohort_size - 1)
            pos_candidates = [j for j in pos_pool if j not in group]
            py_rng.shuffle(pos_candidates)
            group.extend(pos_candidates[:pos_needed])

            # 2) add 0-2 boundary negatives randomly
            remaining_slots = max(0, cohort_size - len(group))
            if remaining_slots > 0 and len(neg_pool) > 0:
                extra_cnt = min(2, remaining_slots, len(neg_pool))
                extra = rng.choice(neg_pool, size=extra_cnt, replace=False).tolist()
                for j in extra:
                    if j not in group:
                        group.append(j)

            # 3) supplement from the rest of candidates in random order
            if len(group) < cohort_size:
                supplement = [j for j, _ in candidates if j not in group]
                py_rng.shuffle(supplement)
                need = cohort_size - len(group)
                group.extend(supplement[:need])

            # 4) trim and dedupe order-preserving
            dedup_group = list(dict.fromkeys(group))[:cohort_size]

            cohort_docs_tuple = tuple(idx2id[j] for j in dedup_group)
            if cohort_docs_tuple in seen_groups:
                continue
            seen_groups.add(cohort_docs_tuple)

            cohorts[str(cohort_id)] = list(cohort_docs_tuple)
            boosted[str(cohort_id)] = [doc_id]
            cohort_id += 1
            built += 1

    return cohorts, boosted


def main() -> None:
    ap = argparse.ArgumentParser(description="Build cohorts from changed_json using semantic similarity")
    ap.add_argument("--changed_json", required=True)
    ap.add_argument("--need_improve_json", required=True)
    ap.add_argument("--out_dir", default="experiments/books")
    ap.add_argument("--backend", choices=["local", "openai"], default="local")
    ap.add_argument("--model_name", default="bge-large-en-v1.5")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--batch_size", type=int, default=128)
    ap.add_argument("--cohort_size", type=int, default=10)
    ap.add_argument("--cohorts_per_doc", type=int, default=2)
    args = ap.parse_args()

    # Load API key from config.json if backend is openai
    api_key = None
    if args.backend == "openai":
        config_path = Path(PROJECT_ROOT) / "config.json"
        if config_path.exists():
            try:
                config_data = json.loads(config_path.read_text(encoding="utf-8"))
                api_key = config_data.get("OPENAI_API_KEY")
                if api_key:
                    os.environ["OPENAI_API_KEY"] = api_key
            except Exception as e:
                print(f"Warning: Failed to read config.json: {e}")

    docs = _read_changed_json(args.changed_json)
    texts = [d["description"] for d in docs]

    provider = EmbeddingProvider(
        EmbeddingProviderConfig(
            backend=args.backend,
            model_name=args.model_name,
            device=args.device,
            batch_size=args.batch_size,
            api_key=api_key,
        )
    )
    X = provider.embed_texts(texts)

    need_ids = _read_need_improve(args.need_improve_json)
    cohorts, boosted = build_cohorts(
        docs,
        X,
        need_ids,
        cohort_size=args.cohort_size,
        cohorts_per_doc=args.cohorts_per_doc,
    )

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "cohorts.json").write_text(json.dumps(cohorts, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "boosted.json").write_text(json.dumps(boosted, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved cohorts and boosted to: {out}")


if __name__ == "__main__":
    main()


