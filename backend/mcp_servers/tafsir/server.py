"""
Tafsir Tool MCP server implementation for RAG Quran.
This server exposes the tafsir lookup functionality through the MCP protocol.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from modelcontextprotocol import ResourceSchema, ToolDefinition, ToolExecutionResult

from backend.mcp_servers.base_server import BaseMCPServer
from backend.agents.tools import TafsirToolAgent, TafsirLookupRequest


class TafsirMCPServer(BaseMCPServer):
    """MCP server that exposes the tafsir lookup functionality."""
    
    def __init__(
        self,
        tafsirs_dir: str = "data/tafsirs",
        name: str = "tafsir-lookup",
        description: str = "Provides direct lookup of tafsir explanations for specific Quranic verses"
    ):
        """
        Initialize the tafsir MCP server.
        
        Args:
            tafsirs_dir: Directory containing tafsir JSON files
            name: The name of the server
            description: A description of the server's capabilities
        """
        # Define the resource schema for tafsirs
        tafsir_resource_schema = ResourceSchema(
            id="tafsir-content",
            name="Tafsir Content",
            description="Tafsir explanations for specific Quranic verses",
            schema={
                "type": "object",
                "properties": {
                    "surah": {
                        "type": "integer",
                        "description": "Surah number"
                    },
                    "verse": {
                        "type": "integer",
                        "description": "Verse number"
                    },
                    "tafsir_name": {
                        "type": ["string", "null"],
                        "description": "Optional tafsir name (e.g., 'ibn-kathir')"
                    }
                },
                "required": ["surah", "verse"]
            }
        )
        
        # Define the tools
        tools = [
            ToolDefinition(
                name="lookup_tafsir",
                description="Look up tafsir explanation for a specific verse",
                parameters={
                    "type": "object",
                    "properties": {
                        "surah": {
                            "type": "integer",
                            "description": "Surah number"
                        },
                        "verse": {
                            "type": "integer",
                            "description": "Verse number"
                        },
                        "tafsir_name": {
                            "type": ["string", "null"],
                            "description": "Optional tafsir name (e.g., 'ibn-kathir')"
                        }
                    },
                    "required": ["surah", "verse"]
                },
                handler=self._handle_lookup_tafsir
            ),
            ToolDefinition(
                name="list_tafsirs",
                description="List available tafsirs",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._handle_list_tafsirs
            )
        ]
        
        # Initialize the base server
        super().__init__(
            name=name,
            description=description,
            resources_schema=[tafsir_resource_schema],
            tools=tools
        )
        
        # Initialize the tafsir tool agent
        self.tafsirs_dir = tafsirs_dir
        self.agent = TafsirToolAgent(tafsirs_dir=tafsirs_dir)
        self.logger.info(f"Initialized Tafsir MCP Server with agent {self.agent.name}")
    
    async def _handle_lookup_tafsir(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Handle lookup_tafsir tool calls."""
        try:
            surah = params.get("surah")
            verse = params.get("verse")
            tafsir_name = params.get("tafsir_name")
            
            if not surah:
                return ToolExecutionResult(error="Surah is required")
            if not verse:
                return ToolExecutionResult(error="Verse is required")
            
            # Create a tafsir lookup request
            request = TafsirLookupRequest(
                query=f"Lookup tafsir for Surah {surah}, Verse {verse}",
                surah=surah,
                verse=verse,
                tafsir_name=tafsir_name
            )
            
            # Process the request
            response = await self.agent.process(request)
            
            # Format the response for MCP
            result = {
                "tafsir_text": response.tafsir_text,
                "tafsir_name": response.tafsir_name,
                "surah": response.surah,
                "verse": response.verse
            }
            
            return ToolExecutionResult(result=result)
            
        except Exception as e:
            self.logger.error(f"Error in lookup_tafsir tool: {str(e)}")
            return ToolExecutionResult(error=f"Error looking up tafsir: {str(e)}")
    
    async def _handle_list_tafsirs(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Handle list_tafsirs tool calls."""
        try:
            # Get available tafsirs
            tafsirs = []
            if hasattr(self.agent, 'available_tafsirs'):
                for tafsir_id, tafsir_info in self.agent.available_tafsirs.items():
                    tafsirs.append({
                        "id": tafsir_id,
                        "name": tafsir_info.get('readable_name', tafsir_id),
                        "filename": tafsir_info.get('filename', f"{tafsir_id}.json")
                    })
            else:
                # Fallback if agent doesn't have available_tafsirs attribute
                for filename in os.listdir(self.tafsirs_dir):
                    if filename.endswith('.json'):
                        tafsir_id = filename.replace('.json', '')
                        
                        # Extract a more readable name from the tafsir ID
                        if '-' in tafsir_id:
                            lang_code, tafsir_name = tafsir_id.split('-', 1)
                            readable_name = tafsir_name.replace('-', ' ').title()
                        else:
                            readable_name = tafsir_id.replace('-', ' ').title()
                            
                        tafsirs.append({
                            "id": tafsir_id,
                            "name": readable_name,
                            "filename": filename
                        })
            
            return ToolExecutionResult(result={"tafsirs": tafsirs})
            
        except Exception as e:
            self.logger.error(f"Error in list_tafsirs tool: {str(e)}")
            return ToolExecutionResult(error=f"Error listing tafsirs: {str(e)}")


def create_server():
    """Create and configure the Tafsir MCP server."""
    return TafsirMCPServer()