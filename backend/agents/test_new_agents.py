"""
Test script for the new agents (Summarizer and Translation) in RAG Quran.
This script demonstrates how to use the new Summarizer and Translation agents.
"""

import asyncio
import json
import sys
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append("..")

from backend.agents.summarizer import SummarizerAgent, SummarizerAgentRequest
from backend.agents.tools.translation import TranslationToolAgent, TranslationRequest


async def test_summarizer_agent(content: str, max_length: int = 200, focus: str = None):
    """
    Test the Summarizer agent with Quranic content.
    
    Args:
        content: The content to summarize
        max_length: Maximum length of summary in words
        focus: Optional focus for the summary
    """
    print(f"\n{'='*80}\nTesting Summarizer Agent\n{'='*80}")
    print(f"Content to summarize (first 100 chars): {content[:100]}...")
    print(f"Max length: {max_length} words")
    if focus:
        print(f"Focus: {focus}")
    
    # Create the summarizer agent
    summarizer = SummarizerAgent()
    
    # Create the request
    request = SummarizerAgentRequest(
        query=f"Summarize the following content in {max_length} words" + (f" with focus on {focus}" if focus else ""),
        content=content,
        max_length=max_length,
        focus=focus
    )
    
    # Process the request
    print("\nProcessing request...")
    response = await summarizer.process(request)
    
    # Print the results
    print("\nSummary:")
    print(response.summary)
    
    print("\nMetadata:")
    print(f"Original length: {response.original_length} words")
    print(f"Summary length: {response.summary_length} words")
    
    return response


async def test_translation_agent(surah: int, verse: int, end_verse: int = None, translation: str = None):
    """
    Test the Translation agent with Quranic verses.
    
    Args:
        surah: Surah number
        verse: Verse number or start of verse range
        end_verse: Optional end of verse range
        translation: Optional translation to use
    """
    print(f"\n{'='*80}\nTesting Translation Agent\n{'='*80}")
    print(f"Surah: {surah}, Verse: {verse}" + (f"-{end_verse}" if end_verse else ""))
    if translation:
        print(f"Translation: {translation}")
    
    # Create the translation agent
    translator = TranslationToolAgent()
    
    # Create the request
    request = TranslationRequest(
        query=f"Translate Surah {surah}, Verse {verse}" + (f"-{end_verse}" if end_verse else ""),
        surah=surah,
        verse=verse,
        end_verse=end_verse,
        translation_name=translation
    )
    
    # Process the request
    print("\nProcessing request...")
    response = await translator.process(request)
    
    # Print the results
    print("\nArabic Text:")
    print(response.arabic_text)
    
    print("\nTranslated Text:")
    print(response.translated_text)
    
    print("\nMetadata:")
    print(f"Translation: {response.translation_name}")
    print(f"Reference: {response.reference}")
    
    return response


async def test_agent_to_agent_workflow():
    """
    Test an agent-to-agent workflow combining retrieval, translation, and summarization.
    """
    print(f"\n{'='*80}\nTesting Agent-to-Agent Workflow\n{'='*80}")
    
    # Step 1: Get a translation
    print("\nStep 1: Getting translation of Surah 2, Verses 1-5...")
    translator = TranslationToolAgent()
    translation_request = TranslationRequest(
        query="Translate Surah 2, Verses 1-5",
        surah=2,
        verse=1,
        end_verse=5
    )
    translation = await translator.process(translation_request)
    
    # Step 2: Summarize the translation
    print("\nStep 2: Summarizing the translation...")
    summarizer = SummarizerAgent()
    combined_text = f"Arabic:\n{translation.arabic_text}\n\nTranslation:\n{translation.translated_text}"
    
    summarizer_request = SummarizerAgentRequest(
        query="Summarize this Quranic passage with a focus on its core message",
        content=combined_text,
        max_length=100,
        focus="core theological message"
    )
    summary = await summarizer.process(summarizer_request)
    
    # Print the final results
    print("\nWorkflow Results:")
    print(f"Source: {translation.reference}")
    print(f"Summary of the passage: {summary.summary}")
    
    return {
        "translation": translation,
        "summary": summary
    }


async def main():
    """Run the test script."""
    # Sample content for summarization
    tafsir_content = """
    Ibn Kathir's Tafsir of Surah Al-Fatiha:
    
    In the name of Allah, the Beneficent, the Merciful.
    
    Allah starts this Surah with His Name as a blessing for the reader. The name Allah is the greatest name of Allah, and it is a name that is uniquely His and cannot be given to any of His creation. It means the One True God who is worthy of worship, who created everything that exists.
    
    'Ar-Rahman' (the Most Gracious) and 'Ar-Raheem' (the Most Merciful) are two names derived from the word 'Rahmah' (mercy). Rahman means the one who has vast mercy for all creation, while Raheem means the one whose mercy is fulfilled and implemented. The mercy of Allah is an attribute that Allah has ascribed to Himself, and His mercy encompasses all things.
    
    All praise and thanks are due to Allah, the Lord of all that exists.
    
    This verse includes the praise and glorification of Allah by mentioning His perfect Attributes and Actions. All praise belongs exclusively to Allah for His Essence and Attributes, for what He has created and continues to create, and for His favors upon His servants, both worldly and religious.
    
    'Lord of all that exists' (Rabb Al-'Alameen) - Rabb means the Owner who has full authority, the Creator, the One who sustains and nurtures all of existence through His generosity. 'Alameen is the plural of 'alam, which refers to everything in existence other than Allah. So Allah is the Lord of all the worlds, mankind, jinn, angels, and everything that exists.
    """
    
    # Test the summarizer agent
    await test_summarizer_agent(tafsir_content, max_length=150, focus="theological concepts")
    
    # Test the translation agent for a single verse
    await test_translation_agent(surah=1, verse=1)
    
    # Test the translation agent for multiple verses
    await test_translation_agent(surah=2, verse=1, end_verse=5, translation="en-yusuf-ali")
    
    # Test the agent-to-agent workflow
    await test_agent_to_agent_workflow()


if __name__ == "__main__":
    asyncio.run(main())