"""
Gemini embedding wrapper for adversarial SEO research.
Provides a compatible interface with OpenAI embeddings using Google's Gemini API.
"""

from typing import List, Optional, Union
import logging
import os
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiEmbeddings:
    """
    Gemini embeddings wrapper that provides compatibility with OpenAI embeddings interface.
    Uses Google's Gemini embedding model (text-embedding-004) for generating embeddings.
    """
    
    def __init__(
        self,
        model: str = "text-embedding-004",
        api_key: Optional[str] = None,
        output_dimensionality: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize the Gemini embeddings client.
        
        Args:
            model: Gemini embedding model name (default: text-embedding-004)
            api_key: Google API key (if not provided, uses GOOGLE_API_KEY env var)
            output_dimensionality: Optional dimension reduction (default: model's full dimensionality)
            **kwargs: Additional arguments (for compatibility)
        """
        self.model = model
        self.output_dimensionality = output_dimensionality
        
        api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "Google API key not provided. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        try:
            self.client = genai.Client(api_key=api_key)
            logger.info(f"Initialized Gemini embeddings with model: {self.model}")
            
            self._test_connection()
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def _test_connection(self):
        """Test the connection to Gemini API with a simple embedding."""
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents="test connection",
                config=types.EmbedContentConfig(
                    output_dimensionality=self.output_dimensionality
                ) if self.output_dimensionality else None
            )
            self.vector_size = len(response.embeddings[0].values)
            logger.info(f"Connection test successful. Vector size: {self.vector_size}")
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            config = None
            if self.output_dimensionality:
                config = types.EmbedContentConfig(
                    output_dimensionality=self.output_dimensionality
                )
            
            response = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=config
            )
            
            embedding = response.embeddings[0].values
            logger.debug(f"Generated embedding for query (length: {len(embedding)})")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding for query: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                return []
            
            config = None
            if self.output_dimensionality:
                config = types.EmbedContentConfig(
                    output_dimensionality=self.output_dimensionality
                )
            
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = self.client.models.embed_content(
                    model=self.model,
                    contents=batch,
                    config=config
                )
                
                batch_embeddings = [emb.values for emb in response.embeddings]
                all_embeddings.extend(batch_embeddings)
                
                logger.debug(f"Generated embeddings for batch {i//batch_size + 1} "
                           f"({len(batch)} documents)")
            
            logger.info(f"Generated embeddings for {len(texts)} documents")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings for documents: {e}")
            raise
    
    def get_vector_size(self) -> int:
        """
        Get the dimension size of embeddings.
        
        Returns:
            Vector dimension size
        """
        return getattr(self, 'vector_size', 768)
    
    def __call__(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Callable interface for generating embeddings.
        
        Args:
            texts: Single text string or list of texts
            
        Returns:
            Single embedding or list of embeddings
        """
        if isinstance(texts, str):
            return self.embed_query(texts)
        else:
            return self.embed_documents(texts)


class GeminiEmbeddingsWithFallback(GeminiEmbeddings):
    """
    Gemini embeddings with OpenAI fallback for development/testing.
    This class provides a fallback to OpenAI embeddings if Gemini fails.
    """
    
    def __init__(
        self,
        model: str = "text-embedding-004",
        api_key: Optional[str] = None,
        fallback_to_openai: bool = True,
        openai_model: str = "text-embedding-ada-002",
        **kwargs
    ):
        """
        Initialize with optional OpenAI fallback.
        
        Args:
            model: Gemini embedding model name
            api_key: Google API key
            fallback_to_openai: Whether to use OpenAI as fallback
            openai_model: OpenAI model for fallback
            **kwargs: Additional arguments
        """
        self.fallback_to_openai = fallback_to_openai
        self.openai_model = openai_model
        self._openai_embeddings = None
        
        try:
            super().__init__(model, api_key, **kwargs)
            self._using_fallback = False
        except Exception as e:
            if fallback_to_openai:
                logger.warning(f"Gemini initialization failed, using OpenAI fallback: {e}")
                self._init_openai_fallback()
                self._using_fallback = True
            else:
                raise
    
    def _init_openai_fallback(self):
        """Initialize OpenAI embeddings as fallback."""
        try:
            from langchain_community.embeddings import OpenAIEmbeddings
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OpenAI API key not found for fallback")
            
            self._openai_embeddings = OpenAIEmbeddings(
                model=self.openai_model,
                openai_api_key=openai_key
            )
            self.vector_size = 1536
            logger.info("Initialized OpenAI fallback embeddings")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI fallback: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding with fallback support."""
        if self._using_fallback:
            return self._openai_embeddings.embed_query(text)
        
        try:
            return super().embed_query(text)
        except Exception as e:
            if self.fallback_to_openai and not self._using_fallback:
                logger.warning(f"Gemini failed, using OpenAI fallback: {e}")
                self._init_openai_fallback()
                self._using_fallback = True
                return self._openai_embeddings.embed_query(text)
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings with fallback support."""
        if self._using_fallback:
            return self._openai_embeddings.embed_documents(texts)
        
        try:
            return super().embed_documents(texts)
        except Exception as e:
            if self.fallback_to_openai and not self._using_fallback:
                logger.warning(f"Gemini failed, using OpenAI fallback: {e}")
                self._init_openai_fallback()
                self._using_fallback = True
                return self._openai_embeddings.embed_documents(texts)
            raise