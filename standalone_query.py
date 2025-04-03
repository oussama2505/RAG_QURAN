#!/usr/bin/env python
"""
Standalone RAG Quran Query Script
This script bypasses all the complex LangChain infrastructure and directly 
uses vector similarity search and OpenAI API to provide answers.
"""
import os
import sys
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_PATH = os.path.join(BASE_DIR, 'vector_db')
EMBEDDING_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
OPENAI_MODEL = "gpt-3.5-turbo"

# Load OpenAI API key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable not found")
    print("Please set your API key in the .env file")
    sys.exit(1)

# Initialize the embedding model
print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

def load_faiss_index():
    """Load the FAISS index and document data"""
    import faiss
    
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

def query_faiss(query, k=15):
    """Query the FAISS index and return the top k results"""
    # Load the index and document data
    index, docstore_data = load_faiss_index()
    
    # Encode the query
    query_vector = model.encode(query)
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
    
    return "\n\n".join(context_parts)

def query_openai(context, question):
    """Query OpenAI with the context and question"""
    try:
        print("Querying OpenAI...")
        # Create a clean client with minimal settings
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Create system prompt
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
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error querying OpenAI: {e}")
        return f"Error generating answer: {str(e)}"

def main():
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python standalone_query.py \"Your question about the Quran\"")
        return 1
    
    # Get the query
    query = " ".join(sys.argv[1:])
    
    print("\n" + "="*50)
    print("RAG Quran Query (Standalone Mode)")
    print("="*50)
    
    print(f"\nQuery: {query}")
    
    # Get relevant documents
    print("\nRetrieving relevant documents...")
    results = query_faiss(query)
    
    if not results:
        print("No relevant documents found.")
        return 1
    
    print(f"Found {len(results)} relevant documents")
    
    # Format context
    context = format_context(results)
    
    # Query OpenAI
    answer = query_openai(context, query)
    
    # Display results
    print("\nAnswer:")
    print("-"*50)
    print(answer)
    print("-"*50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
