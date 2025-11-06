"""Document retrieval strategies for RAG pipeline."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseRetriever(ABC):
    """Abstract base for retrieval strategies."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve documents relevant to query.

        Args:
            query: Search query
            top_k: Number of documents to retrieve

        Returns:
            List of documents with retrieval metadata
        """
        pass


class VectorRetriever(BaseRetriever):
    """Retrieves documents using vector similarity search.

    Uses a VectorStore to find semantically similar documents.
    """

    def __init__(self, vector_store):
        """Initialize retriever.

        Args:
            vector_store: VectorStore instance for similarity search
        """
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve documents by vector similarity.

        Args:
            query: Search query
            top_k: Number of documents to retrieve

        Returns:
            List of documents with similarity scores
        """
        # Use vector store to find similar documents
        results = self.vector_store.search(query, limit=top_k)

        # Format results
        documents = []
        for doc_id, score, payload in results:
            doc_dict = payload.copy()
            doc_dict["id"] = doc_id
            doc_dict["retrieval_score"] = float(score)
            documents.append(doc_dict)

        return documents


class HybridRetriever(BaseRetriever):
    """Hybrid retrieval combining vector search and reranking.

    Uses two-stage retrieval:
    1. Vector similarity to get candidate set
    2. LLM-based reranking to refine results
    """

    def __init__(
        self,
        vector_store,
        reranker,
        retrieval_k: int = 20,
        rerank_k: int = 5,
    ):
        """Initialize hybrid retriever.

        Args:
            vector_store: VectorStore for initial retrieval
            reranker: Ranker for reranking candidates
            retrieval_k: Number of documents in candidate set
            rerank_k: Number of documents after reranking
        """
        self.vector_store = vector_store
        self.reranker = reranker
        self.retrieval_k = retrieval_k
        self.rerank_k = rerank_k

    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Retrieve documents using hybrid approach.

        Args:
            query: Search query
            top_k: Override default rerank_k

        Returns:
            Reranked documents
        """
        final_k = top_k if top_k is not None else self.rerank_k

        # Stage 1: Vector retrieval
        results = self.vector_store.search(query, limit=self.retrieval_k)
        candidate_docs = []

        for doc_id, score, payload in results:
            doc_dict = payload.copy()
            doc_dict["id"] = doc_id
            doc_dict["retrieval_score"] = float(score)
            candidate_docs.append(doc_dict)

        if not candidate_docs:
            return []

        # Stage 2: LLM reranking
        # Convert to Product objects for ranker
        from ranking.base import Product

        products = []
        for doc in candidate_docs:
            # Use content or description field
            description = doc.get("content", doc.get("description", ""))
            products.append(
                Product(
                    id=doc["id"],
                    name=doc.get("name", doc["id"]),
                    description=description,
                    category=doc.get("category"),
                    metadata=doc,
                )
            )

        # Rank products
        ranking_result = self.reranker.rank(query, products, top_k=final_k)

        # Convert back to document format with rerank scores
        reranked_docs = []
        for product_id, score in ranking_result.rankings:
            # Find original document
            doc = next((d for d in candidate_docs if d["id"] == product_id), None)
            if doc:
                doc["rerank_score"] = float(score)
                reranked_docs.append(doc)

        return reranked_docs
