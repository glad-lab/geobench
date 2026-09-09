"""Ranker backends.  Every backend exposes

    rank(noun, names, texts, target, K, seed) -> list[int]   (K ranks, 1..L+1)

The K calls use K different random product orderings (seeded, so the same
orderings are used for the clean and the manipulated list of an instance).
Decoding is greedy / temperature 0 so ordering is the only source of variance.
"""
from __future__ import annotations

import os
import random
import time
from typing import List, Optional, Sequence

from .config import RANKERS
from .prompts import build_messages, target_rank
from .api import ChatAPI


def orderings(L: int, K: int, seed: int) -> List[List[int]]:
    """K permutations of range(L); the first is the identity so K=1 is deterministic."""
    rng = random.Random(seed)
    out = [list(range(L))]
    while len(out) < K:
        p = list(range(L))
        rng.shuffle(p)
        out.append(p)
    return out[:K]


class BaseRanker:
    name: str = "base"
    max_new_tokens: int = 512

    def generate(self, batch_messages: List[List[dict]]) -> List[str]:
        raise NotImplementedError

    def rank(self, noun: str, names: Sequence[str], texts: Sequence[str], target: str,
             K: int = 10, seed: int = 0) -> List[int]:
        L = len(names)
        perms = orderings(L, K, seed)
        batch = []
        for p in perms:
            batch.append(build_messages(noun, [names[i] for i in p], [texts[i] for i in p]))
        replies = self.generate(batch)
        return [target_rank(r, names, target) for r in replies]


# --------------------------------------------------------------------------- #
class HFRanker(BaseRanker):
    def __init__(self, model_id: str, dtype: str = "bfloat16", device_map: str = "auto",
                 batch_size: int = 10, max_new_tokens: int = 512):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.name = model_id
        self.batch_size = batch_size
        self.max_new_tokens = max_new_tokens
        self.tok = AutoTokenizer.from_pretrained(model_id)
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        self.tok.padding_side = "left"
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=getattr(torch, dtype), device_map=device_map
        ).eval()
        self._torch = torch

    def _render(self, messages: List[dict]) -> str:
        kw = {}
        # Qwen3 thinking mode would bury the list in <think>; turn it off.
        if "qwen3" in self.name.lower():
            kw["enable_thinking"] = False
        try:
            return self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, **kw)
        except Exception:
            # Models without a system role (e.g. gemma): fold system into user.
            sys_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
            user = [m for m in messages if m["role"] != "system"]
            user[0] = {"role": "user", "content": sys_msg + "\n\n" + user[0]["content"]}
            return self.tok.apply_chat_template(user, tokenize=False, add_generation_prompt=True, **kw)

    def generate(self, batch_messages: List[List[dict]]) -> List[str]:
        torch = self._torch
        outs: List[str] = []
        for s in range(0, len(batch_messages), self.batch_size):
            chunk = [self._render(m) for m in batch_messages[s:s + self.batch_size]]
            enc = self.tok(chunk, return_tensors="pt", padding=True, add_special_tokens=False).to(self.model.device)
            with torch.no_grad():
                gen = self.model.generate(
                    **enc, max_new_tokens=self.max_new_tokens, do_sample=False,
                    pad_token_id=self.tok.pad_token_id,
                )
            gen = gen[:, enc["input_ids"].shape[1]:]
            outs.extend(self.tok.batch_decode(gen, skip_special_tokens=True))
        return outs


# --------------------------------------------------------------------------- #
class OpenAIRanker(BaseRanker):
    """Chat-completions backend.  Works for OpenAI, or any OpenAI-compatible
    server (vLLM, Together, DeepSeek) via OPENAI_BASE_URL / OPENAI_API_KEY."""

    def __init__(self, model_id: str, max_new_tokens: int = 512, sleep: float = 0.0):
        self.name = model_id
        self.client = ChatAPI(model_id)
        self.identity = self.client.identity
        self.max_new_tokens = max_new_tokens
        self.sleep = sleep

    def _one(self, messages: List[dict]) -> str:
        text = self.client.complete(messages, temperature=0, max_tokens=self.max_new_tokens)
        if self.sleep:
            time.sleep(self.sleep)
        return text

    def generate(self, batch_messages: List[List[dict]]) -> List[str]:
        return [self._one(m) for m in batch_messages]


class AnthropicRanker(BaseRanker):
    def __init__(self, model_id: str, max_new_tokens: int = 512):
        import anthropic
        self.name = model_id
        self.client = anthropic.Anthropic()
        self.max_new_tokens = max_new_tokens

    def _one(self, messages: List[dict]) -> str:
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        user = [m for m in messages if m["role"] != "system"]
        for attempt in range(6):
            try:
                r = self.client.messages.create(
                    model=self.name, system=system, messages=user,
                    max_tokens=self.max_new_tokens, temperature=0,
                )
                return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
            except Exception as e:
                time.sleep(2 ** attempt)
                print(f"[anthropic] {e!r}")
        raise RuntimeError("anthropic ranker: too many failures")

    def generate(self, batch_messages: List[List[dict]]) -> List[str]:
        return [self._one(m) for m in batch_messages]


# --------------------------------------------------------------------------- #
def load_ranker(key: str, **kw) -> BaseRanker:
    if key in RANKERS:
        backend, model_id = RANKERS[key]
    elif "/" in key:                      # raw HF id
        backend, model_id = "hf", key
    else:
        raise KeyError(f"unknown ranker {key!r}; known: {sorted(RANKERS)} or a HF model id")
    if backend == "hf":
        return HFRanker(model_id, **kw)
    if backend == "openai":
        return OpenAIRanker(model_id, **{k: v for k, v in kw.items() if k in ("max_new_tokens", "sleep")})
    if backend == "anthropic":
        return AnthropicRanker(model_id, **{k: v for k, v in kw.items() if k in ("max_new_tokens",)})
    raise ValueError(backend)
