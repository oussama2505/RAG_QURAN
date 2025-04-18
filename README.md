# Quran Knowledge Explorer - RAG System

![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)
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

## Project Structure

```
RAG_QURAN/
├── backend/              # Backend code
│   ├── __init__.py       # Package initialization
│   ├── api/              # API layer
│   │   ├── __init__.py   # Package initialization 
│   │   └── routes.py     # FastAPI implementation
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

## Further Development

Some ideas for extending this project:

1. Add support for multiple languages
2. Implement user feedback mechanisms to improve responses
3. Add more advanced filters (by topic, theme, etc.)
4. Integrate additional tafsirs and scholarly sources
5. Add parallel texts (Arabic + translations)

## Resources for Learning More About RAG Systems

- [LangChain Documentation](https://python.langchain.com/docs/modules/data_connection/)
- [OpenAI Cookbook: RAG with OpenAI embeddings](https://github.com/openai/openai-cookbook)
- [Haystack Documentation](https://docs.haystack.deepset.ai/)
- [Chroma Vector Database](https://docs.trychroma.com/)

## Changelog

### Version 1.2.0 (2025-04-17)

- Refactored project structure for better organization
  - Moved core implementation to `backend/core`
  - Moved API implementation to `backend/api`
  - Updated imports and configuration files
- Updated Docker configuration to work with new structure
- Updated documentation

### Version 1.0.0 (2025-04-10)

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
