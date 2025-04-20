"""
Test script for the A2A integration in RAG Quran.
This script demonstrates how to use the A2A orchestrator to process queries.
"""

import asyncio
import json
import sys
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append("..")

from backend.agents.orchestrator import A2AOrchestrator, QuranQueryRequest


async def test_a2a_quran_query(query: str, surah_filter: int = None, verse_filter: int = None):
    """
    Test the A2A orchestrator with a query about the Quran.
    
    Args:
        query: The question to ask
        surah_filter: Optional surah number to filter by
        verse_filter: Optional verse number to filter by
    """
    print(f"\n{'='*80}\nTesting A2A Quran Query\n{'='*80}")
    print(f"Query: {query}")
    if surah_filter:
        print(f"Surah Filter: {surah_filter}")
    if verse_filter:
        print(f"Verse Filter: {verse_filter}")
    
    # Create the orchestrator
    orchestrator = A2AOrchestrator()
    
    # Create the request
    request = QuranQueryRequest(
        query=query,
        surah_filter=surah_filter,
        verse_filter=verse_filter
    )
    
    # Process the query
    print("\nProcessing query...")
    response = await orchestrator.process_query(request)
    
    # Print the results
    print("\nAnswer:")
    print(response.answer)
    
    print("\nSources:")
    for i, source in enumerate(response.sources, 1):
        print(f"{i}. {source['source_type']} - {source['reference']}")
    
    print("\nFilters Applied:")
    print(json.dumps(response.filters_applied, indent=2))
    
    return response


async def test_direct_tafsir_lookup(surah: int, verse: int):
    """
    Test the direct tafsir lookup functionality.
    
    Args:
        surah: Surah number
        verse: Verse number
    """
    print(f"\n{'='*80}\nTesting Direct Tafsir Lookup\n{'='*80}")
    print(f"Surah: {surah}, Verse: {verse}")
    
    # Create the orchestrator
    orchestrator = A2AOrchestrator()
    
    # Create the request with direct tafsir flag
    request = QuranQueryRequest(
        query=f"What does Surah {surah}, Verse {verse} mean?",
        surah_filter=surah,
        verse_filter=verse,
        use_direct_tafsir=True
    )
    
    # Process the query
    print("\nProcessing query...")
    response = await orchestrator.process_query(request)
    
    # Print the direct tafsir result
    if response.direct_tafsir:
        print("\nDirect Tafsir:")
        print(f"Tafsir: {response.direct_tafsir['tafsir_name']}")
        print(f"Surah: {response.direct_tafsir['surah']}, Verse: {response.direct_tafsir['verse']}")
        print(f"Text: {response.direct_tafsir['text'][:300]}...")
    
    # Print the results
    print("\nAnswer:")
    print(response.answer)
    
    return response


async def main():
    """Run the test script."""
    # Test a general query
    await test_a2a_quran_query("What does the Quran say about patience?")
    
    # Test a query with surah filter
    await test_a2a_quran_query("What are the main themes?", surah_filter=12)
    
    # Test a query with surah and verse filter
    await test_a2a_quran_query("Explain this verse", surah_filter=2, verse_filter=255)
    
    # Test direct tafsir lookup
    await test_direct_tafsir_lookup(surah=1, verse=1)


if __name__ == "__main__":
    asyncio.run(main())
