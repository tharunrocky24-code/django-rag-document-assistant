import logging
import os
from django.conf import settings
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)

class ChromaONNXEmbeddings(Embeddings):
    """
    Ultra-fast, lightweight embedding implementation wrapping ChromaDB's ONNX MiniLM vectorizer.
    Runs locally with ONNX Runtime, requires zero external API keys, uses minimal memory,
    and has zero Windows symlink / GPU dependencies.
    """
    def __init__(self):
        try:
            from chromadb.utils import embedding_functions
            self.ef = embedding_functions.DefaultEmbeddingFunction()
            logger.info("Initialized Chroma ONNX DefaultEmbeddingFunction successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chroma ONNX embeddings: {e}")
            self.ef = None

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self.ef:
            # Chroma DefaultEmbeddingFunction returns list of numpy arrays or lists
            embeddings = self.ef(texts)
            return [list(map(float, vec)) for vec in embeddings]
        return [[0.0] * 384 for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        if not text:
            return [0.0] * 384
        if self.ef:
            embeddings = self.ef([text])
            if embeddings and len(embeddings) > 0:
                return list(map(float, embeddings[0]))
        return [0.0] * 384


_EMBEDDING_INSTANCE = None

def get_embeddings_model():
    """
    Returns a cached embedding model instance (singleton).
    Eliminates disk re-reads on every query for near-instant retrieval.
    """
    global _EMBEDDING_INSTANCE
    if _EMBEDDING_INSTANCE is not None:
        return _EMBEDDING_INSTANCE

    # Check if OpenAI key is explicitly set
    openai_key = getattr(settings, 'OPENAI_API_KEY', '')
    if openai_key and openai_key != 'mock-key-for-dev':
        try:
            from langchain_openai import OpenAIEmbeddings
            model_name = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
            _EMBEDDING_INSTANCE = OpenAIEmbeddings(model=model_name, openai_api_key=openai_key)
            return _EMBEDDING_INSTANCE
        except Exception as e:
            logger.warning(f"OpenAIEmbeddings failed: {e}")

    # Use Chroma's fast ONNX MiniLM vectorizer with RAM caching
    _EMBEDDING_INSTANCE = ChromaONNXEmbeddings()
    return _EMBEDDING_INSTANCE
