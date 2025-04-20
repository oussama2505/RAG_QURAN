# RAG Quran: A2A & MCP Integration Guide

This guide explains how to use the agent-to-agent (A2A) communication and Model Context Protocol (MCP) integration in the RAG Quran project.

## Architecture Overview

The RAG Quran system has been enhanced with two complementary frameworks:

1. **A2A (Agent-to-Agent)**: Enables standardized communication between different components of the system
2. **MCP (Model Context Protocol)**: Exposes these components as servers that can be accessed by external clients

### Components

The system consists of the following components:

- **Retriever Agent**: Finds relevant Quranic passages based on queries
- **Generator Agent**: Creates answers based on retrieved context
- **Tafsir Tool Agent**: Provides direct lookup of tafsir explanations
- **A2A Orchestrator**: Coordinates communication between agents
- **MCP Servers**: Expose agents through standardized protocol

## Using A2A Components

### A2A Orchestrator

The orchestrator provides a unified interface to the entire RAG Quran system:

```python
from backend.agents.orchestrator import A2AOrchestrator, QuranQueryRequest

# Create the orchestrator
orchestrator = A2AOrchestrator()

# Create a query request
request = QuranQueryRequest(
    query="What does the Quran say about patience?",
    surah_filter=None,  # Optional surah filter
    verse_filter=None,  # Optional verse filter
    model_name="gpt-3.5-turbo",  # LLM to use
    use_direct_tafsir=False  # Whether to also get direct tafsir
)

# Process the query
response = await orchestrator.process_query(request)

# Access the response
print(response.answer)  # The generated answer
print(response.sources)  # The sources used in the answer
```

### Individual Agents

You can also use the agents individually:

#### Retriever Agent

```python
from backend.agents.retriever import RetrieverAgent, RetrieverAgentRequest

# Create the agent
retriever_agent = RetrieverAgent()

# Create a request
request = RetrieverAgentRequest(
    query="What does the Quran say about patience?",
    surah_filter=None,  # Optional
    verse_filter=None,  # Optional
)

# Process the request
response = await retriever_agent.process(request)

# Access the response
print(response.formatted_context)  # Formatted context from retrieved documents
print(response.documents)  # List of retrieved documents
```

#### Generator Agent

```python
from backend.agents.generator import GeneratorAgent, GeneratorAgentRequest

# Create the agent
generator_agent = GeneratorAgent(model_name="gpt-3.5-turbo")

# Create a request with context from the retriever
request = GeneratorAgentRequest(
    query="What does the Quran say about patience?",
    context="[Quran 2:153]: O you who have believed, seek help through patience and prayer...",
)

# Process the request
response = await generator_agent.process(request)

# Access the response
print(response.answer)  # The generated answer
print(response.sources)  # The sources used in the answer
```

#### Tafsir Tool Agent

```python
from backend.agents.tools import TafsirToolAgent, TafsirLookupRequest

# Create the agent
tafsir_agent = TafsirToolAgent()

# Create a request
request = TafsirLookupRequest(
    query="Get tafsir for Surah 1, Verse 1",
    surah=1,
    verse=1,
    tafsir_name=None  # Optional, will use default if not specified
)

# Process the request
response = await tafsir_agent.process(request)

# Access the response
print(response.tafsir_text)  # The tafsir explanation
print(response.tafsir_name)  # The name of the tafsir
```

## Using MCP Servers

The MCP servers expose the RAG Quran functionality to external clients through a standardized protocol.

### Starting MCP Servers

```bash
# Start all servers (retriever, generator, tafsir)
python -m backend.mcp_servers.run_servers

# Start a specific server
python -m backend.mcp_servers.run_servers --server retriever --port 5000
```

### Server Endpoints

All MCP servers expose the following endpoints:

- `/capabilities`: Get server capabilities
- `/tools/list`: List available tools
- `/tools/execute`: Execute a tool

### Example Requests

#### Retriever Server (default port: 5000)

```json
POST /tools/execute
{
    "name": "retrieve",
    "parameters": {
        "query": "What does the Quran say about patience?",
        "surah_filter": null,
        "verse_filter": null,
        "k": 5,
        "use_compression": true
    }
}
```

#### Generator Server (default port: 5001)

```json
POST /tools/execute
{
    "name": "generate_answer",
    "parameters": {
        "query": "What does the Quran say about patience?",
        "context": "[Quran 2:153]: O you who have believed, seek help through patience and prayer...",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.0
    }
}
```

#### Tafsir Server (default port: 5002)

```json
POST /tools/execute
{
    "name": "lookup_tafsir",
    "parameters": {
        "surah": 1,
        "verse": 1,
        "tafsir_name": "ar-tafsir-ibn-kathir"
    }
}
```

### Using with MCP Clients

Any MCP-compatible client can connect to these servers, including:

- Claude Desktop
- VS Code extensions with MCP support
- Custom applications using the MCP client libraries

## Running Tests

### Testing A2A Integration

```bash
# Run the A2A test script
python -m backend.agents.test_a2a
```

### Testing MCP Servers

```bash
# Start the MCP servers
python -m backend.mcp_servers.run_servers

# In a separate terminal, run the MCP test script
python -m backend.mcp_servers.test_mcp
```

## Extending the System

### Adding New Agents

To add a new agent to the system:

1. Create a new agent class that extends `BaseAgent`
2. Implement the `process` and `get_capabilities` methods
3. Update the orchestrator to include the new agent
4. Create an MCP server for the new agent

### Adding New Tools

To add a new tool:

1. Create a new tool agent class that extends `BaseAgent`
2. Implement the tool functionality in the `process` method
3. Add the tool to the orchestrator if needed
4. Create an MCP server for the tool

## Troubleshooting

- **MCP Server Connection Issues**: Ensure the server is running and the port is correct
- **Agent Errors**: Check the logs for error messages
- **Model API Errors**: Verify API keys and model availability