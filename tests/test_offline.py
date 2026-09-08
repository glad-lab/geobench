"""Offline tests (no GPU / network): prompt parsing, metrics, collect adapters,
the evaluate loop with a stub ranker, stats and table generation.
Run: python -m pytest -q tests
"""
import json
import os
import pathlib
import sys

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
os.environ["GEOBENCH_ROOT"] = str(ROOT)
sys.path.insert(0, str(ROOT))

from geobench.config import BAD_PHRASES, BAD_WORDS               # noqa: E402
from geobench.metrics import (aggregate_rank, instance_metrics, keyword_violation,  # noqa: E402
                              matched_keywords, nrg, promote, success)
from geobench.prompts import build_messages, parse_ranking, target_rank  # noqa: E402
from geobench.rankers import BaseRanker, orderings               # noqa: E402
from geobench.collect import _select_row, strip_span             # noqa: E402
from geobench import stats as st                                 # noqa: E402


def test_lexicon_sizes():
    assert len(BAD_WORDS) == 24
    assert len(BAD_PHRASES) == 54


def test_kvr_matches_branch_semantics():
    assert keyword_violation("This is the best choice.") == 1
    assert set(matched_keywords("This is the best choice.")) == {"best", "best choice"}
    assert keyword_violation("Topping is not top.") == 1          # 'top' whole-token
    assert keyword_violation("Topping only.") == 0                 # substring 'top' in 'topping' must NOT fire
    assert keyword_violation("Our #1 pick") == 1                   # '#' is kept for the '#1' phrase
    assert keyword_violation("A soft hoodie.") == 0


def test_metrics_definitions():
    assert nrg(10, 1, 10) == 1.0
    assert nrg(1, 11, 10) == -1.0                                  # clipped
    assert success(1, 10, 0.1) == 1 and success(2, 10, 0.1) == 0
    assert promote(1, 1, 10, 0.1) == 0                             # already in top: not a promotion
    assert promote(5, 1, 10, 0.1) == 1
    assert aggregate_rank([1, 4, 11, 3], "median") == 3.5
    assert aggregate_rank([1, 4, 11, 3], "min") == 1
    m = instance_metrics(7, 1, 10)
    assert m["nrg"] == pytest.approx(6 / 9) and m["promote@0.1"] == 1


def test_parse_ranking_variants():
    names = ["The Great Adventure", "Mystery of the Lost Key", "Alien Invasion", "Great"]
    reply = "Sure!\n1. **The Great Adventure** — epic\n2) 'Alien Invasion' by M. Star\n3. Mystery of the Lost Key\n"
    r = parse_ranking(reply, names)
    assert r == {"The Great Adventure": 1, "Alien Invasion": 2, "Mystery of the Lost Key": 3}
    assert target_rank(reply, names, "Great") == 5                 # absent -> L+1
    # longest-name-first prevents 'Great' from stealing 'The Great Adventure'
    assert target_rank("1. The Great Adventure\n2. Great", names, "Great") == 2


def test_prompt_single_line_products():
    msgs = build_messages("book", ["A", "B"], ["line one\n\nline two", "x"])
    body = msgs[1]["content"]
    assert "1. A: line one line two" in body and "2. B: x" in body


def test_orderings_seeded_and_identity_first():
    a = orderings(8, 5, seed=3); b = orderings(8, 5, seed=3)
    assert a == b and a[0] == list(range(8)) and len({tuple(p) for p in a}) >= 4


def test_select_row_best_prefers_latest_tie():
    df = pd.DataFrame({"iter": [0, 99, 199, 299], "attack_prompt": ["a", "b", "c", "d"], "product_rank": [4, 1, 3, 1]})
    assert _select_row(df, "best")["attack_prompt"] == "d"
    assert _select_row(df, "last")["attack_prompt"] == "d"
    assert strip_span('<span style="color:red;"> hi </span>') == "hi"


