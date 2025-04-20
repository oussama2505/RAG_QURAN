import argparse
from typing import Optional
from backend.agents.orchestrator import A2AOrchestrator, QuranQueryRequest
from .utils import (
    print_success, print_error, print_warning, print_info,
    with_progress, format_json, format_markdown
)

def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Quran Knowledge Explorer CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for verses about patience
  quran-cli search "What does the Quran say about patience?"
  
  # Search with surah filter
  quran-cli search "What does Surah Al-Baqarah say about fasting?" --surah 2
  
  # Get translation of a specific verse
  quran-cli translate 1 1
  
  # Get tafsir explanation
  quran-cli tafsir 1 1 --tafsir ibn_kathir
  
  # Configure API settings
  quran-cli config --api-key your_api_key --model gpt-4-turbo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search the Quran')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--surah', type=int, help='Filter by surah number')
    search_parser.add_argument('--verse', type=int, help='Filter by verse number')
    search_parser.add_argument('--format', choices=['text', 'json', 'markdown'], default='text',
                             help='Output format (default: text)')
    
    # Translate command
    translate_parser = subparsers.add_parser('translate', help='Get verse translation')
    translate_parser.add_argument('surah', type=int, help='Surah number')
    translate_parser.add_argument('verse', type=int, help='Verse number')
    translate_parser.add_argument('--translation', default='en-sahih',
                                help='Translation to use (default: en-sahih)')
    
    # Tafsir command
    tafsir_parser = subparsers.add_parser('tafsir', help='Get tafsir explanation')
    tafsir_parser.add_argument('surah', type=int, help='Surah number')
    tafsir_parser.add_argument('verse', type=int, help='Verse number')
    tafsir_parser.add_argument('--tafsir', default='ibn_kathir',
                             help='Tafsir to use (default: ibn_kathir)')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure settings')
    config_parser.add_argument('--api-key', help='OpenAI API key')
    config_parser.add_argument('--model', help='Model to use (e.g., gpt-4-turbo)')
    
    return parser

@with_progress("Searching Quran...")
async def handle_search(args: argparse.Namespace) -> None:
    try:
        orchestrator = A2AOrchestrator()
        request = QuranQueryRequest(
            query=args.query,
            surah_filter=args.surah,
            verse_filter=args.verse
        )
        
        response = await orchestrator.process_query(request)
        
        if args.format == 'json':
            print(format_json({
                'answer': response.answer,
                'sources': response.sources,
                'filters_applied': response.filters_applied
            }))
        elif args.format == 'markdown':
            print(format_markdown({
                'answer': response.answer,
                'sources': response.sources,
                'filters_applied': response.filters_applied
            }))
        else:
            print_info(f"\nAnswer:\n{response.answer}\n")
            if response.sources:
                print_info("Sources:")
                for source in response.sources:
                    print(f"- {source}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

@with_progress("Translating verse...")
async def handle_translate(args: argparse.Namespace) -> None:
    try:
        from backend.agents.tools import TranslationToolAgent, TranslationRequest
        
        agent = TranslationToolAgent()
        request = TranslationRequest(
            surah=args.surah,
            verse=args.verse,
            translation=args.translation
        )
        
        response = await agent.process(request)
        
        print_info(f"\nSurah {args.surah}, Verse {args.verse} ({args.translation}):")
        print(f"\n{response.translation}\n")
        print_info(f"Source: {response.source}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

@with_progress("Retrieving tafsir...")
async def handle_tafsir(args: argparse.Namespace) -> None:
    try:
        from backend.agents.tools import TafsirToolAgent, TafsirLookupRequest
        
        agent = TafsirToolAgent()
        request = TafsirLookupRequest(
            surah=args.surah,
            verse=args.verse,
            tafsir_name=args.tafsir
        )
        
        response = await agent.process(request)
        
        print_info(f"\nTafsir for Surah {args.surah}, Verse {args.verse} ({args.tafsir}):")
        print(f"\n{response.tafsir_text}\n")
        print_info(f"Source: {response.tafsir_name}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

async def handle_config(args: argparse.Namespace) -> None:
    try:
        import os
        from pathlib import Path
        
        config_dir = Path.home() / '.quran-cli'
        config_file = config_dir / 'config.json'
        
        # Create config directory if it doesn't exist
        config_dir.mkdir(exist_ok=True)
        
        # Load existing config if it exists
        config = {}
        if config_file.exists():
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
        
        # Update config with new values
        if args.api_key:
            config['api_key'] = args.api_key
        if args.model:
            config['model'] = args.model
        
        # Save updated config
        import json
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print_success("\nConfiguration updated successfully!")
        print_info("\nCurrent configuration:")
        for key, value in config.items():
            if key == 'api_key':
                print(f"{key}: {'*' * len(value)}")
            else:
                print(f"{key}: {value}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

async def main() -> None:
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    handlers = {
        'search': handle_search,
        'translate': handle_translate,
        'tafsir': handle_tafsir,
        'config': handle_config
    }
    
    await handlers[args.command](args)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main()) 