#!/usr/bin/env python
"""
RAG Quran Query with Direct Requests
This script integrates the direct requests approach with the RAG system
to provide answers about the Quran.
"""
import os
import sys
import json
import requests
import numpy as np
import faiss
from dotenv import load_dotenv
from src.config import VECTOR_DB_PATH
from src.embeddings import get_embedding_model

# Load environment variables
load_dotenv()

# Get OpenAI API key
API_KEY = os.environ.get('OPENAI_API_KEY')
if not API_KEY:
    print("Error: OPENAI_API_KEY environment variable not found")
    print("Please set your API key in the .env file")
    sys.exit(1)

def load_faiss_index():
    """Load the FAISS index and document data"""
    index_path = os.path.join(VECTOR_DB_PATH, "faiss_index")
    if not os.path.exists(index_path):
        print(f"Error: FAISS index not found at {index_path}")
        print("Please run the main application first to create the vector database")
        sys.exit(1)
    
    # Load the index
    index = faiss.read_index(os.path.join(index_path, "index.faiss"))
    
    # Load the documents
    with open(os.path.join(index_path, "docstore.json"), 'r') as f:
        docstore_data = json.load(f)
    
    return index, docstore_data

def query_vector_db(query, embeddings, k=15):
    """Query the vector database with the embedded query"""
    print(f"Retrieving documents for query: {query}...")
    
    # Load the index and document data
    index, docstore_data = load_faiss_index()
    
    # Embed the query
    query_vector = embeddings.embed_query(query)
    query_vector = np.array([query_vector]).astype('float32')
    
    # Search the index
    distances, indices = index.search(query_vector, k)
    
    # Get the documents
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < 0 or idx >= len(docstore_data['docstore']['_dict']):
            continue
            
        doc_id = str(idx)
        if doc_id in docstore_data['docstore']['_dict']:
            doc_info = docstore_data['docstore']['_dict'][doc_id]
            doc_content = doc_info.get('text', '')
            doc_metadata = doc_info.get('metadata', {})
            
            results.append({
                'content': doc_content,
                'metadata': doc_metadata,
                'score': float(distances[0][i])
            })
    
    print(f"Retrieved {len(results)} relevant documents")
    return results

def format_context(results):
    """Format the search results into a context string"""
    if not results:
        return "No relevant information found."
    
    context_parts = []
    seen_refs = set()
    
    for doc in results:
        content = doc['content']
        metadata = doc['metadata']
        
        source = metadata.get('source', 'unknown')
        ref = metadata.get('reference', '')
        
        # Skip duplicates
        ref_key = f"{source}:{ref}"
        if ref_key in seen_refs:
            continue
        seen_refs.add(ref_key)
        
        # Format differently based on source
        if source == "quran":
            context_parts.append(f"[Quran {ref}]: {content}")
        elif source.startswith("tafsir_"):
            tafsir_name = source.replace("tafsir_", "")
            context_parts.append(f"[Tafsir {tafsir_name} on {ref}]: {content}")
        else:
            # Generic format for other sources
            context_parts.append(f"[{source} {ref}]: {content}")
    
    # Show sources for debugging
    sources = [f"{doc['metadata'].get('source', 'unknown')}: {doc['metadata'].get('reference', 'unknown')}" 
              for doc in results]
    print(f"Sources: {sources}")
    
    return "\n\n".join(context_parts)

def query_openai_with_requests(context, question):
    """
    Query OpenAI API directly using the requests library
    """
    try:
        print("Generating answer with OpenAI...")
        
        # OpenAI API endpoint
        url = "https://api.openai.com/v1/chat/completions"
        
        # Headers with API key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # System prompt for the Quran assistant
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
        print("Usage: python rag_direct.py \"Your question about the Quran\"")
        return 1
    
    # Get the query
    query = " ".join(sys.argv[1:])
    
    print("\n" + "="*50)
    print("RAG Quran System (Direct Implementation)")
    print("="*50)
    
    print(f"\nQuery: {query}")
    
    # Initialize embeddings
    print("Initializing embeddings...")
    embeddings = get_embedding_model(model_type="huggingface")
    
    # Get relevant documents
    results = query_vector_db(query, embeddings)
    
    if not results:
        print("No relevant documents found.")
        return 1
    
    # Format context
    context = format_context(results)
    
    # Query OpenAI
    answer = query_openai_with_requests(context, query)
    
    # Display results
    print("\nAnswer:")
    print("-"*50)
    print(answer)
    print("-"*50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
