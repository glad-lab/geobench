"""Paid-run regressions: all clients are fakes and network access is forbidden."""
import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from geobench import api, evaluate as ev, stats
from geobench.attacks import common, cseo_rewrite, zero_shot
from geobench.rankers import BaseRanker, OpenAIRanker
from geobench.run_state import run_lock


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Network access forbidden in offline tests")
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setenv("GEOBENCH_API_PROVIDER", "blockrun")
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("BLOCKRUN_API_URL", raising=False)


def response(text="A useful completion", model="openai/gpt-4o-mini", **kwargs):
    return SimpleNamespace(model=model, choices=[SimpleNamespace(
        message=SimpleNamespace(content=text), finish_reason="stop")], **kwargs)


def test_blockrun_shared_transport_and_model_mapping(monkeypatch):
    calls = []
    class Client:
        def __init__(self, **kwargs):
            assert kwargs == {"api_url": "https://blockrun.ai/api"}
        def chat_completion(self, **kwargs):
            calls.append(kwargs)
            return response(model="gpt-4o-mini-2024-07-18")
    monkeypatch.setitem(sys.modules, "blockrun_llm", SimpleNamespace(LLMClient=Client))
    gen = common.Generator("openai/gpt-4o-mini", temperature=0.7, top_p=0.9, max_new_tokens=600)
    assert gen("system", "rewrite") == "A useful completion"
    ranker = OpenAIRanker("gpt-4o-mini")
    assert ranker.generate([[{"role": "user", "content": "rank"}]]) == ["A useful completion"]
    assert all(c["model"] == "openai/gpt-4o-mini" and c["fallback_models"] is None for c in calls)
    assert calls[0]["max_tokens"] == 600 and calls[0]["top_p"] == 0.9
    assert calls[1]["temperature"] == 0 and calls[1]["max_tokens"] == 512


def test_bearer_compatible_transport(monkeypatch):
    monkeypatch.setenv("GEOBENCH_API_PROVIDER", "blockrun-openai")
    with pytest.raises(ValueError, match="OPENAI_BASE_URL"):
        api.api_identity("gpt-4o-mini")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://proxy.example/v1")
    calls = []
    class Client:
        def __init__(self, **kwargs):
            assert kwargs == {"base_url": "https://proxy.example/v1", "max_retries": 0}
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))
        def create(self, **kwargs):
            calls.append(kwargs)
            return response()
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=Client))
    api.ChatAPI("gpt-4o-mini").complete([], max_tokens=60)
    assert calls[0]["model"] == "openai/gpt-4o-mini"
    assert "fallback_models" not in calls[0]
    monkeypatch.setenv("GEOBENCH_API_PROVIDER", "openai")
    assert api.api_identity("gpt-4o-mini")["model"] == "gpt-4o-mini"


def test_installed_sdk_http_contract(monkeypatch):
    import httpx
    from blockrun_llm import LLMClient
    calls = []
    def handler(request):
        calls.append(json.loads(request.content))
        assert request.url.path == "/api/v1/chat/completions"
        return httpx.Response(200, json={
            "id": "offline-test", "object": "chat.completion", "created": 0,
            "model": "openai/gpt-4o-mini",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "SDK parsed"},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}})
    # A public, unfunded test key is used only for local SDK construction.
    # All HTTP is intercepted; no real wallet is read and no payment is signed.
    monkeypatch.delenv("BLOCKRUN_TX_LOG", raising=False)
    sdk = LLMClient(private_key="0x" + "11" * 32, api_url="https://blockrun.ai/api")
    sdk._client.close()
    sdk._client = httpx.Client(transport=httpx.MockTransport(handler))
    client = object.__new__(api.ChatAPI)
    client.identity = api.api_identity("gpt-4o-mini")
    client.client = sdk
    try:
        assert client.complete([{"role": "user", "content": "offline"}], max_tokens=60) == "SDK parsed"
    finally:
        sdk._client.close()
    assert len(calls) == 1 and calls[0]["model"] == "openai/gpt-4o-mini"


