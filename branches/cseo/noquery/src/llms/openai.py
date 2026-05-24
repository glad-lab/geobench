import json
import os
from typing import List, Optional, Tuple

from openai import OpenAI


def _get_json_list(jsonl_text: str) -> List[dict]:
    return [json.loads(line) for line in jsonl_text.split("\n") if line]


class OpenAIHelper:
    def __init__(self, llm_name: str) -> None:
        # 不做交互式输入，依赖环境变量或外部脚本注入
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            # 保持与上层脚本的职责分离：如果为空，交由调用方处理
            raise EnvironmentError("OPENAI_API_KEY not set. Set env or via config before init OpenAIHelper.")
        self.llm_name = llm_name
        self.client = OpenAI()

        # 仅保留必要条目；如需更多模型可在此扩展
        self.BATCH_PRICES = {
            "gpt-5-nano-2025-08-07": {"input": 0.025, "output": 0.2},
        }

    def create_message(self, user_query: str, list_docs: Optional[list] = None) -> Tuple[list, str]:
        messages = [
            {
                "role": "user",
                "content": user_query,
            }
        ]
        raw_prompt = "User: " + user_query
        return messages, raw_prompt

    def create_request(
        self,
        messages: list,
        system: str,
        i: int,
        max_completion_tokens: int = 8192,
        reasoning_effort: Optional[str] = None,
    ) -> dict:
        if system:
            # 使用 system 角色；与批处理兼容
            messages = [{"role": "system", "content": system}] + messages
        request = {
            "custom_id": f"request-{i}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": self.llm_name,
                "messages": messages,
                "max_completion_tokens": max_completion_tokens,
            },
        }
        if self.llm_name.startswith("o1") or self.llm_name.startswith("o3"):
            request["body"]["reasoning_effort"] = reasoning_effort
        return request

    def run_batch(self, list_requests: List[dict], output_folder: str) -> str:
        # 1) 保存为 JSONL
        requests_path = os.path.join(output_folder, "requests.jsonl")
        with open(requests_path, "w", encoding="utf-8") as f:
            for req in list_requests:
                f.write(json.dumps(req, ensure_ascii=False) + "\n")

        # 2) 上传文件并创建批处理
        batch_input_file = self.client.files.create(file=open(requests_path, "rb"), purpose="batch")

        meta_path = os.path.join(output_folder, "metadata.jsonl")
        with open(meta_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"batch_input_file_id": batch_input_file.id}) + "\n")

        batch = self.client.batches.create(
            input_file_id=batch_input_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"description": output_folder},
        )

        with open(meta_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"batch_response_id": batch.id}) + "\n")

        return batch.id

    def retrieve_text_response(self, response: dict) -> str:
        """
        Robustly extract assistant text from a batch response line.
        Supports both legacy string content and new structured content arrays.
        """
        try:
            message = response["response"]["body"]["choices"][0]["message"]
        except Exception:
            return ""

        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    text_val = item.get("text")
                    if isinstance(text_val, str):
                        parts.append(text_val)
                    # some variants may use nested `content`
                    nested = item.get("content")
                    if isinstance(nested, str):
                        parts.append(nested)
            return "\n".join([p for p in parts if p]).strip()
        return ""

    def retrieve_results(self, batch_id: str):
        status = self.client.batches.retrieve(batch_id)
        if status.status != "completed":
            print("Batch not completed yet")
            return None, None

        list_results = _get_json_list(self.client.files.content(status.output_file_id).text)
        sorted_texts = [None] * status.request_counts.total
        for result in list_results:
            i = int(result["custom_id"].split("-")[-1])
            sorted_texts[i] = self.retrieve_text_response(result)

        # 可选：计算成本（若无价格映射则返回 None）
        total_cost = None
        try:
            input_price = self.BATCH_PRICES[self.llm_name]["input"]
            output_price = self.BATCH_PRICES[self.llm_name]["output"]
            total_cost = 0.0
            for r in list_results:
                usage = r["response"]["body"]["usage"]
                total_cost += usage["prompt_tokens"] * (input_price / 1_000_000)
                total_cost += usage["completion_tokens"] * (output_price / 1_000_000)
        except Exception:
            pass

        return sorted_texts, total_cost

    def get_status(self, batch_id: str) -> str:
        status = self.client.batches.retrieve(batch_id)
        return status.status


