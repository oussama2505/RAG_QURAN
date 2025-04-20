"""
Translation tool agent implementation using A2A protocol.
This agent is responsible for translating Quranic verses to different languages.
"""

import json
import os
from typing import Any, Dict, List, Optional

from backend.agents.base import BaseAgent, AgentRequest, AgentResponse


class TranslationRequest(AgentRequest):
    """Specialized request model for the translation tool agent."""
    surah: int
    verse: int  # Single verse or start of range
    end_verse: Optional[int] = None  # End of range (if translating multiple verses)
    translation_name: Optional[str] = None  # Optional translation source


class TranslationResponse(AgentResponse):
    """Specialized response model for the translation tool agent."""
    arabic_text: str
    translated_text: str
    translation_name: str
    reference: str  # e.g., "Quran 2:255"


class TranslationToolAgent(BaseAgent):
    """Agent responsible for translating Quranic verses to different languages."""
    
    def __init__(
        self,
        data_dir: str = "data",
        default_translation: str = "en-sahih-international",
        name: str = "quran-translation",
        description: str = "Provides translations of Quranic verses in different languages"
    ):
        """
        Initialize the translation tool agent.
        
        Args:
            data_dir: Directory containing Quran data files
            default_translation: Default translation to use
            name: The name of the agent
            description: A description of the agent's capabilities
        """
        super().__init__(name, description)
        self.data_dir = data_dir
        self.default_translation = default_translation
        self._load_quran_data()
        self._load_available_translations()
        
    def _load_quran_data(self):
        """Load the Quran data from JSON file."""
        try:
            quran_path = os.path.join(self.data_dir, "quran.json")
            with open(quran_path, 'r', encoding='utf-8') as f:
                self.quran_data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load Quran data: {e}")
    
    def _load_available_translations(self):
        """Load the list of available translations."""
        # This would typically scan the data directory for translation files
        # For now, we'll hardcode some common translations
        self.available_translations = {
            "en-sahih-international": "Sahih International (English)",
            "en-yusuf-ali": "Yusuf Ali (English)",
            "en-pickthall": "Pickthall (English)",
            "fr-hamidullah": "Hamidullah (French)",
            "tr-diyanet": "Diyanet İşleri (Turkish)",
            "ur-jalandhry": "Jalandhry (Urdu)"
        }
        
    async def process(self, request: TranslationRequest) -> TranslationResponse:
        """
        Process a translation request and return the translated verse(s).
        
        Args:
            request: The translation request containing surah and verse reference
            
        Returns:
            A response containing the translated text
        """
        # Extract parameters
        surah = request.parameters.get("surah", request.surah) if request.parameters else request.surah
        verse = request.parameters.get("verse", request.verse) if request.parameters else request.verse
        end_verse = request.parameters.get("end_verse", getattr(request, "end_verse", None)) if request.parameters else getattr(request, "end_verse", None)
        translation_name = request.parameters.get("translation_name", getattr(request, "translation_name", self.default_translation)) if request.parameters else getattr(request, "translation_name", self.default_translation)
        
        # Validate surah and verse numbers
        if surah < 1 or surah > 114:
            raise ValueError(f"Invalid surah number: {surah}. Must be between 1 and 114.")
        
        # Convert to zero-based indexing for internal use
        surah_idx = surah - 1
        
        # Get the verses
        if end_verse is not None:
            # Multiple verses
            verses = self._get_verses(surah_idx, verse, end_verse)
            arabic_text = "\n".join([v["arabic"] for v in verses])
            translated_text = "\n".join([self._translate_verse(v, translation_name) for v in verses])
            reference = f"Quran {surah}:{verse}-{end_verse}"
        else:
            # Single verse
            verse_data = self._get_verse(surah_idx, verse)
            arabic_text = verse_data["arabic"]
            translated_text = self._translate_verse(verse_data, translation_name)
            reference = f"Quran {surah}:{verse}"
        
        # Get the display name of the translation
        translation_display_name = self.available_translations.get(
            translation_name, translation_name
        )
        
        return TranslationResponse(
            content=translated_text,
            metadata={
                "surah": surah,
                "verse": verse,
                "end_verse": end_verse,
                "translation": translation_name
            },
            arabic_text=arabic_text,
            translated_text=translated_text,
            translation_name=translation_display_name,
            reference=reference
        )
    
    def _get_verse(self, surah_idx: int, verse: int) -> Dict[str, Any]:
        """Get a single verse from the Quran data."""
        # This is a simplified implementation - in production, you would have proper verse lookup
        surah_data = self.quran_data["surahs"][surah_idx]
        
        if verse < 1 or verse > len(surah_data["verses"]):
            raise ValueError(f"Invalid verse number: {verse} for surah {surah_idx + 1}")
        
        verse_idx = verse - 1  # Convert to zero-based indexing
        verse_data = surah_data["verses"][verse_idx]
        
        return {
            "arabic": verse_data["text"],
            "number": verse,
            "surah": surah_idx + 1,
            "metadata": verse_data.get("metadata", {})
        }
    
    def _get_verses(self, surah_idx: int, start_verse: int, end_verse: int) -> List[Dict[str, Any]]:
        """Get multiple verses from the Quran data."""
        surah_data = self.quran_data["surahs"][surah_idx]
        
        if start_verse < 1 or end_verse > len(surah_data["verses"]) or start_verse > end_verse:
            raise ValueError(f"Invalid verse range: {start_verse}-{end_verse} for surah {surah_idx + 1}")
        
        verses = []
        for verse_idx in range(start_verse - 1, end_verse):
            verse_data = surah_data["verses"][verse_idx]
            verses.append({
                "arabic": verse_data["text"],
                "number": verse_idx + 1,
                "surah": surah_idx + 1,
                "metadata": verse_data.get("metadata", {})
            })
        
        return verses
    
    def _translate_verse(self, verse_data: Dict[str, Any], translation_name: str) -> str:
        """
        Translate a verse using the specified translation.
        
        In a real implementation, this would look up the translation from a database.
        For this example, we'll simulate translations with a simple placeholder.
        """
        # In a real implementation, this would fetch from a translations database
        # For now, we'll just return a placeholder that indicates what we'd translate
        surah = verse_data["surah"]
        verse = verse_data["number"]
        
        # Simulate translation (in production, you would load actual translations)
        if translation_name == "en-sahih-international":
            return f"Translation of Surah {surah}, Verse {verse} in Sahih International English"
        elif translation_name == "en-yusuf-ali":
            return f"Translation of Surah {surah}, Verse {verse} in Yusuf Ali English"
        else:
            return f"Translation of Surah {surah}, Verse {verse} in {translation_name}"
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities this agent provides.
        
        Returns:
            A list of capability strings
        """
        return [
            "verse-translation",
            "multi-language-support",
            "range-translation",
            "arabic-text-access"
        ]
    
    def get_available_translations(self) -> Dict[str, str]:
        """
        Get the list of available translations.
        
        Returns:
            A dictionary of translation IDs to display names
        """
        return self.available_translations