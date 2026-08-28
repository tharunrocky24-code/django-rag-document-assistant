import os
import logging
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_core.documents import Document as LCDocument

logger = logging.getLogger(__name__)

def load_document(file_path: str, file_type: str):
    """
    Loads document content based on file_type using appropriate LangChain loader.
    Supports PDF, DOCX, TXT, CSV, MD with automatic encoding fallback.
    """
    file_type = file_type.lower().strip('.')
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at path: {file_path}")

    logger.info(f"Loading document: {file_path} of type {file_type}")

    if file_type == 'pdf':
        loader = PyPDFLoader(file_path)
        return loader.load()
    elif file_type == 'docx':
        loader = Docx2txtLoader(file_path)
        return loader.load()
    elif file_type in ('txt', 'md', 'csv', 'json', 'log'):
        # Try UTF-8 first, fallback to Latin-1
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            return loader.load()
        except Exception:
            try:
                loader = TextLoader(file_path, encoding='latin-1')
                return loader.load()
            except Exception:
                with open(file_path, 'r', errors='ignore') as f:
                    content = f.read()
                return [LCDocument(page_content=content, metadata={"source": file_path})]
    else:
        # Generic fallback
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read()
        return [LCDocument(page_content=content, metadata={"source": file_path})]
