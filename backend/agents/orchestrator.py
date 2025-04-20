"""
A2A Orchestrator for RAG Quran agents.
This module coordinates the communication between retriever, generator, and tool agents.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from backend.agents.base import AgentRequest, AgentResponse
from backend.agents.retriever import RetrieverAgent, RetrieverAgentRequest
from backend.agents.generator import GeneratorAgent, GeneratorAgentRequest
from backend.agents.tools import TafsirToolAgent, TafsirLookupRequest


class QuranQueryRequest(BaseModel):
    """Model for a query about the Quran."""
    query: str
    surah_filter: Optional[int] = None
    verse_filter: Optional[int] = None
    model_name: str = "gpt-3.5-turbo"
    use_direct_tafsir: bool = False


class QuranQueryResponse(BaseModel):
    """Model for a response to a query about the Quran."""
    answer: str
    sources: List[Dict[str, Any]]
    filters_applied: Dict[str, Any]
    direct_tafsir: Optional[Dict[str, Any]] = None


class A2AOrchestrator:
    """
    Orchestrator that coordinates communication between RAG Quran agents.
    This demonstrates agent-to-agent communication using the A2A protocol.
    """
    
    def __init__(
        self,
        vector_store_path: str = "vector_db/faiss_index",
        tafsirs_dir: str = "data/tafsirs",
        model_name: str = "gpt-3.5-turbo"
    ):
        """
        Initialize the orchestrator with the required agents.
        
        Args:
            vector_store_path: Path to the FAISS vector store
            tafsirs_dir: Directory containing tafsir JSON files
            model_name: Default model name to use for generation
        """
        self.retriever_agent = RetrieverAgent(vector_store_path=vector_store_path)
        self.generator_agent = GeneratorAgent(model_name=model_name)
        self.tafsir_tool_agent = TafsirToolAgent(tafsirs_dir=tafsirs_dir)
        print("Initialized A2A Orchestrator with all agents")
        
    async def process_query(self, request: QuranQueryRequest) -> QuranQueryResponse:
        """
        Process a query about the Quran using A2A communication between agents.
        
        Args:
            request: The query request
            
        Returns:
            A response containing the answer and sources
        """
        # Step 1: Prepare filters
        filters_applied = {}
        if request.surah_filter:
            filters_applied["surah_filter"] = request.surah_filter
        if request.verse_filter:
            filters_applied["verse_filter"] = request.verse_filter
            
        # Track all sources
        all_sources = []
        
        # Step 2: Check if direct tafsir lookup is needed
        direct_tafsir_result = None
        if request.use_direct_tafsir and request.surah_filter and request.verse_filter:
            # Use the Tafsir Tool Agent for direct lookup
            tafsir_request = TafsirLookupRequest(
                query=f"Get tafsir for Surah {request.surah_filter}, Verse {request.verse_filter}",
                surah=request.surah_filter,
                verse=request.verse_filter
            )
            
            tafsir_response = await self.tafsir_tool_agent.process(tafsir_request)
            
            direct_tafsir_result = {
                "tafsir_name": tafsir_response.tafsir_name,
                "surah": tafsir_response.surah,
                "verse": tafsir_response.verse,
                "text": tafsir_response.tafsir_text
            }
            
            # Add to sources
            all_sources.append({
                "source_type": "tafsir",
                "reference": f"{request.surah_filter}:{request.verse_filter}",
                "content": tafsir_response.tafsir_text
            })
        
        # Step 3: Use the Retriever Agent to get relevant content
        retriever_request = RetrieverAgentRequest(
            query=request.query,
            surah_filter=request.surah_filter,
            verse_filter=request.verse_filter,
            parameters={
                "k": 5,
                "use_compression": True
            }
        )
        
        retriever_response = await self.retriever_agent.process(retriever_request)
        
        # Extract documents from retriever response
        context = retriever_response.formatted_context
        
        # Add retrieved documents to sources
        if hasattr(retriever_response, 'documents') and retriever_response.documents:
            for doc in retriever_response.documents:
                # Convert to a standardized source format
                source = {
                    "source_type": doc.get("metadata", {}).get("source", "unknown"),
                    "reference": doc.get("metadata", {}).get("reference", "unknown"),
                    "content": doc.get("content", "")
                }
                all_sources.append(source)
        
        # Step 4: Use the Generator Agent to create the answer
        generator_request = GeneratorAgentRequest(
            query=request.query,
            context=context,
            model_name=request.model_name,
            parameters={
                "context": context,
                "model_name": request.model_name
            }
        )
        
        generator_response = await self.generator_agent.process(generator_request)
        
        # Step 5: Compile the final response
        return QuranQueryResponse(
            answer=generator_response.answer,
            sources=all_sources,
            filters_applied=filters_applied,
            direct_tafsir=direct_tafsir_result
        )
