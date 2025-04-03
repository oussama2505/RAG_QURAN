"""
API Key Manager for handling OpenAI API keys in a robust way.
"""
import os
import sys
from dotenv import load_dotenv, find_dotenv

def load_api_key():
    """
    Load the OpenAI API key from environment variables or .env file
    Returns the key if found, None otherwise
    """
    # First try .env file
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path)
    
    # Try to get key from environment
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    # Check if key exists and isn't empty
    if api_key and api_key.strip():
        return api_key.strip()
    
    return None

def ensure_api_key(interactive=True):
    """
    Ensure that the OpenAI API key is available.
    If interactive is True, will prompt the user to enter a key if missing.
    Returns True if key is available, False otherwise.
    """
    api_key = load_api_key()
    
    if api_key:
        # Key already exists
        os.environ["OPENAI_API_KEY"] = api_key
        return True
    
    if not interactive:
        return False
    
    # Interactive mode - ask for key
    print("\nOpenAI API key not found.")
    print("You need an OpenAI API key to use this application.")
    print("You can get one at https://platform.openai.com/account/api-keys")
    
    try:
        user_key = input("\nPlease enter your OpenAI API key: ").strip()
        if not user_key:
            print("No API key provided. Exiting.")
            return False
        
        # Save key to environment for this session
        os.environ["OPENAI_API_KEY"] = user_key
        
        # Ask if user wants to save to .env file
        save = input("Save this API key to .env file for future use? (y/n): ").lower()
        if save == 'y':
            with open('.env', 'a+') as f:
                f.seek(0)
                content = f.read()
                if 'OPENAI_API_KEY' not in content:
                    f.write(f"\nOPENAI_API_KEY={user_key}\n")
                else:
                    print("API key already exists in .env file. Not overwriting.")
        
        return True
    
    except KeyboardInterrupt:
        print("\nAPI key entry cancelled.")
        return False

if __name__ == "__main__":
    # Test the API key loading mechanism
    api_key = load_api_key()
    if api_key:
        print(f"API key found: {api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}")
    else:
        print("No API key found.")
        ensure_api_key()
