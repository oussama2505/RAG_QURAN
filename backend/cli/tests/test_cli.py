import pytest
from unittest.mock import patch, MagicMock
from ..main import (
    handle_search,
    handle_translate,
    handle_tafsir,
    handle_config
)

@pytest.mark.asyncio
async def test_handle_search():
    # Mock the orchestrator and its response
    mock_response = MagicMock()
    mock_response.answer = "Test answer"
    mock_response.sources = ["Source 1", "Source 2"]
    mock_response.filters_applied = {"surah": 1, "verse": None}
    
    mock_orchestrator = MagicMock()
    mock_orchestrator.process_query.return_value = mock_response
    
    # Mock the A2AOrchestrator import
    with patch('backend.cli.main.A2AOrchestrator', return_value=mock_orchestrator):
        # Test with text format
        args = MagicMock()
        args.query = "test query"
        args.surah = 1
        args.verse = None
        args.format = "text"
        
        await handle_search(args)
        
        # Test with json format
        args.format = "json"
        await handle_search(args)
        
        # Test with markdown format
        args.format = "markdown"
        await handle_search(args)

@pytest.mark.asyncio
async def test_handle_translate():
    # Mock the translation agent and its response
    mock_response = MagicMock()
    mock_response.translation = "Test translation"
    mock_response.source = "Test source"
    
    mock_agent = MagicMock()
    mock_agent.process.return_value = mock_response
    
    # Mock the TranslationToolAgent import
    with patch('backend.cli.main.TranslationToolAgent', return_value=mock_agent):
        args = MagicMock()
        args.surah = 1
        args.verse = 1
        args.translation = "en-sahih"
        
        await handle_translate(args)

@pytest.mark.asyncio
async def test_handle_tafsir():
    # Mock the tafsir agent and its response
    mock_response = MagicMock()
    mock_response.tafsir_text = "Test tafsir"
    mock_response.tafsir_name = "Test tafsir name"
    
    mock_agent = MagicMock()
    mock_agent.process.return_value = mock_response
    
    # Mock the TafsirToolAgent import
    with patch('backend.cli.main.TafsirToolAgent', return_value=mock_agent):
        args = MagicMock()
        args.surah = 1
        args.verse = 1
        args.tafsir = "ibn_kathir"
        
        await handle_tafsir(args)

@pytest.mark.asyncio
async def test_handle_config():
    # Mock the file operations
    with patch('backend.cli.main.Path') as mock_path:
        mock_config_file = MagicMock()
        mock_config_file.exists.return_value = False
        mock_path.return_value = mock_config_file
        
        args = MagicMock()
        args.api_key = "test_api_key"
        args.model = "gpt-4-turbo"
        
        await handle_config(args)
        
        # Test with existing config
        mock_config_file.exists.return_value = True
        mock_config_file.read_text.return_value = '{"api_key": "old_key", "model": "old_model"}'
        
        await handle_config(args) 