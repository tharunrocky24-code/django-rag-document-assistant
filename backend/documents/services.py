import os
import logging
from .models import Document
from rag.loaders import load_document
from rag.splitter import split_documents
from rag.vector_store import add_chunks_to_vector_store

logger = logging.getLogger(__name__)

def process_document(document: Document):
    """
    Processes uploaded document:
    1. Sets status to 'processing'
    2. Loads text using appropriate loader
    3. Splits text into chunks
    4. Generates embeddings and stores in ChromaDB with user_id isolation
    5. Updates status to 'completed' or 'failed'
    """
    logger.info(f"Starting processing for document ID: {document.id} (title: {document.title})")
    
    document.processing_status = Document.STATUS_PROCESSING
    document.processing_error = None
    document.save(update_fields=['processing_status', 'processing_error'])

    try:
        file_path = document.file.path
        file_type = document.file_type

        # Load document
        raw_docs = load_document(file_path, file_type)
        if not raw_docs:
            raise ValueError("Document contains no readable text content.")

        # Split document into chunks
        chunks = split_documents(raw_docs)
        if not chunks:
            raise ValueError("Document text splitting produced 0 chunks.")

        # Add chunks & embeddings to ChromaDB
        add_chunks_to_vector_store(
            chunks=chunks,
            user_id=document.user.id,
            document_id=document.id,
            document_name=document.title
        )

        # Update model status
        document.processed = True
        document.processing_status = Document.STATUS_COMPLETED
        document.chunk_count = len(chunks)
        document.save(update_fields=['processed', 'processing_status', 'chunk_count'])

        logger.info(f"Successfully processed document ID: {document.id} with {len(chunks)} chunks")
        return True

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to process document ID: {document.id}. Error: {error_msg}")
        
        document.processed = False
        document.processing_status = Document.STATUS_FAILED
        document.processing_error = f"Failed to process document: {error_msg}"
        document.save(update_fields=['processed', 'processing_status', 'processing_error'])
        return False
