import logging
import os
from django.conf import settings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .retriever import retrieve_user_chunks
from .prompts import SYSTEM_RAG_PROMPT

logger = logging.getLogger(__name__)

# Preferred Groq models in order of capability, speed, and availability
FALLBACK_GROQ_MODELS = [
    'openai/gpt-oss-20b',
    'openai/gpt-oss-120b',
    'groq/compound-mini',
    'qwen/qwen3.6-27b',
    'qwen/qwen3.8-27b',
]

def get_groq_llm(model_name=None, temperature=0.2, max_tokens=1024, request_timeout=8):
    """
    Instantiates ChatGroq using settings or preferred model with low-latency timeout.
    """
    groq_api_key = getattr(settings, 'GROQ_API_KEY', '') or os.getenv('GROQ_API_KEY', '')
    groq_model = model_name or getattr(settings, 'GROQ_MODEL', 'openai/gpt-oss-20b')

    if groq_api_key and groq_api_key != 'mock-key-for-dev':
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                groq_api_key=groq_api_key,
                model_name=groq_model,
                temperature=temperature,
                max_tokens=max_tokens,
                request_timeout=request_timeout,
                max_retries=1
            )
        except Exception as e:
            logger.error(f"Error initializing ChatGroq with {groq_model}: {e}")

    # Fallback to OpenAI if configured
    openai_key = getattr(settings, 'OPENAI_API_KEY', '')
    if openai_key and openai_key != 'mock-key-for-dev':
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=getattr(settings, 'OPENAI_CHAT_MODEL', 'gpt-4o-mini'),
                openai_api_key=openai_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            logger.error(f"Error initializing ChatOpenAI fallback: {e}")

    return None


def generate_conversation_title(question: str) -> str:
    """
    Generates a concise 3-5 word title summarizing the first user question using Groq.
    """
    prompt = f"Generate a brief title (3-5 words maximum) summarizing this question. Do not use quotes or punctuation.\nQuestion: {question}"
    
    primary_model = getattr(settings, 'GROQ_MODEL', 'openai/gpt-oss-120b')
    candidate_models = [primary_model] + [m for m in FALLBACK_GROQ_MODELS if m != primary_model]

    for model_name in candidate_models:
        try:
            llm = get_groq_llm(model_name=model_name, temperature=0.3, max_tokens=30)
            if llm:
                response = llm.invoke([HumanMessage(content=prompt)])
                title = response.content.strip().strip('"').strip("'")
                if title:
                    return title
        except Exception as e:
            logger.debug(f"Title generation failed with {model_name}: {e}")

    return question[:30].strip()


