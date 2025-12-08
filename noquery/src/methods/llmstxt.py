from noquery.src.llms.llm_interface import LLMInterface
from .citation_boosting import CitationBoosting


class LLMstxt(CitationBoosting):
    def __init__(self, llm: LLMInterface):
        super().__init__(llm)
        self.instructions = (
            "Create a llms.txt markdown file to provide LLM-friendly content. This file summarizes the main text and offers brief background information, guidance, and links (if available).\n\n"
            "Follow this template\n# Title\n\n> Introduction paragraph\n\nOptional details go here\n\n## Section name\nMore details\n\nHere is the content of the text:\n{text}"
        )
