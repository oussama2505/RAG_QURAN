"""
Run MCP servers for RAG Quran.
This script starts all MCP servers for the RAG Quran project.
"""

import argparse
import asyncio
import logging
import os
import sys
from typing import List

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modelcontextprotocol import start_server

# Import our MCP servers
from backend.mcp_servers.retriever.server import create_server as create_retriever_server
from backend.mcp_servers.generator.server import create_server as create_generator_server
from backend.mcp_servers.tafsir.server import create_server as create_tafsir_server
from backend.mcp_servers.summarizer.server import create_server as create_summarizer_server
from backend.mcp_servers.translation.server import create_server as create_translation_server


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_servers")


async def run_server(server_type: str, port: int):
    """
    Run a specific MCP server.
    
    Args:
        server_type: Type of server to run ('retriever', 'generator', 'tafsir', 'summarizer', or 'translation')
        port: Port to run the server on
    """
    try:
        # Create the appropriate server
        if server_type == 'retriever':
            server = create_retriever_server()
        elif server_type == 'generator':
            server = create_generator_server()
        elif server_type == 'tafsir':
            server = create_tafsir_server()
        elif server_type == 'summarizer':
            server = create_summarizer_server()
        elif server_type == 'translation':
            server = create_translation_server()
        else:
            logger.error(f"Unknown server type: {server_type}")
            return
        
        # Start the server
        logger.info(f"Starting {server_type} server on port {port}")
        await start_server(server, port=port)
        
    except Exception as e:
        logger.error(f"Error starting {server_type} server: {e}")


async def run_all_servers(ports: List[int] = None):
    """
    Run all MCP servers.
    
    Args:
        ports: List of ports to run servers on [retriever_port, generator_port, tafsir_port, summarizer_port, translation_port]
    """
    if not ports:
        ports = [5000, 5001, 5002, 5003, 5004]
    
    # Create tasks for all servers
    tasks = [
        run_server('retriever', ports[0]),
        run_server('generator', ports[1]),
        run_server('tafsir', ports[2]),
        run_server('summarizer', ports[3]),
        run_server('translation', ports[4])
    ]
    
    # Run all servers concurrently
    logger.info(f"Starting all MCP servers on ports {ports}")
    await asyncio.gather(*tasks)


def main():
    """Parse arguments and run the appropriate servers."""
    parser = argparse.ArgumentParser(description='Run MCP servers for RAG Quran')
    parser.add_argument('--server', choices=['all', 'retriever', 'generator', 'tafsir', 'summarizer', 'translation'], 
                        default='all', help='Server to run (default: all)')
    parser.add_argument('--port', type=int, help='Port to run the server on')
    parser.add_argument('--retriever-port', type=int, default=5000, 
                        help='Port for the retriever server (default: 5000)')
    parser.add_argument('--generator-port', type=int, default=5001, 
                        help='Port for the generator server (default: 5001)')
    parser.add_argument('--tafsir-port', type=int, default=5002, 
                        help='Port for the tafsir server (default: 5002)')
    parser.add_argument('--summarizer-port', type=int, default=5003, 
                        help='Port for the summarizer server (default: 5003)')
    parser.add_argument('--translation-port', type=int, default=5004, 
                        help='Port for the translation server (default: 5004)')
    
    args = parser.parse_args()
    
    if args.server == 'all':
        # Run all servers
        ports = [
            args.retriever_port, 
            args.generator_port, 
            args.tafsir_port, 
            args.summarizer_port,
            args.translation_port
        ]
        asyncio.run(run_all_servers(ports))
    else:
        # Run a specific server
        port = args.port or {
            'retriever': args.retriever_port,
            'generator': args.generator_port,
            'tafsir': args.tafsir_port,
            'summarizer': args.summarizer_port,
            'translation': args.translation_port
        }[args.server]
        
        asyncio.run(run_server(args.server, port))


if __name__ == "__main__":
    main()