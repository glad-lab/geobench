import logging
import os
import re
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from llms import OpenAIHelper  # reuse existing helper

# Set up logging
logger = logging.getLogger(__name__)


class EngineNoQuery:
    """
    Engine for the no-query setting. It builds prompts from cohorts (lists of doc_ids)
    and descriptions, optionally replacing boosted documents with improved versions.
    """

    def __init__(self, doc_type: str = "Book Description") -> None:
        self.doc_type = doc_type

    def _make_search_results(self, list_docs: List[str]) -> Tuple[str, List[str]]:
        blocks: List[str] = []
        for i, txt in enumerate(list_docs):
            blocks.append(f"{self.doc_type} {i+1}:\n{txt}\n\n##########################\n\n")
        return ("".join(blocks), list_docs)

    def _get_citation_order(self, text: str) -> Tuple[List[int], List[int]]:
        pattern = r"\[(\d+)\]"
        matches = re.findall(pattern, text)
        cit_w_dups = [int(m) - 1 for m in matches]
        seen = set()
        cit = []
        for j in cit_w_dups:
            if j not in seen:
                seen.add(j)
                cit.append(j)
        return cit, cit_w_dups

    def run(
        self,
        cohorts: Dict[str, List[str]],
        boosted: Dict[str, List[str]],
        id2text: Dict[str, str],
        improved: Dict[str, str] | None,
        method_name: str,
        developer_prompt: str,
        llm: OpenAIHelper,
        running_folder: str,
    ) -> str:
        os.makedirs(running_folder, exist_ok=True)

        list_rows = []
        list_requests = []

        cohort_ids = list(cohorts.keys())
        cohort_ids.sort(key=lambda x: int(x) if x.isdigit() else x)

        for i, cid in enumerate(cohort_ids):
            members = cohorts[cid]
            target_ids = boosted.get(cid, [])

            # build list_docs with optional improved text for boosted items (method condition)
            list_docs: List[str] = []
            for idx, did in enumerate(members):
                if improved is not None and did in target_ids and did in improved:
                    list_docs.append(improved[did])
                else:
                    list_docs.append(id2text[did])

            # map boosted ids to indices within cohort members
            boost_indices = [members.index(did) for did in target_ids if did in members]

            search_results, _ = self._make_search_results(list_docs)
            user_prompt = (
                "Task: Based only on the following descriptions, select and justify the best choice. "
                "After each sentence, cite the supporting item(s) using [index] format like [1][2].\n\n"
                f"Search Results:\n{search_results}"
            )

            messages, raw_prompt = llm.create_message(user_prompt)
            list_requests.append(llm.create_request(messages, developer_prompt, i))
            list_rows.append([raw_prompt, "", "GLOBAL_TASK", boost_indices, None])

        df = pd.DataFrame(
            list_rows,
            columns=["Prompt", "Response", "Search Query", "Boost Product Index", "Citation Order"],
        )
        df.to_parquet(os.path.join(running_folder, "requests.parquet"))

        batch_id = llm.run_batch(list_requests, running_folder)
        return batch_id

    def process(self, responses_txt: List[str], output_folder: str) -> pd.DataFrame:
        """
        Process LLM responses to extract citations.

        Args:
            responses_txt: List of response texts from LLM
            output_folder: Output folder path

        Returns:
            DataFrame with responses and extracted citations

        Raises:
            FileNotFoundError: If requests.parquet doesn't exist
            ValueError: If number of responses doesn't match requests
        """
        running_folder = output_folder.replace("results", "running")
        requests_path = os.path.join(running_folder, "requests.parquet")

        if not os.path.exists(requests_path):
            raise FileNotFoundError(
                f"Requests file not found: {requests_path}. "
                "Make sure to run the benchmark first to generate requests."
            )

        df = pd.read_parquet(requests_path)

        if len(responses_txt) != len(df):
            logger.warning(
                f"Mismatch: {len(responses_txt)} responses but {len(df)} requests. "
                "Some responses may be missing or extra."
            )

        list_cit = []
        list_cit_dups = []
        errors = 0

        for i, resp in enumerate(responses_txt):
            try:
                c, cd = self._get_citation_order(resp)
            except (ValueError, AttributeError, TypeError) as e:
                logger.warning(
                    f"Failed to extract citations at index {i}: {type(e).__name__}: {e}\n"
                    f"Response preview: {resp[:200] if resp else '<empty>'}..."
                )
                c, cd = [], []
                errors += 1
            except Exception as e:
                logger.error(
                    f"Unexpected error extracting citations at index {i}: {type(e).__name__}: {e}\n"
                    f"Response preview: {resp[:200] if resp else '<empty>'}..."
                )
                c, cd = [], []
                errors += 1

            list_cit.append(c)
            list_cit_dups.append(cd)

        if errors > 0:
            logger.warning(
                f"Citation extraction failed for {errors}/{len(responses_txt)} responses "
                f"({errors/len(responses_txt)*100:.1f}%)"
            )

        df["Response"] = responses_txt
        df["Citation Order"] = list_cit
        df["Citation Order w. Duplicates"] = list_cit_dups
        return df