@pytest.mark.parametrize("error_name,status,retries", [
    ("PaymentError", 500, 0), ("SpendLimitError", None, 0),
    ("AuthenticationError", 401, 0), ("RateLimitError", 429, 1),
])
def test_retry_only_transient_errors(monkeypatch, error_name, status, retries):
    error = type(error_name, (Exception,), {"status_code": status})
    calls = []
    client = object.__new__(api.ChatAPI)
    client.identity = api.api_identity("gpt-4o-mini")
    def complete(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise error("failure")
        return response()
    client.client = SimpleNamespace(chat_completion=complete)
    waits = []
    monkeypatch.setattr(api.time, "sleep", waits.append)
    if retries:
        assert client.complete([]) == "A useful completion"
    else:
        with pytest.raises(error):
            client.complete([])
    assert len(calls) == 1 + retries and len(waits) == retries


@pytest.mark.parametrize("reply", [response(text=""), response(model="other-model"),
                                     response(fallback={"model": "other-model"})])
def test_invalid_response_not_accepted(reply):
    client = object.__new__(api.ChatAPI)
    client.identity = api.api_identity("gpt-4o-mini")
    client.client = SimpleNamespace(chat_completion=lambda **kw: reply)
    with pytest.raises(ValueError):
        client.complete([])


@pytest.fixture
def targets():
    return list(common.iter_instances(["stsdata"]))[:3]


def test_generation_failure_resume_and_config_guard(tmp_path, monkeypatch, targets):
    monkeypatch.setattr(common, "RESULTS_ROOT", tmp_path)
    monkeypatch.setattr(zero_shot, "iter_instances", lambda _: iter(targets))
    calls = []
    class Generator:
        def __init__(self, *args): pass
        def __call__(self, system, user):
            calls.append(user)
            if len(calls) == 3:
                raise RuntimeError("injected interruption")
            return "A useful suffix"
    monkeypatch.setattr(zero_shot, "Generator", Generator)
    args = ["zero_shot", "--attacker", "gpt-4o-mini", "--tag", "att-gpt4omini"]
    monkeypatch.setattr(sys, "argv", args)
    with pytest.raises(RuntimeError, match="interruption"):
        zero_shot.main()
    out = tmp_path / "instances/zero_shot__att-gpt4omini.csv"
    assert len(pd.read_csv(out)) == 2
    with pytest.raises(ValueError, match="incomplete"):
        ev.read_instances(out)
    zero_shot.main()
    assert len(calls) == 4 and len(ev.read_instances(out)) == 3
    assert set(pd.read_csv(out).method) == {"zero_shot__att-gpt4omini"}
    # A completed run must not even instantiate the API client again.
    monkeypatch.setattr(zero_shot, "Generator", lambda *a: pytest.fail("duplicate paid initialization"))
    zero_shot.main()
    monkeypatch.setattr(sys, "argv", args + ["--temperature", "0.1"])
    with pytest.raises(ValueError, match="configuration/input changed"):
        zero_shot.main()
    assert len(calls) == 4


@pytest.mark.parametrize('workers', [1, 3])
def test_all_rewrite_strategies_resume(tmp_path, monkeypatch, targets, workers):
    monkeypatch.setenv('GEOBENCH_API_WORKERS', str(workers))
    monkeypatch.setattr(common, "RESULTS_ROOT", tmp_path)
    monkeypatch.setattr(cseo_rewrite, "iter_instances", lambda _: iter(targets))
    calls = []
    class Generator:
        def __init__(self, *args): pass
        def __call__(self, system, user):
            calls.append(user)
            return "Rewritten source"
    monkeypatch.setattr(cseo_rewrite, "Generator", Generator)
    monkeypatch.setattr(sys, "argv", ["cseo_rewrite", "--rewriter", "gpt-4o-mini"])
    cseo_rewrite.main()
    cseo_rewrite.main()
    assert len(calls) == 30
    outputs = list((tmp_path / "instances").glob("*.csv"))
    assert len(outputs) == 10
    for out in outputs:
        frame = ev.read_instances(out)
        assert len(frame) == 3
        if out.stem == "llm_guidance":
            assert (frame.adv_text == "Rewritten source\n\n" + frame.orig_text).all()


class CountingRanker(BaseRanker):
    name = "stub"
    def __init__(self): self.calls = 0
    def rank(self, noun, names, texts, target, K=10, seed=0):
        self.calls += K
        return [1 if any("BOOST" in text for text in texts) else len(names)] * K


def test_variants_evaluate_and_statistics_separately(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, "RESULTS_ROOT", tmp_path)
    monkeypatch.setattr(stats, "RESULTS_ROOT", tmp_path)
    old = pd.read_csv("results/unified/instances/zero_shot.csv", keep_default_na=False).head(6)
    new = old.copy()
    new["adv_text"] = "BOOST new attack"
    old_path = tmp_path / "zero_shot.csv"
    new_path = tmp_path / "zero_shot__att-gpt4omini.csv"
    old.to_csv(old_path, index=False)
    new.to_csv(new_path, index=False)  # legacy tagged file, row method still zero_shot
    ranker = CountingRanker()
    monkeypatch.setattr(ev, "load_ranker", lambda *a, **kw: ranker)
    monkeypatch.setattr(sys, "argv", ["evaluate", "--instances", str(old_path), str(new_path),
                                     "--ranker", "stub", "--K", "2", "--no-ppl"])
    ev.main()
    assert ranker.calls == 36  # 12 clean, 12 old attack, 12 new attack
    ev.main()
    assert ranker.calls == 36
    result = stats.load_per_instance("stub")
    assert set(result.method) == {"zero_shot", "zero_shot__att-gpt4omini"}
    assert len(result) == 12
    summary = stats.summarize(result, 20)
    assert set(summary.method) == set(result.method)
    assert stats.pairwise(result).iloc[0]["n"] == 6
    from geobench import make_tables as mt
    monkeypatch.setattr(mt, "RESULTS_ROOT", tmp_path)
    (tmp_path / "summary").mkdir()
    summary.to_csv(tmp_path / "summary/stub_summary.csv", index=False)
    methods = mt.ordered_methods(result.method)
    table = mt.table_main("stub", methods, list(result.dataset.unique()), tmp_path).read_text()
    assert "Zero-Shot [att-gpt4omini]" in table
    # Changed protocol or attacks must not silently reuse old output.
    monkeypatch.setattr(sys, "argv", sys.argv + ["--seed", "7"])
    with pytest.raises(ValueError, match="configuration/input changed"):
        ev.main()
    assert ranker.calls == 36


def test_exclusive_checkpoint_lock(tmp_path):
    with run_lock(tmp_path / "test.lock"):
        with pytest.raises(RuntimeError, match="Another process"):
            with run_lock(tmp_path / "test.lock"):
                pass


def test_parallel_failure_drains_successful_inflight_work():
    import threading
    from geobench.run_state import completed_calls
    barrier = threading.Barrier(3)
    def work(i):
        if i < 3:
            barrier.wait(timeout=5)
        if i == 0:
            raise RuntimeError('one request failed')
        return i
    saved = []
    with pytest.raises(RuntimeError, match='one request failed'):
        for result in completed_calls(work, range(6), workers=3):
            saved.append(result)
    assert {1, 2} <= set(saved)
    assert len(saved) == len(set(saved))


def test_parallel_evaluation_preserves_protocol(tmp_path, monkeypatch):
    import threading
    frame = ev.read_instances(Path('results/unified/instances/zero_shot.csv')).head(6)
    class ParallelRanker(CountingRanker, OpenAIRanker):
        def __init__(self):
            self.name = 'stub'
            self.calls = 0
            self.lock = threading.Lock()
        def rank(self, *args, **kwargs):
            with self.lock:
                return super().rank(*args, **kwargs)
    outputs = []
    for workers in (1, 3):
        root = tmp_path / str(workers)
        monkeypatch.setattr(ev, 'RESULTS_ROOT', root)
        monkeypatch.setenv('GEOBENCH_API_WORKERS', str(workers))
        ranker = ParallelRanker()
        out = root / 'zero_shot.csv'
        ev.evaluate(frame, 'stub', 10, 'median', 0, None, out, ranker=ranker)
        assert ranker.calls == 120
        outputs.append(pd.read_csv(out).sort_values(['dataset', 'category', 'target_idx']).reset_index(drop=True))
    pd.testing.assert_frame_equal(*outputs)


@pytest.mark.parametrize("first", ["old", "tagged"])
def test_variant_added_in_later_invocation(tmp_path, monkeypatch, first):
    """An already completed variant must not suppress a later, different variant."""
    monkeypatch.setattr(ev, "RESULTS_ROOT", tmp_path)
    monkeypatch.setattr(stats, "RESULTS_ROOT", tmp_path)
    old = pd.read_csv("results/unified/instances/zero_shot.csv", keep_default_na=False).head(6)
    new = old.copy()
    new["adv_text"] = "BOOST different attack"
    paths = {"old": tmp_path / "zero_shot.csv",
             "tagged": tmp_path / "zero_shot__att-gpt4omini.csv"}
    old.to_csv(paths["old"], index=False)
    new.to_csv(paths["tagged"], index=False)
    ranker = CountingRanker()
    monkeypatch.setattr(ev, "load_ranker", lambda *a, **kw: ranker)

    def run(*selected):
        monkeypatch.setattr(sys, "argv", ["evaluate", "--ranker", "stub", "--K", "10",
                                         "--no-ppl", "--instances", *map(str, selected)])
        ev.main()

    run(paths[first])
    assert ranker.calls == 120  # six clean and six manipulated lists, K=10
    run(paths["tagged" if first == "old" else "old"])
    assert ranker.calls == 180  # new variant incurs all 60 required ranking calls
    for method in ("zero_shot", "zero_shot__att-gpt4omini"):
        out = tmp_path / "per_instance" / "stub" / f"{method}.csv"
        frame = pd.read_csv(out)
        assert len(frame) == 6 and set(frame.method) == {method}
    run(paths["old"], paths["tagged"])
    assert ranker.calls == 180  # only now are both experiments legitimately complete
    result = stats.load_per_instance("stub")
    means = result.groupby("method").r_after.mean()
    assert means["zero_shot__att-gpt4omini"] == 1
    assert means["zero_shot"] > means["zero_shot__att-gpt4omini"]
    summary = stats.summarize(result, 20)
    assert len(summary[summary.metric == "nrg"]) == 2


def test_local_launcher_dry_run_and_bad_paths(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    env = dict(os.environ, REPO=str(repo), PYTHON_BIN=sys.executable,
               DRY_RUN="1", GEOBENCH_RESULTS=str(repo / "results/unified"))
    script = str(repo / "scripts/slurm/submit_eval_api.sh")
    result = subprocess.run(["bash", script], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "no API calls" in result.stdout and "Started" not in result.stdout
    env["REPO"] = str(tmp_path / "missing")
    result = subprocess.run(["bash", script], env=env, capture_output=True, text=True)
    assert result.returncode != 0 and "Invalid geobench REPO" in result.stderr
