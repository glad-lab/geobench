from abc import ABC
from typing import List

from noquery.src.llms.llm_interface import LLMInterface


class CitationBoosting(ABC):
    """
    Base class for improving text quality to boost visibility in generative systems.
    Copied from legacy with minimal changes.
    """

    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.instructions = ""
        self.system_prompt = ""
        self.prompt_template = "{instr}\n\n{description}"

    def improve_texts(self, texts: List[str], output_folder: str):
        list_requests = []
        for i, descr in enumerate(texts):
            msg, _ = self.llm.create_message(
                self.prompt_template.format(instr=self.instructions, description=descr)
            )
            list_requests.append(
                self.llm.create_request(
                    msg,
                    system=self.system_prompt,
                    i=i,
                )
            )
        batch_id = self.llm.run_batch(list_requests, output_folder)
        print(f"Batch ID: {batch_id}")
        return batch_id

    def improve_text(self, text: str):
        msg, _ = self.llm.create_message(
            self.prompt_template.format(instr=self.instructions, description=text)
        )
        response = self.llm.generate(msg)
        return response

    def retrieve_results(self, batch_id):
        results = self.llm.retrieve_results(batch_id)
        if results is None:
            print(f"Results for batch {batch_id} are not ready yet.")
            return None, None
        results_txt = [
            self.post_processing(self.llm.retrieve_text_response(result))
            for result in results
        ]

        total_cost = sum(
            [
                self.llm.calculate_api_call_cost(
                    response,
                    input_cost=self.llm.BATCH_PRICES[self.llm.llm_name]["input"],
                    output_cost=self.llm.BATCH_PRICES[self.llm.llm_name]["output"],
                )
                for response in results
            ]
        )
        return results_txt, total_cost

    def post_processing(self, text: str) -> str:
        return text