class StubRanker(BaseRanker):
    """Puts products containing 'BOOST' first, otherwise keeps listed order."""
    name = "stub"

    def generate(self, batch):
        outs = []
        for msgs in batch:
            block = msgs[1]["content"].split("Products:\n")[1].split("\n\nThe order")[0]
            lines = block.split("\n")
            names = [l.split(". ", 1)[1].split(": ", 1)[0] for l in lines]
            boosted = [n for n, l in zip(names, lines) if "BOOST" in l]
            order = boosted + [n for n in names if n not in boosted]
            outs.append("\n".join(f"{i}. {n}" for i, n in enumerate(order, 1)))
        return outs


def test_evaluate_stats_tables_roundtrip(tmp_path, monkeypatch):
    from geobench import evaluate as ev, config
    monkeypatch.setattr(config, "RESULTS_ROOT", tmp_path)
    monkeypatch.setattr(ev, "RESULTS_ROOT", tmp_path)
    monkeypatch.setattr(st, "RESULTS_ROOT", tmp_path)
    from geobench import make_tables as mt
    monkeypatch.setattr(mt, "RESULTS_ROOT", tmp_path)
    # synthetic dataset
    dsdir = tmp_path / "Datasets" / "Datasets_subsampled_all" / "STSData"
    dsdir.mkdir(parents=True)
    with open(dsdir / "books.jsonl", "w") as f:
        for i in range(10):
            f.write(json.dumps({"Name": f"Book {i}", "Natural": f"desc {i}"}) + "\n")
    monkeypatch.setattr(config, "DATA_ROOT", tmp_path / "Datasets")
    monkeypatch.setattr(config, "MANIFEST_ROOT", tmp_path / "manifests")
    from geobench import data
    monkeypatch.setattr(data, "DATA_ROOT", tmp_path / "Datasets")
    monkeypatch.setattr(data, "MANIFEST_ROOT", tmp_path / "manifests")
    rows = []
    for method, suf in [("stealthrank", " BOOST"), ("zero_shot", " meh"), ("clean", "")]:
        for idx in range(1, 11):
            rows.append({"method": method, "dataset": "stsdata", "category": "books", "target_idx": idx,
                         "target_name": f"Book {idx-1}", "L": 10, "orig_text": f"desc {idx-1}",
                         "adv_suffix": suf.strip(), "adv_text": f"desc {idx-1}{suf}", "select_rule": "best", "source_path": ""})
    inst = pd.DataFrame(rows)
    for m, sub in inst.groupby("method"):
        ev.evaluate(sub, "stub", K=4, agg="median", seed=0, ppl=None, out_path=tmp_path / "per_instance" / "stub" / f"{m}.csv", ranker=StubRanker())
    pi = pd.read_csv(tmp_path / "per_instance" / "stub" / "stealthrank.csv")
    assert (pi.r_after == 1).all() and pi.nrg.mean() > 0.3
    clean = pd.read_csv(tmp_path / "per_instance" / "stub" / "clean.csv")
    assert (clean.nrg == 0).all()
    # resume: second call adds nothing
    ev.evaluate(inst[inst.method == "stealthrank"], "stub", K=4, agg="median", seed=0, ppl=None,
                out_path=tmp_path / "per_instance" / "stub" / "stealthrank.csv", ranker=StubRanker())
    assert len(pd.read_csv(tmp_path / "per_instance" / "stub" / "stealthrank.csv")) == 10
    df = st.load_per_instance("stub"); df = df[df.method != "clean"]
    s = st.summarize(df, 200); o = st.overall(df, 200); p = st.pairwise(df, "nrg")
    assert set(s.method) == {"stealthrank", "zero_shot"} and (s.ci_lo <= s["mean"]).all()
    assert p.iloc[0].n == 10 and p.iloc[0].p < 0.05
    (tmp_path / "summary").mkdir(exist_ok=True)
    s.to_csv(tmp_path / "summary" / "stub_summary.csv", index=False); o.to_csv(tmp_path / "summary" / "stub_overall.csv", index=False)
    out = mt.table_main("stub", ["stealthrank", "zero_shot"], ["stsdata"], tmp_path)
    assert r"\textbf" in out.read_text()


def test_holm():
    import numpy as np
    adj = st.holm(np.array([0.01, 0.04, 0.03, np.nan]))
    assert adj[0] == pytest.approx(0.03) and adj[1] == pytest.approx(0.06) and np.isnan(adj[3])
