# backend/core/retriever.py
import os
from typing import List, Dict, Any
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from backend.core.llm_client import get_chat_model, UnifiedLLMChat

load_dotenv()

def create_basic_retriever(vector_store, k=5):
    """
    Create a simple retriever from a vector store
    """
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

def create_enhanced_retriever(vector_store, k=5, use_compression=True):
    """
    Create an advanced retriever with optional contextual compression
    """
    # Create a more robust base retriever with much lower threshold
    base_retriever = vector_store.as_retriever(
        search_type="similarity",  # Use simple similarity search without threshold filtering
        search_kwargs={
            "k": k * 3,  # Retrieve even more candidates initially
        }
    )
    
    if not use_compression:
        return base_retriever
        
    # Add contextual compression for more focused results
    try:
        # Use our unified LLM client
        print("Creating document compressor with UnifiedLLMChat")
        llm = get_chat_model(model_name="gpt-3.5-turbo", temperature=0)
        
        # Create the compressor
        compressor = LLMChainExtractor.from_llm(llm)
        print("Successfully created LLM compressor")
        
        # Create the compression retriever
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
        
        return compression_retriever
    except Exception as e:
        print(f"Warning: Could not create LLM compressor: {e}")
        return base_retriever  # Fall back to base retriever if compression fails

def retrieve_relevant_context(retriever, query: str, filter_criteria: Dict = None):
    """
    Retrieve relevant documents for a query with optional filtering
    """
    try:
        print(f"Retrieving documents for query: {query[:50]}...")
        if filter_criteria:
            print(f"With filters: {filter_criteria}")
            
        search_kwargs = {}
        if filter_criteria:
            search_kwargs["filter"] = filter_criteria
        
        # Handle different retriever types
        original_kwargs = None
        if hasattr(retriever, 'search_kwargs'):
            original_kwargs = retriever.search_kwargs.copy()
            if filter_criteria:
                retriever.search_kwargs.update(search_kwargs)
        
        # Execute the retrieval
        documents = retriever.get_relevant_documents(query)
        
        # Reset search_kwargs if modified
        if hasattr(retriever, 'search_kwargs') and original_kwargs and filter_criteria:
            retriever.search_kwargs = original_kwargs
        
        # Add query to metadata for tracing
        for doc in documents:
            if not hasattr(doc, 'metadata'):
                doc.metadata = {}
            doc.metadata['query'] = query
        
        return documents
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return []

def format_context_from_docs(documents: List[Any]) -> str:
    """
    Format retrieved documents into a context string
    """
    if not documents:
        return "No relevant information found."
        
    context_parts = []
    seen_refs = set()  # Track seen references to avoid duplicates
    
    for doc in documents:
        source = doc.metadata.get("source", "unknown")
        ref = doc.metadata.get("reference", "")
        
        # Skip duplicates
        ref_key = f"{source}:{ref}"
        if ref_key in seen_refs:
            continue
        seen_refs.add(ref_key)
        
        # Format differently based on source
        if source == "quran":
            context_parts.append(f"[Quran {ref}]: {doc.page_content}")
        elif source.startswith("tafsir_"):
            tafsir_name = source.replace("tafsir_", "")
            context_parts.append(f"[Tafsir {tafsir_name} on {ref}]: {doc.page_content}")
        else:
            # Generic format for other sources
            context_parts.append(f"[{source} {ref}]: {doc.page_content}")
    
    return "\n\n".join(context_parts)