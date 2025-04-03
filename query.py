#!/usr/bin/env python
"""
Simple script to run queries against the RAG Quran system.
This is a simplified version that avoids API key prompts.
"""
import os
import sys
from dotenv import load_dotenv
from src.main import initialize_data_and_models, quran_rag_query

def main():
    # Load environment variables
    load_dotenv()
    
    # Ensure we have a query
    if len(sys.argv) < 2:
        print("Usage: python query.py \"Your question about the Quran\"")
        return 1
    
    # Get the query from command line
    query = " ".join(sys.argv[1:])
    
    print("\n" + "="*50)
    print("RAG Quran Query")
    print("="*50)
    
    # Force loading API key from environment
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        # Try to read from .env file directly
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.strip().startswith('OPENAI_API_KEY='):
                        key = line.strip().split('=', 1)[1].strip()
                        if key:
                            os.environ["OPENAI_API_KEY"] = key
                            print("API key loaded from .env file")
                            break
        except Exception as e:
            print(f"Error reading .env file: {e}")
    
    try:
        # Initialize the models
        print("\nInitializing models...")
        retriever, generator = initialize_data_and_models(rebuild_vector_db=False)
        
        # Run the query
        print(f"\nQuery: {query}")
        print("\nProcessing...")
        
        answer = quran_rag_query(query)
        
        print("\nAnswer:")
        print("-"*50)
        print(answer)
        print("-"*50)
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
