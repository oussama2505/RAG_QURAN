# Changelog

All notable changes to the RAG_QURAN project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-04-10

### Added
- Initial release with core RAG functionality
- Streamlit web UI for interactive querying
- FastAPI REST API with comprehensive documentation
- Vector embedding search using FAISS
- Multiple embedding model options (OpenAI, HuggingFace)
- Surah and verse filtering capabilities
- Docker support for containerized deployment

### Fixed
- OpenAI API integration issues:
  - Resolved proxy configuration problems
  - Fixed response format handling in OpenAI client
  - Implemented robust error handling for API responses
  - Created fallback mechanisms for API failures

### Changed
- Multiple implementation options for OpenAI integration:
  - Direct OpenAI API integration via `direct_openai.py` 
  - LangChain-based integration with fallback mechanisms
  - Unified LLM client with robust error handling

### Documentation
- Added comprehensive README with setup instructions
- Included usage examples for both API and UI
- Created API documentation with Swagger UI
- Added code comments for better maintainability
