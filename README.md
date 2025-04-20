# Quran Knowledge Explorer - RAG System

![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A Retrieval-Augmented Generation (RAG) system for exploring and understanding the Quran. This system combines the power of vector embeddings for semantic search with OpenAI's language models to provide accurate and contextually relevant answers about the Quran.

## Features

- **Semantic search** through Quranic verses and tafsirs (explanations)
- **Contextual answers** generated using advanced LLMs (using OpenAI)
- **Filter by surah and verse** to narrow down your queries
- **Modern UI**: Svelte-based frontend with REST API backend
- **Docker support** for easy deployment
- **Robust error handling** for OpenAI API integration
- **Multiple fallback mechanisms** for reliable operation
- **Direct and LangChain** implementations for flexibility
- **A2A Integration**: Agent-to-agent communication using Google's A2A protocol
- **MCP Support**: Model Context Protocol servers for standardized AI access

## Project Structure

```
RAG_QURAN/
├── backend/              # Backend code
│   ├── __init__.py       # Package initialization
│   ├── api/              # API layer
│   │   ├── __init__.py   # Package initialization
│   │   └── routes.py     # FastAPI implementation
│   ├── agents/           # A2A agent implementations
│   │   ├── base/         # Base agent interfaces
│   │   ├── retriever/    # Retriever agent
│   │   ├── generator/    # Generator agent
│   │   ├── tools/        # Tool agents
│   │   ├── orchestrator.py # A2A orchestration
│   │   └── test_a2a.py   # A2A test script
│   ├── mcp_servers/      # MCP server implementations
│   │   ├── retriever/    # Retriever server
│   │   ├── generator/    # Generator server
│   │   ├── tafsir/       # Tafsir tool server
│   │   ├── base_server.py # Base MCP server
│   │   ├── run_servers.py # Server runner
│   │   └── test_mcp.py   # MCP test script
│   └── core/             # Core implementation
│       ├── __init__.py   # Package initialization
│       ├── api_key_manager.py # API key management
│       ├── config.py     # Configuration settings
│       ├── data_processing.py # Data loading and processing
│       ├── direct_openai.py # Direct OpenAI API integration
│       ├── embeddings.py # Vector embeddings implementation
│       ├── generator.py  # Answer generation with LLM
│       ├── llm_client.py # Unified LLM client implementation
│       ├── main.py       # Main orchestration code
│       └── retriever.py  # Retrieval components
├── frontend/             # Svelte frontend
│   ├── src/              # Frontend source code
│   └── public/           # Static assets
├── data/                 # Data directory
│   ├── quran.json        # Quran text in JSON format
│   └── tafsirs/          # Directory for tafsir JSON files
├── vector_db/            # Vector database storage (created on first run)
├── A2A/                  # A2A protocol repository (cloned)
├── INTEGRATION_GUIDE.md  # A2A/MCP integration guide
├── INTEGRATION_PLAN.md   # A2A/MCP integration plan
├── .env                  # Environment variables
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Multi-container Docker setup
└── requirements.txt      # Python dependencies
```

## Prerequisites

- Python 3.8+ (if running locally)
- Docker and Docker Compose (if using containerized approach)
- OpenAI API key

## Data Preparation

The system expects Quran and tafsir data in a specific format. Prepare your data as follows:

1. Create the data directory:

   ```bash
   mkdir -p data/tafsirs
   ```

2. Add `quran.json` file in the `data` directory with this structure:

   ```json
   {
     "surahs": [
       {
         "number": 1,
         "name": "Al-Fatihah",
         "verses": [
           {
             "number": 1,
             "text": "Bismillah ar-Rahman ar-Raheem"
           },
           ...
         ]
       },
       ...
     ]
   }
   ```

3. Add tafsir files (e.g., `ibn_kathir.json`, `tabari.json`) in the `data/tafsirs` directory with this structure:
   ```json
   [
     {
       "reference": "1:1",
       "explanation": "Explanation of the first verse..."
     },
     ...
   ]
   ```

## Installation and Setup

### Option 1: Using Docker (Recommended)

1. Clone the repository or prepare the files as shown in the project structure.

2. Set up your `.env` file with your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Build and start the containers:

   ```bash
   docker-compose up -d
   ```

4. Access the services:
   - Frontend UI: http://localhost:5173
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Installation

1. Clone the repository or prepare the files as shown in the project structure.

2. Backend Setup:

   ```bash
   python -m venv quran_env
   source quran_env/bin/activate  # On Windows: quran_env\Scripts\activate
   pip install -r requirements.txt
   ```

3. Frontend Setup:

   ```bash
   cd frontend
   npm install
   ```

4. Set up your `.env` file with your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. Run the applications:
   - Start the API:
     ```bash
     cd path/to/RAG_QURAN
     uvicorn backend.api.routes:app --reload
     ```
   - Start the Frontend:
     ```bash
     cd frontend
     npm run dev
     ```

## Usage

### Using the Frontend

1. Open http://localhost:5173 in your browser
2. Enter your question about the Quran in the search field
3. Use the filters to narrow down your search by surah and verse
4. Submit your query to receive a detailed response with relevant verses and explanations

### Using the API

#### REST API Endpoints

- `GET /api/ask?question=your_question&surah=1&verse=1`
- `POST /api/ask` with JSON body:
  ```json
  {
    "question": "What does the Quran say about patience?",
    "surah_filter": 2,
    "verse_filter": 153
  }
  ```

#### Python Example

```python
import requests

# For GET request
response = requests.get(
    "http://localhost:8000/api/ask",
    params={"question": "What does Surah Al-Baqarah say about fasting?", "surah": 2}
)

# For POST request
response = requests.post(
    "http://localhost:8000/api/ask",
    json={
        "question": "What does Surah Al-Baqarah say about fasting?",
        "surah_filter": 2
    }
)

print(response.json())
```

## Customization

### Changing the LLM Model

You can change the OpenAI model by updating the `.env` file:

```
LLM_MODEL_NAME=gpt-4-turbo
```

Supported models include:

- gpt-4-turbo
- gpt-4
- gpt-3.5-turbo

### OpenAI Integration Options

The system provides multiple options for OpenAI integration:

1. **Direct Integration** - Uses `backend.core.direct_openai` to communicate directly with OpenAI API, bypassing LangChain.

   - More reliable for some environments
   - Simpler error handling
   - Recommended for production use

2. **LangChain Integration** - Uses LangChain for OpenAI integration.
   - More extensible
   - Better for complex chains and agents
   - Falls back to direct integration if it fails

### Changing the Embedding Model

You can use different embedding models by setting the `EMBEDDING_MODEL_TYPE` in your `.env` file:

```
EMBEDDING_MODEL_TYPE=openai  # Uses OpenAI embeddings (default)
EMBEDDING_MODEL_TYPE=huggingface  # Uses Hugging Face embeddings (local)
```

### Using A2A and MCP Features

#### Agent-to-Agent (A2A) Communication

The system now supports agent-to-agent communication using Google's A2A protocol:

```python
from backend.agents.orchestrator import A2AOrchestrator, QuranQueryRequest

# Create the orchestrator
orchestrator = A2AOrchestrator()

# Create a query request
request = QuranQueryRequest(
    query="What does the Quran say about patience?",
    surah_filter=None,  # Optional surah filter
    verse_filter=None   # Optional verse filter
)

# Process the query
response = await orchestrator.process_query(request)

# Access the response
print(response.answer)          # The generated answer
print(response.sources)         # The sources used
print(response.filters_applied) # Filters that were applied
```

#### Model Context Protocol (MCP) Servers

The system provides MCP servers for standardized AI access:

1. Start the MCP servers:

   ```bash
   cd backend
   python -m mcp_servers.run_servers
   ```

2. Access the servers via HTTP:

   - Retriever server: http://localhost:5000
   - Generator server: http://localhost:5001
   - Tafsir server: http://localhost:5002

3. Use with any MCP-compatible client, including Claude Desktop and other AI tools.

For detailed usage examples and API documentation, refer to the `INTEGRATION_GUIDE.md` file.

## Further Development

Some ideas for extending this project:

1. Add support for multiple languages
2. Implement user feedback mechanisms to improve responses
3. Add more advanced filters (by topic, theme, etc.)
4. Integrate additional tafsirs and scholarly sources
5. Add parallel texts (Arabic + translations)
6. Create additional A2A agents for specialized tasks
7. Build a CLI interface for the A2A orchestrator
8. Expose more MCP tools for external AI systems

## Resources for Learning More About RAG Systems

- [LangChain Documentation](https://python.langchain.com/docs/modules/data_connection/)
- [OpenAI Cookbook: RAG with OpenAI embeddings](https://github.com/openai/openai-cookbook)
- [Haystack Documentation](https://docs.haystack.deepset.ai/)
- [Chroma Vector Database](https://docs.trychroma.com/)

## Changelog

### Version 1.4.0 (2025-04-17)

- Added Agent-to-Agent (A2A) communication capabilities
  - Implemented modular agent architecture
  - Created retriever, generator, and tool agents
  - Added agent orchestration for seamless workflow
- Added Model Context Protocol (MCP) integration
  - Created MCP servers for each component
  - Exposed standardized APIs for AI access
  - Added testing and documentation
- Updated project structure to accommodate new components
- Added comprehensive integration guide
- Added test scripts for A2A and MCP features

### Version 1.4.0 (2025-04-17)

- Refactored project structure for better organization
  - Moved core implementation to `backend/core`
  - Moved API implementation to `backend/api`
  - Updated imports and configuration files
- Updated Docker configuration to work with new structure
- Updated documentation

### Version 1.4.0 (2025-04-10)

- Initial release with core RAG functionality
- Multiple implementation options for OpenAI integration:
  - Direct OpenAI API integration via `direct_openai.py`
  - LangChain-based integration with fallback mechanisms
  - Unified LLM client with robust error handling
- Fixed issues with OpenAI API response handling
- Added detailed documentation and examples
- Implemented API and Streamlit interfaces

## License

MIT

## CLI Installation and Usage

### Installation

1. Install the CLI tool:

```bash
pip install -e .
```

This will install the `quran-cli` command globally.

### Usage

The CLI provides several commands for interacting with the Quran Knowledge Explorer:

#### Search Command

Search the Quran for specific topics or verses:

```bash
quran-cli search "What does the Quran say about patience?"
```

Filter by surah and verse:

```bash
quran-cli search "What does Surah Al-Baqarah say about fasting?" --surah 2
```

Specify output format (text, json, or markdown):

```bash
quran-cli search "What does the Quran say about patience?" --format json
```

#### Translation Command

Get translations of specific verses:

```bash
quran-cli translate 1 1
```

Specify translation:

```bash
quran-cli translate 1 1 --translation en-sahih
```

#### Tafsir Command

Get tafsir explanations:

```bash
quran-cli tafsir 1 1
```

Specify tafsir:

```bash
quran-cli tafsir 1 1 --tafsir ibn_kathir
```

#### Configuration

Set up your API key and model preferences:

```bash
quran-cli config --api-key your_api_key --model gpt-4-turbo
```

### Help

Get help for any command:

```bash
quran-cli --help
quran-cli search --help
quran-cli translate --help
quran-cli tafsir --help
quran-cli config --help
```

## Troubleshooting

### Common Issues

1. **API Key Not Set**

   - Error: "API key not configured"
   - Solution: Run `quran-cli config --api-key your_api_key`

2. **Invalid Model Name**

   - Error: "Invalid model name"
   - Solution: Use one of the supported models (e.g., gpt-4-turbo, gpt-3.5-turbo)

3. **Network Issues**

   - Error: "Failed to connect to API"
   - Solution: Check your internet connection and API endpoint configuration

4. **Invalid Surah/Verse Numbers**

   - Error: "Invalid surah or verse number"
   - Solution: Use valid surah numbers (1-114) and verse numbers within the surah's range

5. **Configuration File Issues**
   - Error: "Failed to read/write configuration"
   - Solution: Check file permissions in `~/.quran-cli/config.json`

### Getting Help

If you encounter any issues not covered above:

1. Check the error message for specific details
2. Run the command with `--verbose` flag for more information
3. Check the logs in `~/.quran-cli/logs/`
4. Open an issue on GitHub with:
   - The command you were trying to run
   - The complete error message
   - Your system information (OS, Python version)
   - Steps to reproduce the issue
