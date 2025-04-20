"""
Tool agent implementation for tafsir lookup using A2A protocol.
This agent provides specialized tools for the RAG Quran system.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from backend.agents.base import BaseAgent, AgentRequest, AgentResponse


class TafsirLookupRequest(AgentRequest):
    """Specialized request model for tafsir lookup."""
    surah: int
    verse: int
    tafsir_name: Optional[str] = None


class TafsirLookupResponse(AgentResponse):
    """Specialized response model for tafsir lookup."""
    tafsir_text: str
    tafsir_name: str
    surah: int
    verse: int


class TafsirToolAgent(BaseAgent):
    """Agent providing Tafsir lookup tools for the RAG Quran system."""
    
    def __init__(
        self,
        tafsirs_dir: str = "data/tafsirs",
        name: str = "tafsir-tool",
        description: str = "Provides direct lookup of tafsir explanations for specific Quranic verses"
    ):
        """
        Initialize the tafsir tool agent.
        
        Args:
            tafsirs_dir: Directory containing tafsir JSON files
            name: The name of the agent
            description: A description of the agent's capabilities
        """
        super().__init__(name, description)
        self.tafsirs_dir = tafsirs_dir
        self._load_available_tafsirs()
        
    def _load_available_tafsirs(self):
        """Load the list of available tafsirs."""
        try:
            self.available_tafsirs = {}
            # Get all JSON files in the tafsirs directory
            for filename in os.listdir(self.tafsirs_dir):
                if filename.endswith('.json'):
                    tafsir_id = filename.replace('.json', '')
                    
                    # Extract a more readable name from the tafsir ID
                    if '-' in tafsir_id:
                        lang_code, tafsir_name = tafsir_id.split('-', 1)
                        readable_name = tafsir_name.replace('-', ' ').title()
                    else:
                        readable_name = tafsir_id.replace('-', ' ').title()
                        
                    self.available_tafsirs[tafsir_id] = {
                        'filename': filename,
                        'readable_name': readable_name
                    }
                    
            print(f"Loaded {len(self.available_tafsirs)} available tafsirs")
        except Exception as e:
            print(f"Warning: Could not load tafsirs - {e}")
            self.available_tafsirs = {}
    
    async def process(self, request: TafsirLookupRequest) -> TafsirLookupResponse:
        """
        Process a tafsir lookup request and return the matching tafsir text.
        
        Args:
            request: The lookup request containing surah, verse, and optional tafsir name
            
        Returns:
            A response containing the requested tafsir text
        """
        # Extract parameters
        surah = request.parameters.get("surah", request.surah) if request.parameters else request.surah
        verse = request.parameters.get("verse", request.verse) if request.parameters else request.verse
        tafsir_name = request.parameters.get("tafsir_name", request.tafsir_name) if request.parameters else request.tafsir_name
        
        # Default to the first available tafsir if none specified
        if not tafsir_name and self.available_tafsirs:
            tafsir_name = next(iter(self.available_tafsirs.keys()))
            
        if not tafsir_name or tafsir_name not in self.available_tafsirs:
            available_names = ", ".join(self.available_tafsirs.keys())
            return TafsirLookupResponse(
                content=f"Invalid tafsir name. Available tafsirs: {available_names}",
                metadata={"error": "invalid_tafsir", "available": list(self.available_tafsirs.keys())},
                tafsir_text=f"Invalid tafsir name. Available tafsirs: {available_names}",
                tafsir_name="",
                surah=surah,
                verse=verse
            )
            
        # Run the lookup process in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        tafsir_text = await loop.run_in_executor(
            None,
            lambda: self._lookup_tafsir(tafsir_name, surah, verse)
        )
        
        readable_name = self.available_tafsirs[tafsir_name]['readable_name']
        
        return TafsirLookupResponse(
            content=tafsir_text,
            metadata={"tafsir": tafsir_name, "surah": surah, "verse": verse},
            tafsir_text=tafsir_text,
            tafsir_name=readable_name,
            surah=surah,
            verse=verse
        )
    
    def _lookup_tafsir(self, tafsir_name: str, surah: int, verse: int) -> str:
        """
        Look up a specific tafsir text.
        
        Args:
            tafsir_name: Name of the tafsir
            surah: Surah number
            verse: Verse number
            
        Returns:
            The tafsir text for the specified verse
        """
        try:
            # Get the filename for the requested tafsir
            filename = os.path.join(self.tafsirs_dir, self.available_tafsirs[tafsir_name]['filename'])
            
            # Load the tafsir data
            with open(filename, 'r', encoding='utf-8') as file:
                tafsir_data = json.load(file)
                
            # Lookup by surah and verse
            surah_str = str(surah)
            verse_str = str(verse)
            
            if surah_str in tafsir_data and verse_str in tafsir_data[surah_str]:
                return tafsir_data[surah_str][verse_str]
            else:
                return f"No tafsir found for Surah {surah}, Verse {verse} in {tafsir_name}"
                
        except Exception as e:
            print(f"Error looking up tafsir: {e}")
            return f"Error retrieving tafsir: {str(e)}"
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities this agent provides.
        
        Returns:
            A list of capability strings
        """
        return [
            "tafsir-lookup",
            "verse-explanation",
            "direct-reference"
        ]