"""Shared helpers for attack runners that write the unified instance schema."""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import List, Optional

import pandas as pd

from ..config import RESULTS_ROOT
from ..data import load_category, load_manifest, query_noun


class Generator:
    """Text generator used as *attacker* / *rewriter*: HF model or OpenAI-compatible API."""

    def __init__(self, model: str, temperature: float = 0.7, top_p: float = 0.9, max_new_tokens: int = 400,
                 dtype: str = "bfloat16"):
        self.model_name = model
        self.temperature, self.top_p, self.max_new_tokens = temperature, top_p, max_new_tokens
        self.api = model.startswith(("gpt-", "o1", "o3", "o4", "deepseek", "api:"))
        if self.api:
            from openai import OpenAI
            self.client = OpenAI(base_url=os.environ.get("OPENAI_BASE_URL"))
            self.model_name = model.replace("api:", "")
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
            for attempt in range(6):
                try:
                    r = self.client.chat.completions.create(model=self.model_name, messages=msgs,
                                                            temperature=self.temperature, top_p=self.top_p,
                                                            max_tokens=self.max_new_tokens)
                    return (r.choices[0].message.content or "").strip()
                except Exception as e:
                    print(f"[gen] {e!r}; retry"); time.sleep(2 ** attempt)
            raise RuntimeError("generator failed")
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
    out = RESULTS_ROOT / "instances" / (f"{method}{('__' + tag) if tag else ''}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"[{method}] wrote {len(rows)} rows -> {out}")
    return out


def strip_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s[3:]
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3]
    return s.strip().strip('"').strip()