def run_rag_pipeline(user_id: int, question: str, chat_history=None, document_id=None):
    """
    Executes full RAG workflow with LangChain & Groq:
    1. Retrieve relevant document chunks for the user (with optional doc filtering).
    2. Format context and source citations.
    3. Include recent chat history.
    4. Prompt Groq LLM with automatic model fallback.
    5. Return structured answer and source citations.
    """
    # Step 1: Retrieve chunks from ChromaDB
    chunks = retrieve_user_chunks(question, user_id=user_id, document_id=document_id)

    context_text = ""
    sources = []
    seen_sources = set()

    if chunks:
        for chunk in chunks:
            doc_name = chunk.metadata.get('document_name', 'Unknown Document')
            page_num = chunk.metadata.get('page')
            chunk_preview = chunk.page_content[:200].strip().replace('\n', ' ')

            context_text += f"\n[Document: {doc_name} | Page: {page_num or '1'}]\n{chunk.page_content}\n"

            source_key = f"{doc_name}:{page_num}"
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                source_item = {
                    "document": doc_name,
                    "page": page_num or "1",
                    "snippet": chunk_preview
                }
                sources.append(source_item)
    else:
        context_text = "No relevant documents found for this user in the knowledge base."

    # Step 2: Build LLM Messages
    formatted_system_prompt = SYSTEM_RAG_PROMPT.format(context=context_text)
    messages = [SystemMessage(content=formatted_system_prompt)]

    # Add last 6 turns of conversation history
    if chat_history:
        for msg in chat_history[-6:]:
            if hasattr(msg, 'role'):
                if msg.role == 'user':
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == 'assistant':
                    messages.append(AIMessage(content=msg.content))
            elif isinstance(msg, dict):
                role = msg.get('role')
                content = msg.get('content', '')
                if role == 'user':
                    messages.append(HumanMessage(content=content))
                elif role == 'assistant':
                    messages.append(AIMessage(content=content))

    # Current user question
    messages.append(HumanMessage(content=question))

    # Step 3: Invoke Groq LLM with fallback candidate models
    primary_model = getattr(settings, 'GROQ_MODEL', 'openai/gpt-oss-120b')
    candidate_models = [primary_model] + [m for m in FALLBACK_GROQ_MODELS if m != primary_model]

    answer = None
    last_error = None

    for model_name in candidate_models:
        llm = get_groq_llm(model_name=model_name)
        if not llm:
            continue
        try:
            response = llm.invoke(messages)
            answer = response.content.strip()
            if answer:
                break
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Groq invocation failed on {model_name}: {e}. Trying fallback...")

    if not answer:
        if not chunks:
            answer = "I couldn't find any relevant information in your uploaded documents. Please upload documents related to this topic."
        else:
            answer = f"Error during generation: {last_error or 'No response received from model.'}"

    return {
        "answer": answer,
        "sources": sources
    }


def stream_rag_pipeline(user_id: int, question: str, chat_history=None, document_id=None):
    """
    Generator yielding token strings in real-time from Groq LLM.
    """
    # Retrieve chunks from ChromaDB
    chunks = retrieve_user_chunks(question, user_id=user_id, document_id=document_id)

    context_text = ""
    if chunks:
        for chunk in chunks:
            doc_name = chunk.metadata.get('document_name', 'Unknown Document')
            page_num = chunk.metadata.get('page')
            context_text += f"\n[Document: {doc_name} | Page: {page_num or '1'}]\n{chunk.page_content}\n"
    else:
        context_text = "No relevant documents found for this user in the knowledge base."

    formatted_system_prompt = SYSTEM_RAG_PROMPT.format(context=context_text)
    messages = [SystemMessage(content=formatted_system_prompt)]

    if chat_history:
        for msg in chat_history[-6:]:
            if hasattr(msg, 'role'):
                if msg.role == 'user':
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == 'assistant':
                    messages.append(AIMessage(content=msg.content))
            elif isinstance(msg, dict):
                role = msg.get('role')
                content = msg.get('content', '')
                if role == 'user':
                    messages.append(HumanMessage(content=content))
                elif role == 'assistant':
                    messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=question))

    primary_model = getattr(settings, 'GROQ_MODEL', 'openai/gpt-oss-20b')
    candidate_models = [primary_model, 'openai/gpt-oss-120b']

    streamed_anything = False
    error_msg = None

    for model_name in candidate_models:
        llm = get_groq_llm(model_name=model_name, request_timeout=6)
        if not llm:
            continue
        try:
            for chunk in llm.stream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    streamed_anything = True
                    yield chunk.content
            if streamed_anything:
                break
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"Groq streaming failed on {model_name}: {e}")
            # If network connection is timing out, don't cascade retry
            if "timeout" in error_msg.lower() or "connect" in error_msg.lower():
                break
            continue

    if not streamed_anything:
        if error_msg and ("timeout" in error_msg.lower() or "connect" in error_msg.lower()):
            yield "⚠️ Unable to reach Groq AI cloud service due to a network connection timeout. Please verify your internet connection or try again in a moment."
        else:
            yield "I couldn't find any relevant information in your uploaded documents or connect to the model."

