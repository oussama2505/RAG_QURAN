"""
Generator MCP server implementation for RAG Quran.
This server exposes the generator agent functionality through the MCP protocol.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from modelcontextprotocol import ResourceSchema, ToolDefinition, ToolExecutionResult

from backend.mcp_servers.base_server import BaseMCPServer
from backend.agents.generator import GeneratorAgent, GeneratorAgentRequest


class GeneratorMCPServer(BaseMCPServer):
    """MCP server that exposes the generator agent functionality."""
    
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.0,
        max_tokens: int = 1000,
        name: str = "quran-generator",
        description: str = "Generates answers to questions about the Quran based on provided context"
    ):
        """
        Initialize the generator MCP server.
        
        Args:
            model_name: Name of the LLM to use
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            name: The name of the server
            description: A description of the server's capabilities
        """
        # Define the tools
        tools = [
            ToolDefinition(
                name="generate_answer",
                description="Generate an answer based on provided Quranic context",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question to answer"
                        },
                        "context": {
                            "type": "string",
                            "description": "The Quranic context to use for answering"
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
                        },
                        "max_tokens": {
                            "type": "integer",
                            "description": "Maximum tokens to generate",
                            "default": max_tokens
                        }
                    },
                    "required": ["query", "context"]
                },
                handler=self._handle_generate_answer
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
        
        # Initialize the generator agent
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.agent = GeneratorAgent(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.logger.info(f"Initialized Generator MCP Server with agent {self.agent.name}")
    
    async def _handle_generate_answer(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Handle generate_answer tool calls."""
        try:
            query = params.get("query")
            context = params.get("context")
            
            if not query:
                return ToolExecutionResult(error="Query is required")
            if not context:
                return ToolExecutionResult(error="Context is required")
            
            # Get optional parameters
            model_name = params.get("model_name", self.model_name)
            temperature = params.get("temperature", self.temperature)
            max_tokens = params.get("max_tokens", self.max_tokens)
            
            # Create a generator request
            request = GeneratorAgentRequest(
                query=query,
                context=context,
                parameters={
                    "model_name": model_name,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            
            # Process the request
            response = await self.agent.process(request)
            
            # Format the response for MCP
            result = {
                "answer": response.answer,
                "sources": response.sources,
                "metadata": response.metadata
            }
            
            return ToolExecutionResult(result=result)
            
        except Exception as e:
            self.logger.error(f"Error in generate_answer tool: {str(e)}")
            return ToolExecutionResult(error=f"Error generating answer: {str(e)}")
    
    async def _handle_list_models(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Handle list_models tool calls."""
        # List of available models
        models = [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "provider": "OpenAI",
                "description": "Fast and cost-effective model for most queries"
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "provider": "OpenAI",
                "description": "More capable model for complex queries"
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "provider": "OpenAI",
                "description": "Highly capable model for advanced queries"
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
    """Create and configure the Generator MCP server."""
    return GeneratorMCPServer()