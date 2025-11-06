"""Response generation strategies for RAG pipeline."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseGenerator(ABC):
    """Abstract base for generation strategies."""

    @abstractmethod
    def generate(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Generate response from query and documents.

        Args:
            query: User query
            documents: Retrieved documents

        Returns:
            Generated response text
        """
        pass


class LLMGenerator(BaseGenerator):
    """Generates responses using LLM with retrieved documents.

    Constructs a prompt with retrieved documents and uses LLM
    to generate a response.
    """

    DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that recommends products based on retrieved information.
Answer the user's question using ONLY the information from the provided documents.
If the information isn't in the documents, say so."""

    DEFAULT_USER_TEMPLATE = """Question: {query}

Retrieved Documents:
{documents}

Please answer the question based on the above documents."""

    def __init__(
        self,
        llm_client,
        system_prompt: Optional[str] = None,
        user_template: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 500,
    ):
        """Initialize generator.

        Args:
            llm_client: LLM client from src.llm
            system_prompt: System prompt for LLM
            user_template: Template for user message
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
        """
        self.llm_client = llm_client
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.user_template = user_template or self.DEFAULT_USER_TEMPLATE
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Generate response using LLM.

        Args:
            query: User query
            documents: Retrieved documents

        Returns:
            Generated response text
        """
        # Format documents into text
        doc_text = self._format_documents(documents)

        # Construct user message
        user_message = self.user_template.format(query=query, documents=doc_text)

        # Generate response using LLM client
        # Check if client has generate_text method (new interface)
        if hasattr(self.llm_client, "generate_text"):
            response = self.llm_client.generate_text(
                prompt=user_message,
                system_prompt=self.system_prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.content if hasattr(response, "content") else str(response)
        else:
            # Fallback for old interface
            # Construct messages for generate() method
            messages = [{"role": "user", "content": user_message}]

            if self.system_prompt:
                messages.insert(0, {"role": "system", "content": self.system_prompt})

            response = self.llm_client.generate(
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            return response.content if hasattr(response, "content") else str(response)

    def _format_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Format documents into readable text.

        Args:
            documents: List of document dictionaries

        Returns:
            Formatted document text
        """
        formatted = []

        for i, doc in enumerate(documents, 1):
            # Extract key fields
            name = doc.get("name", doc.get("original_id", "Unknown"))
            description = doc.get("content", doc.get("description", "No description"))
            price = doc.get("price", "N/A")
            rating = doc.get("rating", "N/A")
            category = doc.get("category", "")

            # Build document entry
            doc_entry = [f"Document {i}:", f"Name: {name}"]

            if category:
                doc_entry.append(f"Category: {category}")

            if price != "N/A":
                doc_entry.append(f"Price: ${price}")

            if rating != "N/A":
                doc_entry.append(f"Rating: {rating}")

            doc_entry.append(f"Description: {description}")

            # Add retrieval score if available
            if "retrieval_score" in doc:
                doc_entry.append(f"Relevance Score: {doc['retrieval_score']:.3f}")

            formatted.append("\n".join(doc_entry))

        return "\n\n".join(formatted)
