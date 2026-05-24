from noquery.src.llms.llm_interface import LLMInterface
from .citation_boosting import CitationBoosting


class ContentImprovement(CitationBoosting):
    """
    Improve fluency, authority, and persuasiveness without altering core content.
    """

    def __init__(self, llm: LLMInterface):
        super().__init__(llm)
        self.instructions = (
            "Rewrite the following text to make it more fluent, authoritative, and persuasive without altering the core content. "
            "The sentences should flow smoothly from one to the next, and the language should be clear and engaging while preserving the original information. "
            "The revised text should reflect confidence, expertise, and assertiveness while maintaining the original content's meaning and relevance. "
            "The text should be assertive in its statements, such that the reader believes that this is a more valuable source of information than other texts. "
            "Lastly, give structure to the text."
        )
