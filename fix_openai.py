#!/usr/bin/env python
"""
Fixed OpenAI implementation that works around proxy issues.
"""
import os
import sys
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Get OpenAI API key
API_KEY = os.environ.get('OPENAI_API_KEY')
if not API_KEY:
    print("Error: OPENAI_API_KEY environment variable not found")
    print("Please set your API key in the .env file")
    sys.exit(1)

def get_openai_client():
    """
    Get an OpenAI client with proxy settings explicitly disabled
    """
    # Create a new clean environment without proxy settings
    env_copy = dict(os.environ)
    for key in list(env_copy.keys()):
        # Remove any HTTP_PROXY, HTTPS_PROXY, etc. variables
        if 'PROXY' in key.upper() or 'proxy' in key.lower():
            del env_copy[key]
    
    # Temporarily update the environment
    old_env = os.environ.copy()
    os.environ.clear()
    os.environ.update(env_copy)
    
    # Create the client with minimal settings
    try:
        client = openai.OpenAI(api_key=API_KEY)
        # Restore original environment
        os.environ.clear()
        os.environ.update(old_env)
        return client
    except Exception as e:
        # Restore original environment even if there was an error
        os.environ.clear()
        os.environ.update(old_env)
        raise e

def query_openai(question):
    """
    Query OpenAI with a direct implementation that works around proxy issues
    """
    try:
        print("Connecting to OpenAI with fixed implementation...")
        client = get_openai_client()
        
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
        print("Usage: python fix_openai.py \"Your question about the Quran\"")
        return 1
    
    # Get the query
    query = " ".join(sys.argv[1:])
    
    print("\n" + "="*50)
    print("Fixed OpenAI Query Test")
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
