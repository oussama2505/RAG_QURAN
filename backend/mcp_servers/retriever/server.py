"""
Retriever MCP server implementation for RAG Quran.
This server exposes the retriever agent functionality through the MCP protocol.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from modelcontextprotocol import ResourceSchema, ToolDefinition, ToolExecutionResult

from backend.mcp_servers.base_server import BaseMCPServer
from backend.agents.retriever import RetrieverAgent, RetrieverAgentRequest


class RetrieverMCPServer(BaseMCPServer):
    """MCP server that exposes the retriever agent functionality."""
    
    def __init__(
        self,
        vector_store_path: str = "vector_db/faiss_index",
        name: str = "quran-retriever",
        description: str = "Retrieves relevant passages from the Quran and Tafsir based on natural language queries"
    ):
        """
        Initialize the retriever MCP server.
        
        Args:
            vector_store_path: Path to the FAISS vector store
            name: The name of the server
            description: A description of the server's capabilities
        """
        # Define the resource schema for Quranic content
        quran_resource_schema = ResourceSchema(
            id="quran-content",
            name="Quranic Content",
            description="Quran verses and tafsir explanations",
            schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for in the Quran"
                    },
                    "surah_filter": {
                        "type": ["integer", "null"],
                        "description": "Optional surah number to filter by"
                    },
                    "verse_filter": {
                        "type": ["integer", "null"],
                        "description": "Optional verse number to filter by"
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    },
                    "use_compression": {
                        "type": "boolean",
                        "description": "Whether to use contextual compression",
                        "default": True
                    }
                },
                "required": ["query"]
            }
        )
        
        # Define the tools
        tools = [
            ToolDefinition(
                name="retrieve",
                description="Retrieve relevant passages from the Quran and Tafsir",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query to search for in the Quran"
                        },
                        "surah_filter": {
                            "type": ["integer", "null"],
                            "description": "Optional surah number to filter by"
                        },
                        "verse_filter": {
                            "type": ["integer", "null"],
                            "description": "Optional verse number to filter by"
                        },
                        "k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        },
                        "use_compression": {
                            "type": "boolean",
                            "description": "Whether to use contextual compression",
                            "default": True
                        }
                    },
                    "required": ["query"]
                },
                handler=self._handle_retrieve
            )
        ]
        
        # Initialize the base server
        super().__init__(
            name=name,
            description=description,
            resources_schema=[quran_resource_schema],
            tools=tools
        )
        
        # Initialize the retriever agent
        self.agent = RetrieverAgent(vector_store_path=vector_store_path)
        self.logger.info(f"Initialized Retriever MCP Server with agent {self.agent.name}")
    
    async def _handle_retrieve(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Handle retrieve tool calls."""
        try:
            query = params.get("query")
            if not query:
                return ToolExecutionResult(error="Query is required")
            
            # Create a retriever request
            request = RetrieverAgentRequest(
                query=query,
                surah_filter=params.get("surah_filter"),
                verse_filter=params.get("verse_filter"),
                parameters={
                    "k": params.get("k", 5),
                    "use_compression": params.get("use_compression", True)
                }
            )
            
            # Process the request
            response = await self.agent.process(request)
            
            # Format the response for MCP
            result = {
                "formatted_context": response.formatted_context,
                "documents": response.documents,
                "metadata": response.metadata
            }
            
            return ToolExecutionResult(result=result)
            
        except Exception as e:
            self.logger.error(f"Error in retrieve tool: {str(e)}")
            return ToolExecutionResult(error=f"Error retrieving documents: {str(e)}")
            

def create_server():
    """Create and configure the Retriever MCP server."""
    return RetrieverMCPServer()