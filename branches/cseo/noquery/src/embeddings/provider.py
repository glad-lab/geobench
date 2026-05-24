import os
from dataclasses import dataclass
from typing import Iterable, List, Literal, Optional

import numpy as np


BackendType = Literal["openai", "local"]

# ⚠️ 警告：请勿在此文件中硬编码API密钥！
# 使用优先级：环境变量 OPENAI_API_KEY > EmbeddingProviderConfig.api_key > 抛出错误
# 请通过环境变量、config.json或.env文件设置API密钥
OPENAI_API_KEY_FALLBACK: str = ""  # 已移除硬编码密钥


@dataclass
class EmbeddingProviderConfig:
    backend: BackendType = "local"
    model_name: str = "bge-large-en-v1.5"
    device: str = "cpu"  # only for local
    batch_size: int = 128
    api_key: Optional[str] = None  # 仅当 backend=openai 时可用


class EmbeddingProvider:
    """
    A minimal embedding provider that supports two backends:
    - openai: uses OpenAI Embeddings API (e.g., text-embedding-3-large)
    - local: uses sentence-transformers (e.g., BAAI/bge-large-en-v1.5)

    The embed_texts method always returns a float32 numpy array with row-wise L2 normalization applied.
    """

    def __init__(self, config: EmbeddingProviderConfig) -> None:
        self.config = config
        self._client = None
        self._model = None

        if self.config.backend == "openai":
            try:
                from openai import OpenAI  # type: ignore
            except Exception as exc:  # pragma: no cover
                raise RuntimeError(
                    "openai package is required for backend 'openai'"
                ) from exc
            # 读取顺序：环境变量 > 配置传入 > 文件内常量
            api_key = (
                os.environ.get("OPENAI_API_KEY")
                or self.config.api_key
                or OPENAI_API_KEY_FALLBACK
            )
            if not api_key:
                raise EnvironmentError("OPENAI_API_KEY is not set (env/config/fallback all empty).")
            # 确保 openai 客户端能读取到
            os.environ["OPENAI_API_KEY"] = api_key
            self._client = OpenAI()
        elif self.config.backend == "local":
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
            except Exception as exc:  # pragma: no cover
                raise RuntimeError(
                    "sentence-transformers is required for backend 'local'"
                ) from exc
            self._model = SentenceTransformer(self.config.model_name, device=self.config.device)
        else:
            raise ValueError(f"Unsupported backend: {self.config.backend}")

    def _chunks(self, seq: List[str], size: int) -> Iterable[List[str]]:
        for i in range(0, len(seq), size):
            yield seq[i : i + size]

    def _l2_normalize(self, x: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
        return (x / norms).astype("float32")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if len(texts) == 0:
            return np.zeros((0, 1), dtype="float32")

        if self.config.backend == "openai":
            from openai import RateLimitError  # type: ignore

            vectors: List[np.ndarray] = []
            for chunk in self._chunks(texts, self.config.batch_size):
                resp = self._client.embeddings.create(
                    model=self.config.model_name,
                    input=chunk,
                )
                # Preserve order
                chunk_vecs = [np.array(d.embedding, dtype="float32") for d in resp.data]
                vectors.append(np.vstack(chunk_vecs))
            X = np.vstack(vectors)
            return self._l2_normalize(X)

        if self.config.backend == "local":
            # sentence-transformers supports batching internally
            X = self._model.encode(
                texts,
                batch_size=self.config.batch_size,
                show_progress_bar=True,
                normalize_embeddings=False,
            )
            if not isinstance(X, np.ndarray):
                X = np.array(X)
            return self._l2_normalize(X)

        raise AssertionError("Unreachable backend branch")


