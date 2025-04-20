"""
Test script for MCP servers in RAG Quran.
This script tests the MCP servers using direct HTTP requests.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import httpx
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_test")


async def test_retriever_server(port: int = 5000):
    """Test the Retriever MCP server."""
    logger.info(f"Testing Retriever MCP server on port {port}")
    
    # Define the test query
    test_query = {
        "name": "retrieve",
        "parameters": {
            "query": "What does the Quran say about patience?",
            "k": 3,
            "use_compression": True
        }
    }
    
    # Send the request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:{port}/tools/execute",
            json=test_query,
            timeout=30.0
        )
        
    # Log the results
    logger.info(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info("Retrieved context snippet:")
        if "result" in result and "formatted_context" in result["result"]:
            context = result["result"]["formatted_context"]
            # Print the first 500 characters of the context
            logger.info(context[:500] + "..." if len(context) > 500 else context)
        else:
            logger.warning("Unexpected response format")
            logger.info(json.dumps(result, indent=2))
    else:
        logger.error(f"Error: {response.text}")


async def test_generator_server(port: int = 5001):
    """Test the Generator MCP server."""
    logger.info(f"Testing Generator MCP server on port {port}")
    
    # Define the test query
    test_query = {
        "name": "generate_answer",
        "parameters": {
            "query": "What does the Quran say about patience?",
            "context": "[Quran 2:153]: O you who have believed, seek help through patience and prayer. Indeed, Allah is with the patient.\n\n[Quran 3:200]: O you who have believed, persevere and endure and remain stationed and fear Allah that you may be successful.\n\n[Quran 13:24]: Peace be upon you for what you patiently endured. And excellent is the final home.",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.0
        }
    }
    
    # Send the request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:{port}/tools/execute",
            json=test_query,
            timeout=30.0
        )
        
    # Log the results
    logger.info(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info("Generated answer snippet:")
        if "result" in result and "answer" in result["result"]:
            answer = result["result"]["answer"]
            # Print the first 500 characters of the answer
            logger.info(answer[:500] + "..." if len(answer) > 500 else answer)
        else:
            logger.warning("Unexpected response format")
            logger.info(json.dumps(result, indent=2))
    else:
        logger.error(f"Error: {response.text}")


async def test_tafsir_server(port: int = 5002):
    """Test the Tafsir MCP server."""
    logger.info(f"Testing Tafsir MCP server on port {port}")
    
    # Test listing available tafsirs
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:{port}/tools/execute",
            json={"name": "list_tafsirs", "parameters": {}}
        )
        
    # Log the results
    logger.info(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info("Available tafsirs:")
        if "result" in result and "tafsirs" in result["result"]:
            tafsirs = result["result"]["tafsirs"]
            for tafsir in tafsirs[:5]:  # Show first 5 tafsirs
                logger.info(f"- {tafsir.get('name', 'Unknown')} ({tafsir.get('id', 'no-id')})")
            
            # If we have tafsirs, test lookup
            if tafsirs:
                tafsir_id = tafsirs[0]["id"]
                await test_tafsir_lookup(port, tafsir_id, 1, 1)
        else:
            logger.warning("Unexpected response format")
            logger.info(json.dumps(result, indent=2))
    else:
        logger.error(f"Error: {response.text}")


async def test_tafsir_lookup(port: int, tafsir_name: str, surah: int, verse: int):
    """Test looking up a specific tafsir."""
    logger.info(f"Testing tafsir lookup for Surah {surah}, Verse {verse} with tafsir {tafsir_name}")
    
    # Define the test query
    test_query = {
        "name": "lookup_tafsir",
        "parameters": {
            "surah": surah,
            "verse": verse,
            "tafsir_name": tafsir_name
        }
    }
    
    # Send the request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:{port}/tools/execute",
            json=test_query,
            timeout=30.0
        )
        
    # Log the results
    logger.info(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info("Tafsir content:")
        if "result" in result and "tafsir_text" in result["result"]:
            text = result["result"]["tafsir_text"]
            # Print the first 500 characters of the tafsir
            logger.info(text[:500] + "..." if len(text) > 500 else text)
        else:
            logger.warning("Unexpected response format")
            logger.info(json.dumps(result, indent=2))
    else:
        logger.error(f"Error: {response.text}")


async def test_all_servers(retriever_port: int = 5000, generator_port: int = 5001, tafsir_port: int = 5002):
    """Test all MCP servers."""
    await test_retriever_server(retriever_port)
    print("\n" + "="*80 + "\n")
    await test_generator_server(generator_port)
    print("\n" + "="*80 + "\n")
    await test_tafsir_server(tafsir_port)


async def main():
    """Parse arguments and run the tests."""
    parser = argparse.ArgumentParser(description='Test MCP servers for RAG Quran')
    parser.add_argument('--server', choices=['all', 'retriever', 'generator', 'tafsir'], 
                        default='all', help='Server to test (default: all)')
    parser.add_argument('--retriever-port', type=int, default=5000, 
                        help='Port for the retriever server (default: 5000)')
    parser.add_argument('--generator-port', type=int, default=5001, 
                        help='Port for the generator server (default: 5001)')
    parser.add_argument('--tafsir-port', type=int, default=5002, 
                        help='Port for the tafsir server (default: 5002)')
    
    args = parser.parse_args()
    
    if args.server == 'all':
        await test_all_servers(
            retriever_port=args.retriever_port,
            generator_port=args.generator_port,
            tafsir_port=args.tafsir_port
        )
    elif args.server == 'retriever':
        await test_retriever_server(args.retriever_port)
    elif args.server == 'generator':
        await test_generator_server(args.generator_port)
    elif args.server == 'tafsir':
        await test_tafsir_server(args.tafsir_port)


if __name__ == "__main__":
    asyncio.run(main())