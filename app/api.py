# app/api.py
import sys
import os
import json
import numpy as np
import faiss
import requests
import time
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings  # Add this import at the top with other imports

# Add the project root to the path so we can import the src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import VECTOR_DB_PATH
from src.embeddings import get_embedding_model
from src.api_key_manager import load_api_key, ensure_api_key
from src.generator import generate_answer, create_answer_generator

# Direct OpenAI function for fallback mode
def generate_direct_answer(question, api_key):
    """Generate an answer using OpenAI directly, without RAG components.
    Based on our previous successful solution in openai_query.py"""
    import requests
    import json
    
    print("Using direct OpenAI implementation with requests")
    
    # Create a system prompt about Quran knowledge
    system_prompt = """You are a knowledgeable Quran scholar assistant. Your task is to provide accurate, respectful, and helpful information about the Quran. Consider different interpretations where relevant, but avoid making claims without textual support.

Please answer questions about the Quran based on your knowledge. If you don't know the answer or aren't sure, acknowledge the limitations of your knowledge while providing what information you can.

Ensure your response is well-structured with:
1. A direct answer to the question
2. Supporting evidence from the Quran if available in your knowledge
3. If applicable, mention different scholarly interpretations

Cite specific Surah and verse numbers when possible (e.g., "Quran 2:255").
"""
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Convert messages to JSON
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
    
    request_body = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0
    })
    
    # Disable proxies explicitly (key fix from previous successful solution)
    proxies = {"http": None, "https": None}
    
    try:
        # Make the API call with explicit proxy settings and error handling
        print("Sending request to OpenAI API...")
        response = requests.post(
            url, 
            headers=headers, 
            data=request_body,  # Using data instead of json parameter
            proxies=proxies,  
            timeout=45,
            verify=True  # Verify SSL certificates
        )
        
        # Debug info
        print(f"OpenAI API Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                answer = response_data['choices'][0]['message']['content']
                print("Successfully received answer from OpenAI")
                return answer
            except (KeyError, json.JSONDecodeError) as e:
                print(f"Error parsing OpenAI response: {str(e)}")
                print(f"Response content: {response.text[:200]}...")
                return f"Error: Failed to parse the response. Details: {str(e)}"
        else:
            print(f"OpenAI API Error Response: {response.text}")
            return f"Error: API returned status code {response.status_code}. Please check your OpenAI API key."
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return f"Error: Failed to communicate with OpenAI API. Details: {str(e)}"

# Enable debug mode for easier troubleshooting
DEBUG_MODE = False

# Enable fallback mode to work without embeddings
FALLBACK_MODE = False

# Initialize the FastAPI app
app = FastAPI(
    title="Quran Knowledge Explorer API",
    description="API for querying information about the Quran using RAG technology",
    version="1.0.0"
)

# Global variables to store models and data
embeddings = None
index = None
docstore_data = None
rag_system_ready = False
initialization_error = None

# Load environment variables
load_dotenv()

# Initialize the RAG system on startup
@app.on_event("startup")
async def startup_event():
    global embeddings, index, docstore_data, rag_system_ready, initialization_error
    
    try:
        # Check API key
        if ensure_api_key(interactive=False):
            print("✅ API key loaded successfully")
        else:
            print("⚠️ WARNING: OpenAI API key not found")
            print("Some functionality may not work without an API key")
        
        # Use basic embeddings for testing
        print("Initializing basic embeddings for testing...")
        class BasicEmbeddings(Embeddings):
            def embed_documents(self, texts):
                return [[1.0] * 384 for _ in texts]
            def embed_query(self, text):
                return [1.0] * 384
        
        embeddings = BasicEmbeddings()
        print("✅ Successfully initialized basic embeddings")
        
        try:
            # Load FAISS index
            index_path = os.path.join(VECTOR_DB_PATH, "faiss_index")
            if not os.path.exists(index_path):
                print(f"❌ ERROR: FAISS index directory not found at {index_path}")
                raise FileNotFoundError(f"FAISS index directory not found at {index_path}")
            
            if not os.path.exists(os.path.join(index_path, "index.faiss")):
                print(f"❌ ERROR: index.faiss file not found in {index_path}")
                raise FileNotFoundError(f"index.faiss file not found in {index_path}")
            
            print("Loading FAISS index...")
            index = faiss.read_index(os.path.join(index_path, "index.faiss"))
            print("✅ FAISS index loaded successfully")
            
            if not os.path.exists(os.path.join(index_path, "docstore.json")):
                print(f"❌ ERROR: docstore.json file not found in {index_path}")
                raise FileNotFoundError(f"docstore.json file not found in {index_path}")
            
            # Load the documents
            print("Loading document store...")
            with open(os.path.join(index_path, "docstore.json"), 'r') as f:
                docstore_data = json.load(f)
            
            doc_count = len(docstore_data['docstore']['_dict'])
            print(f"✅ Loaded {doc_count} documents")
            if doc_count == 0:
                print("❌ WARNING: Document store is empty")
        except Exception as idx_error:
            print(f"❌ ERROR loading vector database: {str(idx_error)}")
            raise
        
        # Set RAG system as ready
        rag_system_ready = True
        print("✅ RAG system initialized successfully")
    
    except Exception as e:
        initialization_error = str(e)
        print(f"❌ Error initializing RAG system: {initialization_error}")
        print("Entering fallback mode - API will still function but RAG capabilities may be limited")
        # We'll continue anyway and enter fallback mode

# Request model
class QuestionRequest(BaseModel):
    question: str
    surah_filter: Optional[int] = None
    verse_filter: Optional[int] = None

# Source item model
class SourceItem(BaseModel):
    source_type: str
    reference: str
    content: str

# Response model
class AnswerResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    filters_applied: Dict[str, Any]

# Helper functions to work with our src modules in the API
def retrieve_documents(query, filters=None):
    """Retrieve relevant documents from vector database"""
    global embeddings, index, docstore_data, rag_system_ready
    
    start_time = time.time()
    
    # Check if we're in fallback mode
    if FALLBACK_MODE:
        print("Using fallback mode for document retrieval")
        # Load sample documents from docstore.json if available
        try:
            if docstore_data is not None:
                # Try to get documents from the existing docstore
                results = []
                for doc_id, doc in docstore_data['docstore']['_dict'].items():
                    # Apply filter if specified
                    if filters and 'surah' in filters and filters['surah']:
                        surah_filter = filters['surah']
                        doc_metadata = doc.get('metadata', {})
                        if 'surah' in doc_metadata and str(doc_metadata['surah']) != str(surah_filter):
                            continue
                    
                    # Simple keyword matching since we can't use embeddings
                    doc_content = doc.get('page_content', '').lower()
                    if any(keyword in doc_content for keyword in query.lower().split()):
                        results.append({
                            'content': doc.get('page_content', ''),
                            'metadata': doc.get('metadata', {}),
                            'score': 1.0  # Dummy score
                        })
                
                if results:
                    print(f"Found {len(results)} documents using keyword matching")
                    return results[:5]  # Return up to 5 documents
                
                # If no matches, return first document as a fallback
                if docstore_data['docstore']['_dict']:
                    first_doc = list(docstore_data['docstore']['_dict'].values())[0]
                    return [{
                        'content': first_doc.get('page_content', 'No content available'),
                        'metadata': first_doc.get('metadata', {'source': 'fallback', 'reference': 'fallback-1'}),
                        'score': 1.0
                    }]
        except Exception as e:
            print(f"Error in fallback retrieval: {e}")
        
        # If we get here, we need to provide some content
        return [{
            'content': "In the name of Allah, the Entirely Merciful, the Especially Merciful. All praise is due to Allah, Lord of the worlds.",
            'metadata': {
                'source': 'quran',
                'reference': '1:1-2',
                'surah': 1
            },
            'score': 1.0
        }]
    
    # Check if the RAG system is ready
    if not rag_system_ready:
        if DEBUG_MODE:
            print("⚠️ WARNING: RAG system not fully initialized, using limited mode")
            # In debug mode, return dummy data instead of failing
            return [{
                'content': "This is a fallback result because the RAG system is not fully initialized. The system is in debug mode.",
                'metadata': {
                    'source': 'debug',
                    'reference': 'debug-1',
                },
                'score': 1.0
            }]
        else:
            # In production mode, raise an error
            raise HTTPException(
                status_code=503, 
                detail="RAG system not initialized properly. Check API status for details."
            )
    
    # Double-check components
    if embeddings is None:
        print("❌ ERROR: Embeddings model is None")
        raise HTTPException(status_code=500, detail="Embeddings model not initialized")
    
    if index is None:
        print("❌ ERROR: FAISS index is None")
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    if docstore_data is None:
        print("❌ ERROR: Document store is None")
        raise HTTPException(status_code=500, detail="Document store not initialized")
    
    try:
        if DEBUG_MODE:
            print(f"\n------------ Document Retrieval ------------")
            print(f"Query: '{query}'")
            if filters:
                print(f"Filters: {filters}")
        
        # Enhanced query with filters if provided
        enhanced_query = query
        if filters and 'surah' in filters and filters['surah']:
            surah_num = filters['surah']
            enhanced_query = f"information about surah {surah_num} {query}"
            if DEBUG_MODE:
                print(f"Enhanced query: '{enhanced_query}'")
        
        # Embed the query
        print(f"Embedding query: {enhanced_query}")
        try:
            query_vector = embeddings.embed_query(enhanced_query)
            if DEBUG_MODE:
                print(f"Embedding successful, dimension: {len(query_vector)}")
            query_vector = np.array([query_vector]).astype('float32')
        except Exception as e:
            if DEBUG_MODE:
                print(f"❌ ERROR embedding query: {str(e)}")
            raise
        
        # Search the index
        print("Searching vector database...")
        k = 15  # Number of results to retrieve
        if DEBUG_MODE:
            print(f"Searching for top {k} matches...")
        
        try:
            distances, indices = index.search(query_vector, k)
            if DEBUG_MODE:
                print(f"Search completed, raw indices: {indices[0][:5]}...")
        except Exception as e:
            if DEBUG_MODE:
                print(f"❌ ERROR searching index: {str(e)}")
            raise
        
        # Get the documents
        results = []
        valid_count = 0
        filtered_count = 0
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(docstore_data['docstore']['_dict']):
                if DEBUG_MODE and idx >= 0:
                    print(f"Index {idx} out of bounds for docstore with {len(docstore_data['docstore']['_dict'])} items")
                continue
                
            doc_id = str(idx)
            if doc_id in docstore_data['docstore']['_dict']:
                doc_info = docstore_data['docstore']['_dict'][doc_id]
                doc_content = doc_info.get('text', '')
                doc_metadata = doc_info.get('metadata', {})
                
                # Apply additional filters if provided
                include = True
                if filters and 'surah' in filters and filters['surah']:
                    if 'surah_number' in doc_metadata and doc_metadata['surah_number'] != filters['surah']:
                        include = False
                
                if include:
                    results.append({
                        'content': doc_content,
                        'metadata': doc_metadata,
                        'score': float(distances[0][i])
                    })
        
        print(f"Retrieved {len(results)} relevant documents")
        return results
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ ERROR retrieving documents ({elapsed_time:.2f}s): {str(e)}")
        
        if DEBUG_MODE:
            # In debug mode, return dummy data instead of failing
            print("Returning fallback data in debug mode")
            return [{
                'content': f"Error retrieving documents: {str(e)}",
                'metadata': {
                    'source': 'error',
                    'reference': 'error-1',
                },
                'score': 1.0
            }]
        else:
            # In production mode, raise an error
            raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

def prepare_sources(results):
    """Format the search results for the response"""
    if not results:
        return []
    
    sources = []
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
        
        # Add to sources list
        sources.append({
            "source_type": source,
            "reference": ref,
            "content": content
        })
    
    return sources

def format_context_for_llm(results):
    """Format the search results into a context string for the LLM"""
    if not results:
        return "No relevant information found."
    
    context_parts = []
    
    for doc in results:
        content = doc['content']
        metadata = doc['metadata']
        
        source = metadata.get('source', 'unknown')
        ref = metadata.get('reference', '')
        
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

@app.post("/api/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Get an answer to a question about the Quran
    """
    overall_start_time = time.time() # Start timing the whole request
    if DEBUG_MODE:
        print(f"\n----- Processing question: '{request.question}' -----")

    # Ensure RAG system is ready before proceeding (unless in fallback)
    if not rag_system_ready and not FALLBACK_MODE:
         # Check if initialization failed during startup
        if initialization_error:
             error_detail = f"RAG system initialization failed: {initialization_error}. Cannot process RAG queries."
             if DEBUG_MODE: print(f"ERROR: {error_detail}")
             raise HTTPException(status_code=503, detail=error_detail)
        else:
            # This case might occur if startup hasn't finished, but it's unlikely
             error_detail = "RAG system is not ready yet. Please try again shortly."
             if DEBUG_MODE: print(f"WARNING: {error_detail}")
             raise HTTPException(status_code=503, detail=error_detail)

    try:
        # Create filters dictionary
        filters = {}
        if request.surah_filter:
            filters["surah"] = request.surah_filter
        if request.verse_filter:
            filters["verse"] = request.verse_filter

        if DEBUG_MODE:
            print(f"Retrieving documents with filters: {filters}")

        # --- Time the retrieval step ---
        retrieval_start_time = time.time()
        try:
            results = retrieve_documents(request.question, filters)
            retrieval_duration = time.time() - retrieval_start_time
            if DEBUG_MODE:
                print(f"⏱️ Document retrieval took {retrieval_duration:.2f} seconds.")
        except HTTPException as http_exc:
             # Propagate HTTP exceptions (like 503 if RAG not ready and not in FALLBACK_MODE)
             raise http_exc
        except Exception as retrieval_error:
            retrieval_duration = time.time() - retrieval_start_time
            error_detail = f"Error retrieving documents: {str(retrieval_error)} (took {retrieval_duration:.2f}s)"
            if DEBUG_MODE:
                print(f"ERROR: {error_detail}")
            # Return a 500 error if retrieval fails fundamentally
            raise HTTPException(status_code=500, detail=error_detail)

        if not results:
            if DEBUG_MODE:
                print("No relevant documents found")
            # If no documents, inform the user, don't proceed to LLM
            overall_duration = time.time() - overall_start_time
            if DEBUG_MODE: print(f"⏱️ Request finished (no results) in {overall_duration:.2f} seconds.")
            return AnswerResponse(
                answer="I couldn't find specific information relevant to your question in the available documents. You could try rephrasing.",
                sources=[],
                filters_applied=filters
            )

        # Format context for the LLM
        if DEBUG_MODE:
            print(f"Formatting {len(results)} documents for LLM")
        context = format_context_for_llm(results)

        # Prepare sources for the response
        sources = prepare_sources(results)

        if DEBUG_MODE:
            print("Generating answer using RAG context...")

        # Verify API key is essential for the generator step
        api_key = load_api_key()
        if not api_key:
            error_detail = "OpenAI API key not found. Cannot generate answer."
            if DEBUG_MODE:
                print(f"ERROR: {error_detail}")
            # Return error response, don't raise HTTPException here as sources were found
            return AnswerResponse(
                answer=f"Error: {error_detail} Please set your API key.",
                sources=[SourceItem(**s) for s in sources], # Include sources found so far
                filters_applied=filters
            )

        # Use generate_answer from src/generator.py correctly with context
        # --- Time the LLM generation step ---
        generation_start_time = time.time()
        try:
            # Create an answer generator instance
            generator = create_answer_generator()
            
            # Try direct_openai approach first (more reliable)
            answer = None
            try:
                from src.direct_openai import generate_answer_with_openai
                print("API using direct OpenAI implementation first")
                direct_answer = generate_answer_with_openai(context, request.question)
                if direct_answer and isinstance(direct_answer, str):
                    answer = direct_answer
                    print("API successfully used direct OpenAI implementation")
            except Exception as direct_error:
                print(f"API direct OpenAI implementation failed: {str(direct_error)}")
                
            # If direct approach failed, fall back to LangChain
            if not answer:
                try:
                    # Call generate_answer with all required parameters
                    print("API falling back to LangChain implementation")
                    langchain_answer = generate_answer(generator, context, request.question)
                    
                    # Ensure answer is a string
                    if isinstance(langchain_answer, dict):
                        # If answer is a dict, extract the content or convert to string
                        answer = str(langchain_answer.get('content', str(langchain_answer)))
                    elif hasattr(langchain_answer, 'content'):
                        # If it has content attribute, use that
                        answer = langchain_answer.content
                    elif isinstance(langchain_answer, list) and langchain_answer and hasattr(langchain_answer[0], 'content'):
                        # If it's a list of message-like objects
                        answer = langchain_answer[0].content
                    elif not isinstance(langchain_answer, str):
                        # Convert any non-string answer to string
                        answer = str(langchain_answer)
                    else:
                        answer = langchain_answer
                except Exception as langchain_error:
                    raise Exception(f"Both OpenAI direct and LangChain approaches failed: {str(langchain_error)}")
                
            generation_duration = time.time() - generation_start_time
            if DEBUG_MODE:
                print(f"⏱️ LLM answer generation took {generation_duration:.2f} seconds.")

        except Exception as gen_error:
            generation_duration = time.time() - generation_start_time
            error_detail = f"Error generating answer with LLM: {str(gen_error)} (attempt took {generation_duration:.2f}s)"
            if DEBUG_MODE:
                print(f"ERROR: {error_detail}")
            # Return error response, including sources found
            # Don't fall back to another internal API call here
            overall_duration = time.time() - overall_start_time
            if DEBUG_MODE: print(f"⏱️ Request finished (generation error) in {overall_duration:.2f} seconds.")
            return AnswerResponse(
                answer=f"Error: {error_detail}",
                sources=[SourceItem(**s) for s in sources],
                filters_applied=filters
            )

        # Convert source dict to SourceItem model
        source_items = [SourceItem(**s) for s in sources]

        overall_duration = time.time() - overall_start_time
        if DEBUG_MODE:
            print(f"✅ Successfully processed question in {overall_duration:.2f} seconds.")

        return AnswerResponse(
            answer=answer,
            sources=source_items,
            filters_applied=filters
        )

    except HTTPException as http_exc:
         # Re-raise specific HTTP exceptions from retrieval
         overall_duration = time.time() - overall_start_time
         if DEBUG_MODE: print(f"⏱️ Request finished (HTTPException) in {overall_duration:.2f} seconds.")
         raise http_exc
    except Exception as e:
        # Catch any other unexpected errors during processing
        overall_duration = time.time() - overall_start_time
        error_detail = f"Unexpected error processing query: {str(e)}"
        if DEBUG_MODE:
            import traceback
            print(f"CRITICAL ERROR: {error_detail} (request took {overall_duration:.2f}s)")
            traceback.print_exc() # Print full stack trace in debug mode
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/api/ask")
async def ask_question_get(
    question: str = Query(..., description="Your question about the Quran"),
    surah: Optional[int] = Query(None, description="Optional surah number filter"),
    verse: Optional[int] = Query(None, description="Optional verse number filter")
):
    """
    Get an answer to a question about the Quran (GET endpoint)
    """
    # Use the same implementation as the POST endpoint
    request = QuestionRequest(
        question=question,
        surah_filter=surah,
        verse_filter=verse
    )
    return await ask_question(request)

@app.get("/")
async def root():
    """Get API status and initialization information"""
    status = "running"
    details = {}
    
    # Check OpenAI API key
    api_key = load_api_key()
    details["openai_api_key"] = "available" if api_key else "missing"
    
    # Check RAG components
    details["embeddings"] = "initialized" if embeddings is not None else "failed"
    details["vector_db"] = "initialized" if index is not None else "failed"
    details["document_store"] = "initialized" if docstore_data is not None else "failed"
    details["rag_system"] = "ready" if rag_system_ready else "limited"
    details["fallback_mode"] = "enabled" if FALLBACK_MODE else "disabled"
    
    if initialization_error:
        details["initialization_error"] = initialization_error
    
    return {
        "message": "Welcome to the Quran Knowledge Explorer API",
        "endpoints": [
            {
                "path": "/api/ask",
                "methods": ["POST", "GET"],
                "description": "Get an answer to a question about the Quran"
            },
            {
                "path": "/docs",
                "methods": ["GET"],
                "description": "OpenAPI documentation"
            }
        ],
        "status": status,
        "details": details,
        "debug_mode": DEBUG_MODE
    }

# Run the API with uvicorn when this file is executed directly
if __name__ == "__main__":
    import uvicorn
    print("Starting Quran Knowledge Explorer API...")
    print("Access the API documentation at http://localhost:8000/docs")
    print("Try querying with: curl http://localhost:8000/api/ask?question=What+does+the+Quran+say+about+kindness+to+parents")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
