"""
Direct OpenAI API integration that bypasses LangChain's complexities.
This provides a simplified, reliable way to generate answers using OpenAI's API.
"""
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_client():
    """Get an OpenAI API client with the API key from environment"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Create client with minimal configuration to avoid proxy issues
    return openai.OpenAI(api_key=api_key)

def generate_answer_with_openai(context, question, model="gpt-3.5-turbo"):
    """
    Generate an answer using OpenAI API directly
    
    Args:
        context: The context information from retrieved documents
        question: The user's question
        model: The OpenAI model to use
    
    Returns:
        str: The generated answer
    """
    try:
        # Get client
        client = get_openai_client()
        
        # Create prompt
        system_prompt = """You are a knowledgeable Quran scholar assistant. Your task is to provide accurate, respectful, and helpful information about the Quran based on the context provided. Consider different interpretations where relevant, but avoid making claims without textual support.

Context information is below:
-----------------
{context}
-----------------

Given this context, provide a thoughtful response to the user's question. If the context doesn't contain sufficient information to answer fully, acknowledge the limitations while providing what you can based on the available information.

Ensure your response is well-structured with:
1. A direct answer to the question
2. Supporting evidence from the Quran verses and/or tafsir provided in the context
3. If applicable, mention different scholarly interpretations

Cite specific Surah and verse numbers when referencing Quranic text (e.g., "Quran 2:255").
""".format(context=context)

        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0,
            max_tokens=1000
        )
        
        # Handle both legacy and new client response formats
        try:
            # New client format
            return response.choices[0].message.content
        except AttributeError:
            # Legacy client format
            if isinstance(response, dict):
                return response['choices'][0]['message']['content']
            else:
                return str(response)
    
    except Exception as e:
        print(f"Error generating answer with OpenAI: {e}")
        return f"I encountered an error when generating the answer: {str(e)}"