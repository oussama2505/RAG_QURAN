import os
from src import config
from src.data_processing import load_quran_data, load_tafsir_data, create_document_chunks
from src.embeddings import create_vector_store, load_vector_store, get_embedding_model
from src.retriever import create_enhanced_retriever
from src.generator import create_answer_generator, process_query

def initialize_data_and_models(rebuild_vector_db=False, sample_size=None):
    """
    Initialize the RAG components
    
    Args:
        rebuild_vector_db (bool): Whether to rebuild the vector DB
        sample_size (int, optional): If set, only use a sample of documents for testing
    """
    # Create directories if they don't exist
    os.makedirs(config.VECTOR_DB_PATH, exist_ok=True)
    
    # Check if vector database exists and whether to rebuild
    index_path = os.path.join(config.VECTOR_DB_PATH, "faiss_index")
    vector_db_exists = os.path.exists(index_path) and os.path.isdir(index_path)
    
    try:
        if not vector_db_exists or rebuild_vector_db:
            print("Building vector database...")
            
            # Load and process data
            print("Loading Quran data...")
            quran_docs = load_quran_data(config.QURAN_DATA_PATH)
            print(f"Loaded {len(quran_docs)} Quran documents")
            
            print("Loading Tafsir data...")
            tafsir_docs = load_tafsir_data(config.TAFSIR_DIR_PATH)
            print(f"Loaded {len(tafsir_docs)} Tafsir documents")
            
            # Combine documents
            all_docs = quran_docs + tafsir_docs
            print(f"Total documents: {len(all_docs)}")
            
            # For testing purposes, optionally use only a sample of documents
            if sample_size and sample_size < len(all_docs):
                print(f"Using sample of {sample_size} documents for testing...")
                import random
                random.seed(42)  # For reproducibility
                all_docs = random.sample(all_docs, sample_size)
            
            # Create document chunks
            print("Creating document chunks...")
            chunked_docs = create_document_chunks(all_docs, config.CHUNK_SIZE)
            print(f"Created {len(chunked_docs)} document chunks")
            
            # Create vector store
            print("Creating vector store with HuggingFace embeddings...")
            vector_store = create_vector_store(
                chunked_docs, 
                config.VECTOR_DB_PATH,
                "huggingface"
            )
        else:
            print("Loading existing vector database...")
            vector_store = load_vector_store(
                config.VECTOR_DB_PATH,
                "huggingface"
            )
    except Exception as e:
        print(f"Error initializing vector store with HuggingFace embeddings: {e}")
        print("Attempting fallback to minimal test case...")
        
        # Create a minimal test set
        print("Loading a small subset of data for testing...")
        quran_docs = load_quran_data(config.QURAN_DATA_PATH)[:10]  # Just first 10 verses
        print(f"Using {len(quran_docs)} Quran documents")
        
        # Create document chunks
        print("Creating document chunks...")
        chunked_docs = create_document_chunks(quran_docs, config.CHUNK_SIZE)
        print(f"Created {len(chunked_docs)} document chunks")
        
        # Use a fallback embedding method (might be slower but more compatible)
        print("Creating vector store with fallback minimal configuration...")
        vector_store = create_vector_store(
            chunked_docs,
            config.VECTOR_DB_PATH,
            "huggingface",
            fallback=True
        )
    
    # Create retriever
    retriever = create_enhanced_retriever(vector_store, k=5)
    
    # Create generator
    generator = create_answer_generator(
        model_name=config.LLM_MODEL_NAME,
        temperature=0
    )
    
    return retriever, generator

def quran_rag_query(question, surah_filter=None, verse_filter=None):
    """
    Query the Quran RAG system
    """
    try:
        # Initialize components
        retriever, generator = initialize_data_and_models()
        
        # Prepare filters
        filters = {}
        if surah_filter:
            filters["surah_num"] = surah_filter
        if verse_filter:
            filters["verse_num"] = verse_filter
        
        # Process query
        answer = process_query(retriever, generator, question, filters)
        
        # If answer is empty or just says no info found, try without filters
        if ("couldn't find any relevant information" in answer.lower() or not answer.strip()) and (surah_filter or verse_filter):
            print("No results with filters, trying without filters...")
            answer = process_query(retriever, generator, question, None)
        
        return answer
    except Exception as e:
        error_msg = f"Error in quran_rag_query: {str(e)}"
        print(error_msg)
        return "I encountered an error processing your query. Please check the system logs or try again later."

if __name__ == "__main__":
    # Example usage
    question = "What does the Quran say about patience?"
    answer = quran_rag_query(question)
    print(f"Question: {question}")
    print(f"Answer: {answer}")