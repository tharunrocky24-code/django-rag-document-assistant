import logging
from django.conf import settings
from .vector_store import get_vector_store

logger = logging.getLogger(__name__)

def retrieve_user_chunks(query: str, user_id: int, document_id: int = None, top_k=None):
    """
    Retrieves top_k relevant chunks STRICTLY filtered by user_id.
    Optionally filters by specific document_id if provided.
    """
    k = top_k or getattr(settings, 'TOP_K', 4)
    vector_store = get_vector_store()

    # Strict user isolation filter
    if document_id:
        search_filter = {
            "$and": [
                {"user_id": {"$eq": str(user_id)}},
                {"document_id": {"$eq": str(document_id)}}
            ]
        }
    else:
        search_filter = {"user_id": {"$eq": str(user_id)}}

    try:
        docs = vector_store.similarity_search(
            query=query,
            k=k,
            filter=search_filter
        )
        logger.info(f"Retrieved {len(docs)} chunks for query '{query[:30]}' (user_id={user_id})")
        return docs
    except Exception as e:
        logger.error(f"Error during similarity search in ChromaDB: {e}")
        return []
