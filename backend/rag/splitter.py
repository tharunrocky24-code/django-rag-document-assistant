try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        # Simple fallback splitter if langchain text splitters not found
        class RecursiveCharacterTextSplitter:
            def __init__(self, chunk_size=1000, chunk_overlap=200, separators=None):
                self.chunk_size = chunk_size
                self.chunk_overlap = chunk_overlap

            def split_documents(self, docs):
                from langchain_core.documents import Document
                chunks = []
                for doc in docs:
                    text = doc.page_content
                    start = 0
                    while start < len(text):
                        end = min(start + self.chunk_size, len(text))
                        chunk_text = text[start:end]
                        new_meta = dict(doc.metadata)
                        chunks.append(Document(page_content=chunk_text, metadata=new_meta))
                        if end >= len(text):
                            break
                        start += self.chunk_size - self.chunk_overlap
                return chunks

from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def split_documents(documents, chunk_size=None, chunk_overlap=None):
    """
    Splits documents into text chunks using RecursiveCharacterTextSplitter.
    """
    c_size = chunk_size or getattr(settings, 'CHUNK_SIZE', 1000)
    c_overlap = chunk_overlap or getattr(settings, 'CHUNK_OVERLAP', 200)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=c_size,
        chunk_overlap=c_overlap,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} raw docs into {len(chunks)} text chunks (size: {c_size}, overlap: {c_overlap})")
    return chunks
