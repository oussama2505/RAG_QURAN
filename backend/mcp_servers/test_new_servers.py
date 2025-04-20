"""
Test script for the MCP servers in RAG Quran.
This script tests the MCP servers for the new Summarizer and Translation services.
"""

import asyncio
import json
import sys
import httpx
from typing import Dict, Any

# Make sure the servers are running before executing this script
# Run: python -m backend.mcp_servers.run_servers


async def test_summarizer_mcp_server():
    """Test the Summarizer MCP server."""
    print(f"\n{'='*80}\nTesting Summarizer MCP Server\n{'='*80}")
    
    # Sample tafsir content to summarize
    tafsir_content = """
    Ibn Kathir's Tafsir of Surah Al-Fatiha:
    
    In the name of Allah, the Beneficent, the Merciful.
    
    Allah starts this Surah with His Name as a blessing for the reader. The name Allah is the greatest name of Allah, and it is a name that is uniquely His and cannot be given to any of His creation. It means the One True God who is worthy of worship, who created everything that exists.
    
    'Ar-Rahman' (the Most Gracious) and 'Ar-Raheem' (the Most Merciful) are two names derived from the word 'Rahmah' (mercy). Rahman means the one who has vast mercy for all creation, while Raheem means the one whose mercy is fulfilled and implemented. The mercy of Allah is an attribute that Allah has ascribed to Himself, and His mercy encompasses all things.
    
    All praise and thanks are due to Allah, the Lord of all that exists.
    
    This verse includes the praise and glorification of Allah by mentioning His perfect Attributes and Actions. All praise belongs exclusively to Allah for His Essence and Attributes, for what He has created and continues to create, and for His favors upon His servants, both worldly and religious.
    
    'Lord of all that exists' (Rabb Al-'Alameen) - Rabb means the Owner who has full authority, the Creator, the One who sustains and nurtures all of existence through His generosity. 'Alameen is the plural of 'alam, which refers to everything in existence other than Allah. So Allah is the Lord of all the worlds, mankind, jinn, angels, and everything that exists.
    """
    
    # Create the request payload
    payload = {
        "name": "summarize_content",
        "parameters": {
            "content": tafsir_content,
            "max_length": 150,
            "focus": "theological concepts",
            "model_name": "gpt-3.5-turbo"
        }
    }
    
    # Send the request to the server
    async with httpx.AsyncClient() as client:
        print("\nSending request to summarizer MCP server...")
        try:
            response = await client.post(
                "http://localhost:5003/tools/execute",
                json=payload,
                timeout=30.0
            )
            
            # Check the response
            if response.status_code == 200:
                result = response.json()
                print("\nSummary:")
                print(result["result"]["summary"])
                print("\nMetadata:")
                print(f"Original length: {result['result']['original_length']} words")
                print(f"Summary length: {result['result']['summary_length']} words")
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None


async def test_translation_mcp_server():
    """Test the Translation MCP server."""
    print(f"\n{'='*80}\nTesting Translation MCP Server\n{'='*80}")
    
    # Test translating a single verse
    await _test_translation_verse(1, 1)
    
    # Test translating multiple verses with a specific translation
    await _test_translation_verse(2, 1, 5, "en-yusuf-ali")
    
    # Test listing available translations
    await _test_list_translations()


async def _test_translation_verse(surah: int, verse: int, end_verse: int = None, translation: str = None):
    """Test the translate_verse endpoint."""
    # Create the request payload
    payload = {
        "name": "translate_verse",
        "parameters": {
            "surah": surah,
            "verse": verse
        }
    }
    
    # Add optional parameters if provided
    if end_verse:
        payload["parameters"]["end_verse"] = end_verse
    if translation:
        payload["parameters"]["translation_name"] = translation
    
    # Send the request to the server
    async with httpx.AsyncClient() as client:
        print(f"\nSending request to translate Surah {surah}, Verse {verse}" + 
              (f"-{end_verse}" if end_verse else "") + 
              (f" in {translation}" if translation else "") + "...")
        
        try:
            response = await client.post(
                "http://localhost:5004/tools/execute",
                json=payload,
                timeout=30.0
            )
            
            # Check the response
            if response.status_code == 200:
                result = response.json()
                print("\nArabic Text:")
                print(result["result"]["arabic_text"])
                print("\nTranslated Text:")
                print(result["result"]["translated_text"])
                print("\nMetadata:")
                print(f"Translation: {result['result']['translation_name']}")
                print(f"Reference: {result['result']['reference']}")
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None


async def _test_list_translations():
    """Test the list_translations endpoint."""
    # Create the request payload
    payload = {
        "name": "list_translations",
        "parameters": {}
    }
    
    # Send the request to the server
    async with httpx.AsyncClient() as client:
        print("\nSending request to list available translations...")
        try:
            response = await client.post(
                "http://localhost:5004/tools/execute",
                json=payload,
                timeout=30.0
            )
            
            # Check the response
            if response.status_code == 200:
                result = response.json()
                print("\nAvailable Translations:")
                for i, translation in enumerate(result["result"]["translations"], 1):
                    print(f"{i}. {translation['name']} (ID: {translation['id']})")
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None


async def test_mcp_workflow():
    """Test a workflow combining multiple MCP servers."""
    print(f"\n{'='*80}\nTesting Multi-Server MCP Workflow\n{'='*80}")
    
    # Step 1: Get a translation using the Translation MCP server
    print("\nStep 1: Getting translation of Surah 2, Verses 1-5...")
    translation_payload = {
        "name": "translate_verse",
        "parameters": {
            "surah": 2,
            "verse": 1,
            "end_verse": 5
        }
    }
    
    async with httpx.AsyncClient() as client:
        translation_response = await client.post(
            "http://localhost:5004/tools/execute",
            json=translation_payload,
            timeout=30.0
        )
        
        if translation_response.status_code != 200:
            print(f"Error in translation step: {translation_response.status_code} - {translation_response.text}")
            return None
        
        translation_result = translation_response.json()
        
        # Step 2: Summarize the translation using the Summarizer MCP server
        print("\nStep 2: Summarizing the translation...")
        combined_text = f"Arabic:\n{translation_result['result']['arabic_text']}\n\nTranslation:\n{translation_result['result']['translated_text']}"
        
        summarizer_payload = {
            "name": "summarize_content",
            "parameters": {
                "content": combined_text,
                "max_length": 100,
                "focus": "core theological message"
            }
        }
        
        summarizer_response = await client.post(
            "http://localhost:5003/tools/execute",
            json=summarizer_payload,
            timeout=30.0
        )
        
        if summarizer_response.status_code != 200:
            print(f"Error in summarization step: {summarizer_response.status_code} - {summarizer_response.text}")
            return None
        
        summary_result = summarizer_response.json()
        
        # Print the final results
        print("\nWorkflow Results:")
        print(f"Source: {translation_result['result']['reference']}")
        print(f"Summary of the passage: {summary_result['result']['summary']}")
        
        return {
            "translation": translation_result,
            "summary": summary_result
        }


async def main():
    """Run the MCP test script."""
    print("Make sure that the MCP servers are running first!")
    print("You can start them with: python -m backend.mcp_servers.run_servers")
    
    # Add a small delay to allow the user to read the instructions
    await asyncio.sleep(2)
    
    # Test the summarizer MCP server
    await test_summarizer_mcp_server()
    
    # Test the translation MCP server
    await test_translation_mcp_server()
    
    # Test a workflow combining multiple MCP servers
    await test_mcp_workflow()


if __name__ == "__main__":
    asyncio.run(main())