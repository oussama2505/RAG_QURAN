"""
Translation MCP server implementation for RAG Quran.
This server exposes the translation tool agent functionality through the MCP protocol.
"""

from typing import Any, Dict, List

from modelcontextprotocol import ToolDefinition, ToolExecutionResult

from backend.mcp_servers.base_server import BaseMCPServer
from backend.agents.tools.translation import TranslationToolAgent, TranslationRequest


class TranslationMCPServer(BaseMCPServer):
    """MCP server that exposes the translation tool agent functionality."""
    
    def __init__(
        self,
        name: str = "quran-translation",
        description: str = "Provides translations of Quranic verses in different languages",
        data_dir: str = "data",
        default_translation: str = "en-sahih-international"
    ):
        """
        Initialize the translation MCP server.
        
        Args:
            name: The name of the server
            description: A description of the server's capabilities
            data_dir: Directory containing Quran data files
            default_translation: Default translation to use
        """
        # Define the tools
        tools = [
            ToolDefinition(
                name="translate_verse",
                description="Translate a Quranic verse to a specific language",
                parameters={
                    "type": "object",
                    "properties": {
                        "surah": {
                            "type": "integer",
                            "description": "The surah number (1-114)"
                        },
                        "verse": {
                            "type": "integer",
                            "description": "The verse number or start of verse range"
                        },
                        "end_verse": {
                            "type": "integer",
                            "description": "Optional end of verse range for translating multiple verses"
                        },
                        "translation_name": {
                            "type": "string",
                            "description": "The translation to use (e.g., 'en-sahih-international')"
                        }
                    },
                    "required": ["surah", "verse"]
                },
                handler=self._handle_translate_verse
            ),
            ToolDefinition(
                name="list_translations",
                description="List available translations",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._handle_list_translations
            )
        ]
        
        # Initialize the base server
        super().__init__(
            name=name,
            description=description,
            tools=tools
        )
        
        # Initialize the translation agent
        self.data_dir = data_dir
        self.default_translation = default_translation
        self.agent = TranslationToolAgent(
            data_dir=data_dir,
            default_translation=default_translation
        )
        self.logger.info(f"Initialized Translation MCP Server with agent {self.agent.name}")
    
    async def _handle_translate_verse(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Handle translate_verse tool calls."""
        try:
            surah = params.get("surah")
            verse = params.get("verse")
            
            if not surah or not verse:
                return ToolExecutionResult(error="Surah and verse are required")
            
            # Get optional parameters
            end_verse = params.get("end_verse")
            translation_name = params.get("translation_name", self.default_translation)
            
            # Create a translation request
            request = TranslationRequest(
                query=f"Translate Surah {surah}, Verse {verse}" + (f"-{end_verse}" if end_verse else ""),
                surah=surah,
                verse=verse,
                parameters={
                    "end_verse": end_verse,
                    "translation_name": translation_name
                }
            )
            
            # Process the request
            response = await self.agent.process(request)
            
            # Format the response for MCP
            result = {
                "arabic_text": response.arabic_text,
                "translated_text": response.translated_text,
                "translation_name": response.translation_name,
                "reference": response.reference,
                "metadata": response.metadata
            }
            
            return ToolExecutionResult(result=result)
            
        except Exception as e:
            self.logger.error(f"Error in translate_verse tool: {str(e)}")
            return ToolExecutionResult(error=f"Error translating verse: {str(e)}")
    
    async def _handle_list_translations(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Handle list_translations tool calls."""
        try:
            translations = self.agent.get_available_translations()
            translations_list = [
                {"id": key, "name": value} for key, value in translations.items()
            ]
            
            return ToolExecutionResult(result={"translations": translations_list})
            
        except Exception as e:
            self.logger.error(f"Error in list_translations tool: {str(e)}")
            return ToolExecutionResult(error=f"Error listing translations: {str(e)}")


def create_server():
    """Create and configure the Translation MCP server."""
    return TranslationMCPServer()