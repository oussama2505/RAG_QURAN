"""
Summarizer MCP server implementation for RAG Quran.
This server exposes the summarizer agent functionality through the MCP protocol.
"""

import asyncio
from typing import Any, Dict, List, Optional

from modelcontextprotocol import ResourceSchema, ToolDefinition, ToolExecutionResult

from backend.mcp_servers.base_server import BaseMCPServer
from backend.agents.summarizer import SummarizerAgent, SummarizerAgentRequest


class SummarizerMCPServer(BaseMCPServer):
    """MCP server that exposes the summarizer agent functionality."""
    
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.3,
        name: str = "quran-summarizer",
        description: str = "Summarizes Quranic passages or tafsirs with customizable length and focus"
    ):
        """
        Initialize the summarizer MCP server.
        
        Args:
            model_name: Name of the LLM to use
            temperature: Temperature parameter for generation
            name: The name of the server
            description: A description of the server's capabilities
        """
        # Define the tools
        tools = [
            ToolDefinition(
                name="summarize_content",
                description="Summarize Quranic content or tafsir explanations",
                parameters={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content to summarize"
                        },
                        "max_length": {
                            "type": "integer",
                            "description": "Maximum length of summary in words",
                            "default": 200
                        },
                        "focus": {
                            "type": "string",
                            "description": "Optional focus for the summary (e.g., 'historical context')",
                            "default": None
                        },
                        "model_name": {
                            "type": "string",
                            "description": "Name of the LLM to use",
                            "default": model_name
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Temperature parameter for generation",
                            "default": temperature
                        }
                    },
                    "required": ["content"]
                },
                handler=self._handle_summarize_content
            ),
            ToolDefinition(
                name="list_models",
                description="List available language models",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._handle_list_models
            )
        ]
        
        # Initialize the base server
        super().__init__(
            name=name,
            description=description,
            tools=tools
        )
        
        # Initialize the summarizer agent
        self.model_name = model_name
        self.temperature = temperature
        self.agent = SummarizerAgent(
            model_name=model_name,
            temperature=temperature
        )
        self.logger.info(f"Initialized Summarizer MCP Server with agent {self.agent.name}")
    
    async def _handle_summarize_content(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Handle summarize_content tool calls."""
        try:
            content = params.get("content")
            
            if not content:
                return ToolExecutionResult(error="Content is required")
            
            # Get optional parameters
            max_length = params.get("max_length", 200)
            focus = params.get("focus")
            model_name = params.get("model_name", self.model_name)
            temperature = params.get("temperature", self.temperature)
            
            # Create a summarizer request
            request = SummarizerAgentRequest(
                query=f"Summarize the following content in {max_length} words" + (f" with focus on {focus}" if focus else ""),
                content=content,
                parameters={
                    "max_length": max_length,
                    "focus": focus,
                    "model_name": model_name,
                    "temperature": temperature
                }
            )
            
            # Process the request
            response = await self.agent.process(request)
            
            # Format the response for MCP
            result = {
                "summary": response.summary,
                "original_length": response.original_length,
                "summary_length": response.summary_length,
                "metadata": response.metadata
            }
            
            return ToolExecutionResult(result=result)
            
        except Exception as e:
            self.logger.error(f"Error in summarize_content tool: {str(e)}")
            return ToolExecutionResult(error=f"Error summarizing content: {str(e)}")
    
    async def _handle_list_models(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Handle list_models tool calls."""
        # List of available models
        models = [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "provider": "OpenAI",
                "description": "Fast and cost-effective model for most summaries"
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "provider": "OpenAI",
                "description": "More capable model for complex content"
            },
            {
                "id": "claude-3-opus",
                "name": "Claude 3 Opus",
                "provider": "Anthropic",
                "description": "Anthropic's most capable model"
            },
            {
                "id": "claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "provider": "Anthropic",
                "description": "Good balance of intelligence and speed"
            }
        ]
        
        return ToolExecutionResult(result={"models": models})


def create_server():
    """Create and configure the Summarizer MCP server."""
    return SummarizerMCPServer()