"""Explicit API transports; importing this module never loads a wallet or calls a model."""
from __future__ import annotations

import os
import time
import json
import threading
from pathlib import Path
from urllib.parse import urlsplit

_usage_lock = threading.Lock()


def api_identity(model: str) -> dict:
    model = model.removeprefix("api:")
    provider = os.environ.get("GEOBENCH_API_PROVIDER", "openai")
    if provider not in {"openai", "blockrun", "blockrun-openai"}:
        raise ValueError(f"Unknown GEOBENCH_API_PROVIDER: {provider}")
    if provider.startswith("blockrun"):
        if "/" not in model:
            model = ("deepseek/" if model.startswith("deepseek") else "openai/") + model
        if model.startswith("blockrun/"):
            raise ValueError("Automatic model routing is not allowed for experiments")
    endpoint = (os.environ.get("BLOCKRUN_API_URL", "https://blockrun.ai/api")
                if provider == "blockrun" else os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    if provider == "blockrun-openai" and not os.environ.get("OPENAI_BASE_URL"):
        raise ValueError("Set OPENAI_BASE_URL to your BlockRun bearer-compatible endpoint")
    url = urlsplit(endpoint)
    if url.username or url.password or url.query or url.fragment:
        raise ValueError("API endpoint must not contain credentials, query parameters or fragments")
    return {"provider": provider, "model": model, "endpoint": endpoint.rstrip("/"),
            "allow_truncated": os.environ.get("GEOBENCH_ALLOW_TRUNCATED", "0") == "1"}


class ChatAPI:
    def __init__(self, model: str):
        self.identity = api_identity(model)
        if self.identity["provider"] == "blockrun":
            from blockrun_llm import LLMClient
            self.client = LLMClient(api_url=self.identity["endpoint"])
        else:
            from openai import OpenAI
            self.client = OpenAI(base_url=self.identity["endpoint"], max_retries=0)

    def complete(self, messages, **parameters) -> str:
        for attempt in range(6):
            try:
                if self.identity["provider"] == "blockrun":
                    response = self.client.chat_completion(
                        model=self.identity["model"], messages=messages,
                        fallback_models=None, **parameters)
                else:
                    response = self.client.chat.completions.create(
                        model=self.identity["model"], messages=messages, **parameters)
                log_path = os.environ.get("GEOBENCH_USAGE_LOG")
                if log_path:
                    usage = getattr(response, "usage", None)
                    record = {"timestamp": time.time(), "model": getattr(response, "model", None),
                              "prompt_tokens": getattr(usage, "prompt_tokens", None),
                              "completion_tokens": getattr(usage, "completion_tokens", None),
                              "finish_reason": response.choices[0].finish_reason}
                    with _usage_lock:
                        path = Path(log_path)
                        path.parent.mkdir(parents=True, exist_ok=True)
                        with path.open("a") as log:
                            log.write(json.dumps(record) + "\n")
                break
            except Exception as exc:
                # Payment/guardrail/auth/invalid-request failures must stop immediately.
                import httpx
                status = getattr(exc, "status_code", None)
                transient = status == 429 or (isinstance(status, int) and status >= 500)
                transient |= isinstance(exc, (httpx.TransportError, TimeoutError, ConnectionError))
                transient |= type(exc).__name__ in {"APIConnectionError", "APITimeoutError"}
                if "payment" in type(exc).__name__.lower() or "spendlimit" in type(exc).__name__.lower():
                    transient = False
                if not transient or attempt == 5:
                    raise
                print(f"[api] {type(exc).__name__}; retry in {2 ** attempt}s", flush=True)
                time.sleep(2 ** attempt)
        if getattr(response, "fallback", None):
            raise ValueError("API substituted a fallback model; response not saved")
        served = getattr(response, "model", None)
        requested = self.identity["model"].split("/")[-1]
        if served:
            served = served.split("/")[-1]
            if served != requested and not served.startswith(requested + "-"):
                raise ValueError(f"Unexpected served model: {served}; expected {requested}")
        choice = response.choices[0]
        text = choice.message.content
        if not isinstance(text, str) or not text.strip():
            raise ValueError("API returned an empty/non-text completion; response not saved")
        reason = getattr(choice, "finish_reason", None)
        if reason == "content_filter" or (reason == "length" and not self.identity["allow_truncated"]):
            raise ValueError("API returned a truncated or filtered completion; response not saved")
        return text.strip()
