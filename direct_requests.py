#!/usr/bin/env python
"""
Direct requests implementation for OpenAI API
This script uses the requests library directly instead of the OpenAI client library
to avoid proxy configuration issues.
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get OpenAI API key
API_KEY = os.environ.get('OPENAI_API_KEY')
if not API_KEY:
    print("Error: OPENAI_API_KEY environment variable not found")
    print("Please set your API key in the .env file")
    sys.exit(1)

def query_openai_with_requests(question):
    """
    Query OpenAI API directly using the requests library
    """
    try:
        print("Connecting to OpenAI with direct requests...")
        
        # OpenAI API endpoint
        url = "https://api.openai.com/v1/chat/completions"
        
        # Headers with API key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # System prompt for the Quran assistant
        system_prompt = """You are a knowledgeable Quran scholar assistant. Your task is to provide accurate, respectful, and helpful information about the Quran. 

This is a test to check if the connection to OpenAI API is working properly.
Please respond with a brief answer about the Quran related to the user's question.
"""
        
        # Request payload
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "temperature": 0
        }
        
        # Make the request with explicitly no proxies
        response = requests.post(
            url, 
            headers=headers, 
            json=payload,
            proxies=None,  # Explicitly disable proxies
            timeout=30
        )
        
        # Check for successful response
        if response.status_code == 200:
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return f"Error: API returned status code {response.status_code}"
            
    except Exception as e:
        print(f"Error querying OpenAI: {e}")
        return f"Error: {str(e)}"

def main():
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python direct_requests.py \"Your question about the Quran\"")
        return 1
    
    # Get the query
    query = " ".join(sys.argv[1:])
    
    print("\n" + "="*50)
    print("Direct Requests OpenAI Query Test")
    print("="*50)
    
    print(f"\nQuery: {query}")
    
    # Send the query directly to OpenAI using requests
    answer = query_openai_with_requests(query)
    
    # Display results
    print("\nAnswer:")
    print("-"*50)
    print(answer)
    print("-"*50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
