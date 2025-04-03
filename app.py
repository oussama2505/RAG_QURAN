#!/usr/bin/env python
"""
Main application for the RAG Quran system.
Provides a simple command-line interface to interact with the RAG system.
"""
import os
import sys
import argparse
from dotenv import load_dotenv
from src.main import initialize_data_and_models, quran_rag_query
from src.api_key_manager import ensure_api_key

def main():
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="RAG Quran - Query the Quran using RAG")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild the vector database")
    parser.add_argument("--query", type=str, help="Query to run (if provided, runs in single query mode)")
    parser.add_argument("--surah", type=int, help="Filter by surah number")
    parser.add_argument("--verse", type=int, help="Filter by verse number")
    parser.add_argument("--sample", type=int, help="Use a sample size for testing")
    
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print("RAG Quran System")
    print("="*50)
    
    try:
        # Ensure OpenAI API key is available
        if not ensure_api_key(interactive=True):
            print("ERROR: OpenAI API key is required to use this application.")
            return 1
        
        print("API key successfully loaded.")
            
        # Initialize the system with optional rebuild
        retriever, generator = initialize_data_and_models(
            rebuild_vector_db=args.rebuild,
            sample_size=args.sample
        )
        
        # Single query mode
        if args.query:
            print(f"\nQuery: {args.query}")
            answer = quran_rag_query(
                args.query, 
                surah_filter=args.surah, 
                verse_filter=args.verse
            )
            print("\nAnswer:")
            print("-"*50)
            print(answer)
            print("-"*50)
            return 0
            
        # Interactive mode
        print("\nEnter your questions about the Quran. Type 'exit' to quit.")
        print("-"*50)
        
        while True:
            try:
                question = input("\nYour question: ")
                if question.lower() in ('exit', 'quit', 'q'):
                    break
                    
                if not question.strip():
                    continue
                    
                # Process filters for surah and verse if provided
                surah_filter = args.surah
                verse_filter = args.verse
                
                # Check for filter commands in the query
                if question.lower().startswith("surah:"):
                    parts = question.split(" ", 1)
                    try:
                        surah_filter = int(parts[0].split(":")[1])
                        question = parts[1] if len(parts) > 1 else ""
                        print(f"Filtering to Surah {surah_filter}")
                    except (ValueError, IndexError):
                        print("Invalid surah filter format. Use 'surah:123 Your question'")
                
                # Get answer
                if question.strip():
                    answer = quran_rag_query(question, surah_filter=surah_filter, verse_filter=verse_filter)
                    print("\nAnswer:")
                    print("-"*50)
                    print(answer)
                    print("-"*50)
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        return 0
    
    except Exception as e:
        print(f"Error initializing RAG Quran system: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
