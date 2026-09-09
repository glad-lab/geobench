"""Shared helpers for attack runners that write the unified instance schema."""
from __future__ import annotations

import os
import json
from pathlib import Path
from typing import List, Optional

import pandas as pd

from ..config import RESULTS_ROOT
from ..data import load_category, load_manifest, query_noun
from ..api import ChatAPI, api_identity
from ..run_state import atomic_text, bind_config, digest, experiment_name, run_lock


class Generator:
    """Text generator used as *attacker* / *rewriter*: HF model or OpenAI-compatible API."""

    def __init__(self, model: str, temperature: float = 0.7, top_p: float = 0.9, max_new_tokens: int = 400,
                 dtype: str = "bfloat16"):
        self.model_name = model
        self.temperature, self.top_p, self.max_new_tokens = temperature, top_p, max_new_tokens
        self.api = model.startswith(("gpt-", "o1", "o3", "o4", "deepseek", "api:", "openai/"))
        if self.api:
            self.client = ChatAPI(model)
            self.model_name = model.removeprefix("api:")
        else:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.torch = torch
            self.tok = AutoTokenizer.from_pretrained(model)
            if self.tok.pad_token is None:
                self.tok.pad_token = self.tok.eos_token
            self.tok.padding_side = "left"
            self.model = AutoModelForCausalLM.from_pretrained(model, torch_dtype=getattr(torch, dtype), device_map="auto").eval()

    def __call__(self, system: Optional[str], user: str) -> str:
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
        if self.api:
            return self.client.complete(msgs, temperature=self.temperature, top_p=self.top_p,
                                        max_tokens=self.max_new_tokens)
        try:
            prompt = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        except Exception:
            prompt = self.tok.apply_chat_template([{"role": "user", "content": (system + "\n\n" if system else "") + user}],
                                                  tokenize=False, add_generation_prompt=True)
        enc = self.tok(prompt, return_tensors="pt", add_special_tokens=False).to(self.model.device)
        with self.torch.no_grad():
            out = self.model.generate(**enc, max_new_tokens=self.max_new_tokens, do_sample=self.temperature > 0,
                                      temperature=max(self.temperature, 1e-5), top_p=self.top_p,
                                      pad_token_id=self.tok.pad_token_id)
        return self.tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def iter_instances(datasets: List[str]):
    for ds in datasets:
        man = load_manifest(ds)
        for cat, grp in man.groupby("category", sort=True):
            items = load_category(ds, cat)
            for _, r in grp.iterrows():
                idx = int(r.target_idx)
                yield ds, cat, idx, items, query_noun(ds, cat)


def write_instances(rows: List[dict], method: str, tag: str = "") -> Path:
    name = experiment_name(method, tag)
    out = RESULTS_ROOT / "instances" / f"{name}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = [dict(r, method=name, base_method=method) for r in rows]
    atomic_text(out, pd.DataFrame(rows).to_csv(index=False))
    print(f"[{method}] wrote {len(rows)} rows -> {out}")
    return out


class GenerationRun:
    """Save each completed row atomically, with configuration-checked resume."""

    def __init__(self, method, tag, config, targets):
        self.name = experiment_name(method, tag)
        self.method = method
        self.path = RESULTS_ROOT / "instances" / f"{self.name}.csv"
        self.config = dict(config, schema=1, experiment=self.name, targets=digest([
            [ds, cat, idx, noun, [[it.name, it.text] for it in items]]
            for ds, cat, idx, items, noun in targets]))
        self.expected = {(ds, cat, idx) for ds, cat, idx, _, _ in targets}
        if len(self.expected) != len(targets) or not targets:
            raise ValueError("Targets must be nonempty and unique")
        self.rows = []
        self.done = set()

    def __enter__(self):
        self.lock = run_lock(self.path.with_suffix(".lock"))
        self.lock.__enter__()
        try:
            self.meta = bind_config(self.path, self.config)
            if self.path.exists():
                self.rows = pd.read_csv(self.path, keep_default_na=False).to_dict("records")
                self.done = {(r['dataset'], r['category'], int(r['target_idx'])) for r in self.rows}
                if (len(self.done) != len(self.rows) or not self.done <= self.expected
                        or any(r['method'] != self.name or not str(r['adv_text']).strip() for r in self.rows)):
                    raise ValueError(f"Invalid checkpoint: {self.path}")
            print(f"[{self.name}] resume {len(self.done)}/{len(self.expected)}", flush=True)
            return self
        except BaseException:
            self.lock.__exit__(None, None, None)
            raise

    def add(self, row):
        key = row['dataset'], row['category'], int(row['target_idx'])
        if key not in self.expected or key in self.done:
            raise ValueError(f"Unexpected or duplicate target: {key}")
        if not row['adv_text'].strip():
            raise ValueError("Empty generation; checkpoint not advanced")
        self.rows.append(dict(row, method=self.name, base_method=self.method))
        atomic_text(self.path, pd.DataFrame(self.rows).to_csv(index=False))
        self.done.add(key)
        if len(self.done) % 25 == 0:
            print(f"[{self.name}] saved {len(self.done)}/{len(self.expected)}", flush=True)

    def __exit__(self, kind, value, traceback):
        try:
            if kind is None and self.done == self.expected:
                atomic_text(self.meta, json.dumps({"config": self.config, "complete": True}, indent=2) + "\n")
        finally:
            self.lock.__exit__(kind, value, traceback)


def generation_identity(model):
    if model.startswith(("gpt-", "o1", "o3", "o4", "deepseek", "api:", "openai/")):
        return api_identity(model)
    return {"provider": "hf", "model": model}


def strip_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s[3:]
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3]
    return s.strip().strip('"').strip()
