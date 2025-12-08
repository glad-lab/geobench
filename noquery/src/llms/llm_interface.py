from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple


class LLMInterface(ABC):
    llm_name: str
    BATCH_PRICES: dict

    @abstractmethod
    def create_message(self, user_query: str, list_docs: Optional[list] = None) -> Tuple[list, str]:
        raise NotImplementedError

    @abstractmethod
    def create_request(
        self,
        messages: list,
        system: str,
        i: int,
        max_completion_tokens: int = 8192,
        reasoning_effort: Optional[str] = None,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    def run_batch(self, list_requests: List[dict], output_folder: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def retrieve_results(self, batch_id: str) -> Tuple[Optional[List[str]], Optional[float]]:
        raise NotImplementedError

    @abstractmethod
    def retrieve_text_response(self, response: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_status(self, batch_id: str) -> str:
        raise NotImplementedError

    def calculate_api_call_cost(self, response: Any, input_cost: float, output_cost: float) -> float:  # optional
        # 可按需由具体实现覆盖；此处提供兜底实现
        return 0.0


