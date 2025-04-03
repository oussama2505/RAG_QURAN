#!/usr/bin/env python
"""
Direct OpenAI Query Script
This script bypasses all dependencies and directly connects to OpenAI API
to test if the connection works.
"""
import os
import sys
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Get OpenAI API key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable not found")
    print("Please set your API key in the .env file")
    sys.exit(1)

def query_openai(question):
    """Query OpenAI directly"""
    try:
        print("Connecting to OpenAI...")
        # Create a clean client with minimal settings
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # System prompt for the Quran assistant
        system_prompt = """You are a knowledgeable Quran scholar assistant. Your task is to provide accurate, respectful, and helpful information about the Quran. 

This is a test to check if the connection to OpenAI API is working properly.
Please respond with a brief answer about the Quran related to the user's question.
"""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error querying OpenAI: {e}")
        return f"Error: {str(e)}"

def main():
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python direct_openai_query.py \"Your question about the Quran\"")
        return 1
    
    # Get the query
    query = " ".join(sys.argv[1:])
    
    print("\n" + "="*50)
    print("Direct OpenAI Query Test")
    print("="*50)
    
    print(f"\nQuery: {query}")
    
    # Send the query directly to OpenAI
    answer = query_openai(query)
    
    # Display results
    print("\nAnswer:")
    print("-"*50)
    print(answer)
    print("-"*50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
