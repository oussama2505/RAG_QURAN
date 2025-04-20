"""
Base MCP server implementation for RAG Quran.
This module provides the foundation for all MCP server implementations in the system.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable

from modelcontextprotocol import (
    Server, 
    ResourceSchema, 
    ToolDefinition,
    ToolCall,
    ToolExecutionResult
)


class BaseMCPServer(Server):
    """Base MCP server implementation for RAG Quran."""
    
    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        resources_schema: Optional[List[ResourceSchema]] = None,
        tools: Optional[List[ToolDefinition]] = None
    ):
        """
        Initialize the base MCP server.
        
        Args:
            name: The name of the server
            description: A description of the server's capabilities
            version: The server version
            resources_schema: Optional list of resource schemas
            tools: Optional list of tool definitions
        """
        super().__init__(name=name, description=description)
        self.version = version
        
        # Register resources schemas if provided
        if resources_schema:
            for schema in resources_schema:
                self.register_resource_schema(schema)
        
        # Register tools if provided
        if tools:
            for tool in tools:
                self.register_tool(tool)
        
        self.logger = logging.getLogger(f"mcp.server.{name}")
        self.logger.setLevel(logging.INFO)
        self._register_default_tools()
        
    def _register_default_tools(self):
        """Register default tools that all servers should have."""
        self.register_tool(
            ToolDefinition(
                name="get_version",
                description="Get the server version",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._handle_get_version
            )
        )
        
    async def _handle_get_version(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Handle the get_version tool call."""
        return ToolExecutionResult(
            result={
                "version": self.version,
                "name": self.name,
                "description": self.description
            }
        )
        
    async def execute_tool(self, tool_call: ToolCall) -> ToolExecutionResult:
        """
        Execute a tool call by routing to the appropriate handler.
        
        Args:
            tool_call: The tool call to execute
            
        Returns:
            The result of the tool execution
        """
        try:
            self.logger.info(f"Executing tool: {tool_call.name}")
            
            # Get the handler for this tool
            tool = self.get_registered_tool(tool_call.name)
            if not tool:
                self.logger.error(f"Tool not found: {tool_call.name}")
                return ToolExecutionResult(
                    error=f"Tool not found: {tool_call.name}"
                )
                
            # Execute the tool handler
            handler = tool.handler
            if asyncio.iscoroutinefunction(handler):
                result = await handler(tool_call.parameters)
            else:
                result = handler(tool_call.parameters)
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_call.name}: {str(e)}")
            return ToolExecutionResult(
                error=f"Error executing tool {tool_call.name}: {str(e)}"
            )
            
    def get_registered_tools(self) -> List[ToolDefinition]:
        """Get all registered tools."""
        return list(self._tools.values())
        
    def get_registered_resources(self) -> List[ResourceSchema]:
        """Get all registered resource schemas."""
        return list(self._resource_schemas.values())