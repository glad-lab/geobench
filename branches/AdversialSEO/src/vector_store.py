"""
Vector store management for adversarial SEO research.
Handles Qdrant integration and embedding management.
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import uuid
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
    UpdateStatus
)
import logging
import os

# Use new LangChain OpenAI import (fixes deprecation warning)
try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    # Fallback to old import for backward compatibility
    from langchain_community.embeddings import OpenAIEmbeddings

try:
    from .gemini_embeddings import GeminiEmbeddingsWithFallback
except ImportError:
    from gemini_embeddings import GeminiEmbeddingsWithFallback

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a document to be stored in the vector database."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class VectorStoreManager:
    """
    Manages vector storage using Qdrant for document embeddings.
    Supports both product descriptions and noise documents.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "adversarial_seo",
        embedding_model: str = "text-embedding-3-small",
        embedding_provider: str = "openai",
        api_key: Optional[str] = None,
        reset_collection: bool = False
    ):
        """
        Initialize the vector store manager.

        Args:
            host: Qdrant host (default: localhost)
            port: Qdrant port (default: 6333)
            collection_name: Name of the collection (default: adversarial_seo)
            embedding_model: Embedding model name (default: text-embedding-3-small)
                - OpenAI options: text-embedding-3-small (1536 dims), text-embedding-3-large (3072 dims)
                - Gemini options: text-embedding-004 (768 dims)
            embedding_provider: Provider to use (default: openai)
                - Options: "openai" (recommended), "gemini" (requires Google API key)
            api_key: API key for the embedding provider
                - OpenAI: Get from https://platform.openai.com/api-keys
                - Gemini: Get from https://aistudio.google.com/app/apikey
            reset_collection: Whether to reset the collection on init (default: False)
        """
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.embedding_provider = embedding_provider.lower()

        if self.embedding_provider == "openai":
            self.embeddings = OpenAIEmbeddings(
                model=embedding_model,
                openai_api_key=api_key or os.getenv("OPENAI_API_KEY")
            )
            # Set vector size based on OpenAI model
            if "text-embedding-3-small" in embedding_model:
                self.vector_size = 1536
            elif "text-embedding-3-large" in embedding_model:
                self.vector_size = 3072
            elif "text-embedding-ada-002" in embedding_model:
                self.vector_size = 1536
            else:
                self.vector_size = 1536  # Default for OpenAI models
        elif self.embedding_provider == "gemini":
            gemini_model = embedding_model if "text-embedding-004" in embedding_model or "embedding-001" in embedding_model else "text-embedding-004"
            self.embeddings = GeminiEmbeddingsWithFallback(
                model=gemini_model,
                api_key=api_key,
                fallback_to_openai=True,
                openai_model="text-embedding-ada-002"
            )
            self.vector_size = self.embeddings.get_vector_size()
        else:
            raise ValueError(
                f"Unsupported embedding provider: {embedding_provider}. "
                f"Supported providers: 'openai', 'gemini'"
            )
        
        logger.info(f"Initialized vector store with {self.embedding_provider} embeddings, "
                   f"model: {embedding_model}, vector size: {self.vector_size}")
        
        self._init_collection(reset_collection)
    
    def _init_collection(self, reset: bool = False):
        """Initialize or reset the Qdrant collection."""
        try:
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)

            if reset and collection_exists:
                self.client.delete_collection(self.collection_name)
                logger.info(f"Deleted existing collection: {self.collection_name}")
                collection_exists = False

            # Check if existing collection has correct vector dimension
            if collection_exists:
                collection_info = self.client.get_collection(self.collection_name)
                existing_size = collection_info.config.params.vectors.size

                if existing_size != self.vector_size:
                    logger.warning(
                        f"Collection '{self.collection_name}' has vector size {existing_size} "
                        f"but current embeddings produce {self.vector_size} dimensions. "
                        f"Recreating collection..."
                    )
                    self.client.delete_collection(self.collection_name)
                    collection_exists = False

            if not collection_exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection '{self.collection_name}' with vector size {self.vector_size}")
            else:
                logger.info(f"Using existing collection '{self.collection_name}' with vector size {self.vector_size}")

        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> bool:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document dictionaries
            batch_size: Batch size for insertion
            
        Returns:
            Success status
        """
        try:
            points = []
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                texts = [doc.get("content", doc.get("description", "")) for doc in batch]
                embeddings = self.embeddings.embed_documents(texts)
                
                for doc, embedding in zip(batch, embeddings):
                    doc_id_str = doc.get("id", str(uuid.uuid4()))
                    try:
                        point_id = uuid.UUID(doc_id_str) if isinstance(doc_id_str, str) else doc_id_str
                    except ValueError:
                        point_id = uuid.uuid4()
                    
                    point_id = str(point_id)
                    
                    metadata = {
                        "original_id": doc_id_str,
                        "name": doc.get("name", ""),
                        "category": doc.get("category", ""),
                        "type": doc.get("type", "product")
                    }
                    
                    if "description" in doc:
                        metadata["description"] = doc["description"]
                    if "content" in doc:
                        metadata["content"] = doc["content"]
                    
                    attack_metadata_fields = ["_attack_type", "_is_attack_document", "approach", "has_attack", "attack_type"]
                    
                    for key, value in doc.items():
                        if key not in ["id", "embedding"]:
                            if key in attack_metadata_fields:
                                metadata[f"__{key}"] = value  
                            elif key not in metadata: 
                                metadata[key] = value
                    
                    points.append(
                        PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload=metadata
                        )
                    )
                
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                
            logger.info(f"Added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            filter_dict: Optional filters for search
            score_threshold: Minimum similarity score
            
        Returns:
            List of (id, score, metadata) tuples
        """
        try:
            query_embedding = self.embeddings.embed_query(query)
            
            search_filter = None
            if filter_dict:
                conditions = []
                for key, value in filter_dict.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                search_filter = Filter(must=conditions)
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            
            formatted_results = [
                (
                    str(hit.id),
                    hit.score,
                    hit.payload
                )
                for hit in results
            ]
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_by_id(self, doc_id: str) -> Optional[Dict]:
        """
        Retrieve a document by its ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document metadata or None
        """
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[doc_id]
            )
            
            if result:
                return result[0].payload
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document: {e}")
            return None
    
    def update_document(
        self,
        doc_id: str,
        metadata_updates: Dict[str, Any]
    ) -> bool:
        """
        Update document metadata.
        
        Args:
            doc_id: Document ID
            metadata_updates: Metadata to update
            
        Returns:
            Success status
        """
        try:
            self.client.set_payload(
                collection_name=self.collection_name,
                payload=metadata_updates,
                points=[doc_id]
            )
            logger.info(f"Updated document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    def delete_documents(
        self,
        doc_ids: List[str]
    ) -> bool:
        """
        Delete documents from the vector store.
        
        Args:
            doc_ids: List of document IDs to delete
            
        Returns:
            Success status
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=doc_ids
            )
            logger.info(f"Deleted {len(doc_ids)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            info = self.client.get_collection(self.collection_name)
            
            return {
                "name": self.collection_name,
                "vector_count": info.vectors_count,
                "indexed_vectors": info.indexed_vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": info.config.params.vectors.distance
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def add_noise_documents(
        self,
        noise_documents: List[Dict[str, str]],
        noise_ratio: float = 0.3
    ) -> bool:
        """
        Add noise documents to simulate real-world search conditions.
        
        Args:
            noise_documents: List of irrelevant documents
            noise_ratio: Ratio of noise to add (0.3 = 30% noise)
            
        Returns:
            Success status
        """
        current_stats = self.get_collection_stats()
        current_count = current_stats.get("points_count", 0)
        target_noise_count = int(current_count * noise_ratio)
        
        import random
        sampled_noise = random.sample(
            noise_documents,
            min(target_noise_count, len(noise_documents))
        )
        
        for doc in sampled_noise:
            doc["type"] = "noise"
            doc["is_noise"] = True
        
        return self.add_documents(sampled_noise)
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection.
        
        Returns:
            Success status
        """
        try:
            self.client.delete_collection(self.collection_name)
            self._init_collection(reset=False)
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False