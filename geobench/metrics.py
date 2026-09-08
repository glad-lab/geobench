"""Metric definitions (paper Appendix C), implemented once.

r_before, r_after in {1, ..., L+1}; L+1 = target absent from the reply.
"""
from __future__ import annotations

import math
import re
from typing import Iterable, Optional, Sequence

from .config import ALPHAS, BAD_PHRASES, BAD_WORDS


def aggregate_rank(ranks: Sequence[int], how: str = "median") -> float:
    """Collapse K ordering-level ranks into one rank for the instance."""
    xs = sorted(ranks)
    if how == "median":
        n = len(xs)
        return float(xs[n // 2]) if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])
    if how == "mean":
        return float(sum(xs) / len(xs))
    if how == "min":
        return float(xs[0])
    raise ValueError(how)


def nrg(r_before: float, r_after: float, L: int) -> float:
    """Normalized Rank Gain, clipped to [-1, 1]  (Eq. 1-2)."""
    raw = (r_before - r_after) / (L - 1)
    return max(-1.0, min(1.0, raw))


def top_alpha(L: int, alpha: float) -> int:
    return math.ceil(alpha * L)


def success(r_after: float, L: int, alpha: float) -> int:
    """Success@alpha (Eq. 3)."""
    return int(r_after <= top_alpha(L, alpha))


def promote(r_before: float, r_after: float, L: int, alpha: float) -> int:
    """Promote@alpha (Eq. 4): moved from outside the top-alpha region into it."""
    t = top_alpha(L, alpha)
    return int(r_before > t and r_after <= t)


# --------------------------------------------------------------------------- #
# KVR — identical to every branch's contains_bad_phrase()
# --------------------------------------------------------------------------- #
_PUNCT = re.compile(r"[^\w\s#]")


def keyword_violation(text: str) -> int:
    if not isinstance(text, str):
        return 0
    cleaned = _PUNCT.sub("", text.lower())
    tokens = cleaned.split()
    joined = " ".join(tokens)
    for phrase in BAD_PHRASES:
        if phrase in joined:
            return 1
    for w in BAD_WORDS:
        if w in tokens:
            return 1
    return 0


def matched_keywords(text: str) -> list:
    """Which lexicon entries fired (for the appendix / error analysis)."""
    cleaned = _PUNCT.sub("", (text or "").lower())
    tokens = set(cleaned.split())
    joined = " ".join(cleaned.split())
    hits = [p for p in BAD_PHRASES if p in joined] + [w for w in BAD_WORDS if w in tokens]
    return sorted(hits)


# --------------------------------------------------------------------------- #
# Perplexity ratio
# --------------------------------------------------------------------------- #
class Perplexity:
    """PPL under a fixed reference LM (paper: Vicuna-7B, fp16)."""

    def __init__(self, model_id: str, dtype: str = "float16", device: Optional[str] = None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=getattr(torch, dtype)).to(self.device).eval()

    def __call__(self, text: str) -> float:
        if not isinstance(text, str) or not text.strip():
            return float("nan")
        enc = self.tok(text, return_tensors="pt", truncation=True, max_length=2048).to(self.device)
        with self.torch.no_grad():
            out = self.model(**enc, labels=enc["input_ids"])
        loss = out.loss
        if loss is None or not self.torch.isfinite(loss):
            return float("nan")
        return float(self.torch.exp(loss).item())


def ppl_ratio(ppl_orig: float, ppl_adv: float) -> float:
    if not (math.isfinite(ppl_orig) and math.isfinite(ppl_adv)) or ppl_orig <= 0:
        return float("nan")
    return ppl_adv / ppl_orig


def instance_metrics(r_before: float, r_after: float, L: int) -> dict:
    d = {"nrg": nrg(r_before, r_after, L)}
    for a in ALPHAS:
        tag = f"{a:g}"
        d[f"success@{tag}"] = success(r_after, L, a)
        d[f"promote@{tag}"] = promote(r_before, r_after, L, a)
    return d
