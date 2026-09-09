"""Atomic checkpoints and stable experiment identities for paid runs."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED


def api_workers():
    value = int(os.environ.get("GEOBENCH_API_WORKERS", "1"))
    if not 1 <= value <= 64:
        raise ValueError("GEOBENCH_API_WORKERS must be between 1 and 64")
    return value


def completed_calls(fn, inputs, workers=1):
    """Bound in-flight work; on failure drain successful work before raising."""
    if workers == 1:
        for item in inputs:
            yield fn(item)
        return
    iterator = iter(inputs)
    failure = None
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = set()
        for _ in range(workers):
            try:
                pending.add(pool.submit(fn, next(iterator)))
            except StopIteration:
                break
        while pending:
            finished, pending = wait(pending, return_when=FIRST_COMPLETED)
            results = []
            for future in finished:
                try:
                    results.append(future.result())
                except Exception as exc:
                    failure = failure or exc
            for result in results:
                yield result
            if failure is None:
                for _ in finished:
                    try:
                        pending.add(pool.submit(fn, next(iterator)))
                    except StopIteration:
                        break
    if failure is not None:
        raise failure


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def experiment_name(method: str, tag: str = "") -> str:
    name = f"{method}__{tag}" if tag else method
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", name):
        raise ValueError(f"Invalid experiment name: {name!r}")
    return name


def base_method(name: str) -> str:
    return name.split("__", 1)[0]


def atomic_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@contextmanager
def run_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError(f"Another process is writing this experiment: {path}") from None
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def bind_config(output: Path, config: dict) -> Path:
    """Refuse to resume a changed/untracked run before spending more money."""
    meta = output.with_suffix(".run.json")
    if meta.exists():
        if json.loads(meta.read_text())["config"] != config:
            raise ValueError(f"Run configuration/input changed for {output}; use a new tag or results directory")
    elif output.exists() and output.stat().st_size:
        raise ValueError(f"Existing output has no resume metadata: {output}; use a new results directory")
    else:
        atomic_text(meta, json.dumps({"config": config, "complete": False}, indent=2) + "\n")
    return meta
