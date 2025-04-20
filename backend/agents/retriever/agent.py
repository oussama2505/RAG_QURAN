"""
Retriever agent implementation using A2A protocol.
This agent is responsible for retrieving relevant Quranic context based on queries.
"""

import asyncio
from typing import Any, Dict, List, Optional

from backend.agents.base import BaseAgent, AgentRequest, AgentResponse
from backend.core.retriever import (
    create_enhanced_retriever,
    retrieve_relevant_context,
    format_context_from_docs
)
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from backend.core.embeddings import get_embeddings_model


class RetrieverAgentRequest(AgentRequest):
    """Specialized request model for the retriever agent."""
    surah_filter: Optional[int] = None
    verse_filter: Optional[int] = None
    k: int = 5
    use_compression: bool = True


class RetrieverAgentResponse(AgentResponse):
    """Specialized response model for the retriever agent."""
    documents: List[Dict[str, Any]]
    formatted_context: str


class RetrieverAgent(BaseAgent):
    """Agent responsible for retrieving relevant Quranic context based on queries."""
    
    def __init__(
        self,
        vector_store_path: str = "vector_db/faiss_index",
        embeddings: Optional[Embeddings] = None,
        name: str = "quran-retriever",
        description: str = "Retrieves relevant passages from the Quran and Tafsir based on natural language queries"
    ):
        """
        Initialize the retriever agent.
        
        Args:
            vector_store_path: Path to the FAISS vector store
            embeddings: Embeddings model to use (will be created if not provided)
            name: The name of the agent
            description: A description of the agent's capabilities
        """
        super().__init__(name, description)
        self.vector_store_path = vector_store_path
        self.embeddings = embeddings or get_embeddings_model()
        self._initialize_vector_store()
        
    def _initialize_vector_store(self):
        """Initialize the vector store from disk."""
        try:
            self.vector_store = FAISS.load_local(
                self.vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"Loaded vector store from {self.vector_store_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load vector store: {e}")
        
        # Create the retriever with default settings
        self.retriever = create_enhanced_retriever(
            self.vector_store,
            k=5,
            use_compression=True
        )
    
    async def process(self, request: RetrieverAgentRequest) -> RetrieverAgentResponse:
        """
        Process a retrieval request and return relevant Quranic context.
        
        Args:
            request: The retrieval request containing query and parameters
            
        Returns:
            A response containing retrieved documents and formatted context
        """
        # Extract parameters
        query = request.query
        k = request.parameters.get("k", request.k) if request.parameters else request.k
        use_compression = request.parameters.get("use_compression", request.use_compression) if request.parameters else request.use_compression
        
        # Create filter criteria if needed
        filter_criteria = {}
        surah_filter = request.parameters.get("surah_filter", request.surah_filter) if request.parameters else request.surah_filter
        verse_filter = request.parameters.get("verse_filter", request.verse_filter) if request.parameters else request.verse_filter
        
        if surah_filter:
            filter_criteria["surah"] = surah_filter
        if verse_filter:
            filter_criteria["verse"] = verse_filter
            
        # Update retriever if needed
        if k != 5 or not use_compression:
            self.retriever = create_enhanced_retriever(
                self.vector_store, 
                k=k,
                use_compression=use_compression
            )
            
        # Run the retrieval process in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        documents = await loop.run_in_executor(
            None,
            lambda: retrieve_relevant_context(self.retriever, query, filter_criteria)
        )
        
        # Format the context
        formatted_context = format_context_from_docs(documents)
        
        # Convert documents to serializable format
        serializable_docs = []
        for doc in documents:
            serializable_docs.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
            
        return RetrieverAgentResponse(
            content=formatted_context,
            metadata={"query": query, "filter_criteria": filter_criteria},
            documents=serializable_docs,
            formatted_context=formatted_context
        )
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities this agent provides.
        
        Returns:
            A list of capability strings
        """
        return [
            "quran-retrieval",
            "tafsir-retrieval",
            "context-retrieval",
            "surah-filtering",
            "verse-filtering"
        ]