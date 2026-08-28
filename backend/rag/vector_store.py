import os
import logging
from django.conf import settings
from .embeddings import get_embeddings_model

logger = logging.getLogger(__name__)

def get_chroma_class():
    try:
        from langchain_chroma import Chroma
        return Chroma
    except ImportError:
        try:
            from langchain_community.vectorstores import Chroma
            return Chroma
        except ImportError:
            from chromadb import PersistentClient
            # Direct ChromaDB fallback if needed
            return None

_VECTOR_STORE_INSTANCE = None

def get_vector_store():
    """
    Returns persistent Chroma vector store instance (singleton).
    Reuses in-memory vector store connection for ultra-fast query execution.
    """
    global _VECTOR_STORE_INSTANCE
    if _VECTOR_STORE_INSTANCE is not None:
        return _VECTOR_STORE_INSTANCE

    persist_dir = getattr(settings, 'CHROMA_PERSIST_DIRECTORY', 'chroma_db')
    os.makedirs(persist_dir, exist_ok=True)
    
    embeddings = get_embeddings_model()
    ChromaClass = get_chroma_class()
    
    if ChromaClass:
        _VECTOR_STORE_INSTANCE = ChromaClass(
            collection_name="user_documents",
            embedding_function=embeddings,
            persist_directory=persist_dir
        )
        return _VECTOR_STORE_INSTANCE
    raise RuntimeError("Could not initialize Chroma vector store from langchain_chroma or langchain_community.")

def add_chunks_to_vector_store(chunks, user_id: int, document_id: int, document_name: str):
    """
    Adds chunks to ChromaDB with user_id, document_id metadata for strict user isolation.
    """
    vector_store = get_vector_store()

    for idx, chunk in enumerate(chunks):
        page_num = chunk.metadata.get('page', 1)
        if isinstance(page_num, int):
            page_num = page_num + 1 # Convert 0-indexed page to 1-indexed
            
        chunk.metadata.update({
            "user_id": str(user_id),
            "document_id": str(document_id),
            "document_name": str(document_name),
            "chunk_id": f"{document_id}_{idx}",
            "page": str(page_num),
            "source": str(document_name)
        })

    vector_store.add_documents(chunks)
    logger.info(f"Added {len(chunks)} chunks to ChromaDB for document_id={document_id}, user_id={user_id}")

def delete_document_vectors(user_id: int, document_id: int):
    """
    Deletes all vector embeddings associated with a specific document and user.
    """
    try:
        vector_store = get_vector_store()
        collection = vector_store._collection
        results = collection.get(
            where={
                "$and": [
                    {"user_id": {"$eq": str(user_id)}},
                    {"document_id": {"$eq": str(document_id)}}
                ]
            }
        )
        if results and results.get('ids'):
            collection.delete(ids=results['ids'])
            logger.info(f"Deleted {len(results['ids'])} vectors for document_id={document_id}, user_id={user_id}")
    except Exception as e:
        logger.error(f"Error deleting vectors for doc_id={document_id}: {str(e)}")
