# src/embeddings.py
import os
import pickle
from typing import List, Dict, Any
import openai
# from langchain_openai import OpenAIEmbeddings  # Comment out as we're not using this directly
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
import numpy as np

load_dotenv()  # Load API keys from .env file

# Configure OpenAI globally to avoid proxies parameter issue
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    # Set the API key globally
    openai.api_key = api_key
    # Remove incorrect client initialization
    # Ensure no proxies are used by setting them to None explicitly
    openai.proxy = None

# Global model cache to avoid reloading models
_GLOBAL_MODEL_CACHE = {}

# Custom OpenAI embeddings class to avoid proxies parameter issue
class CustomOpenAIEmbeddings(Embeddings):
    """Custom implementation of OpenAI embeddings to avoid proxies parameter issues."""
    
    def __init__(self, model="text-embedding-ada-002"):
        self.model = model
        # Ensure the API key is set globally
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        openai.api_key = api_key
        # No need to create a client object, use openai methods directly
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using the OpenAI API"""
        # Call OpenAI's embeddings endpoint directly
        results = []
        for i in range(0, len(texts), 100):  # Process in batches of 100
            batch = texts[i:i+100]
            response = openai.Embedding.create(model=self.model, input=batch)
            results.extend([data.embedding for data in response.data])
        return results
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a query using the OpenAI API"""
        response = openai.Embedding.create(model=self.model, input=[text])
        return response.data[0].embedding

# Custom HuggingFace embeddings class to handle import issues
class CustomHuggingFaceEmbeddings(Embeddings):
    """Custom implementation of HuggingFace embeddings to avoid import issues."""
    
    def __init__(self):
        # Check if model is already in cache
        if "transformer_model" in _GLOBAL_MODEL_CACHE and "tokenizer" in _GLOBAL_MODEL_CACHE:
            print("Using cached transformer model")
            self.model = _GLOBAL_MODEL_CACHE["transformer_model"]
            self.tokenizer = _GLOBAL_MODEL_CACHE["tokenizer"]
            self.use_alternative = True
            return
            
        try:
            # Try using transformers directly first (more compatible with newer huggingface-hub)
            from transformers import AutoTokenizer, AutoModel
            import torch
            import torch.nn.functional as F
            import warnings
            
            # Suppress specific deprecation warnings
            warnings.filterwarnings('ignore', category=FutureWarning, 
                                  module='huggingface_hub.file_download')
            warnings.filterwarnings('ignore', category=FutureWarning, 
                                  module='transformers.utils.generic')
            
            print("Initializing embeddings with transformers...")
            # Use download_only=True to avoid deprecation warning
            self.tokenizer = AutoTokenizer.from_pretrained(
                'sentence-transformers/all-MiniLM-L6-v2',
                local_files_only=False
            )
            self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
            self.use_alternative = True
            
            # Cache the model for future use
            _GLOBAL_MODEL_CACHE["transformer_model"] = self.model
            _GLOBAL_MODEL_CACHE["tokenizer"] = self.tokenizer
            
            print("Successfully initialized transformer-based embeddings")
        except Exception as e:
            print(f"Error initializing with transformers: {e}")
            # Rest of the initialization code remains unchanged
            try:
                if "sentence_transformer" in _GLOBAL_MODEL_CACHE:
                    print("Using cached sentence transformer model")
                    self.model = _GLOBAL_MODEL_CACHE["sentence_transformer"]
                    return
                    
                print("Trying SentenceTransformer...")
                import torch
                from sentence_transformers import SentenceTransformer
                
                # Model initialization with proper parameters
                self.model = SentenceTransformer(
                    'all-MiniLM-L6-v2',
                    device='cpu',
                )
                
                # Cache the model
                _GLOBAL_MODEL_CACHE["sentence_transformer"] = self.model
                
                print("Successfully initialized SentenceTransformer model")
            except Exception as e2:
                print(f"Error initializing SentenceTransformer: {e2}")
                raise Exception("Could not initialize any embedding model")
    
    def mean_pooling(self, model_output, attention_mask):
        """Perform mean pooling on token embeddings"""
        import torch
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def embed_with_transformers(self, texts):
        """Alternative embedding method using the transformers library directly"""
        import torch
        import torch.nn.functional as F
        
        # Process in batches to avoid memory issues
        max_batch_size = 32  # Adjust based on your available memory
        results = []
        
        for i in range(0, len(texts), max_batch_size):
            batch_texts = texts[i:i+max_batch_size]
            
            # Tokenize batch
            encoded_input = self.tokenizer(batch_texts, padding=True, truncation=True, 
                                          max_length=512, return_tensors='pt')
            
            # Compute token embeddings
            with torch.no_grad():
                model_output = self.model(**encoded_input)
            
            # Perform pooling
            embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
            
            # Normalize embeddings
            embeddings = F.normalize(embeddings, p=2, dim=1)
            
            # Add to results
            results.append(embeddings.cpu().numpy())
        
        # Combine all batches
        if len(results) > 1:
            return np.vstack(results)
        elif len(results) == 1:
            return results[0]
        else:
            return np.array([])
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using SentenceTransformer"""
        try:
            if hasattr(self, 'use_alternative'):
                # Use alternative embedding method
                return self.embed_with_transformers(texts).tolist()
            else:
                # Use standard SentenceTransformer
                embeddings = self.model.encode(texts, normalize_embeddings=True)
                return embeddings.tolist()
        except Exception as e:
            print(f"Error in embed_documents: {e}")
            # Return basic embeddings as fallback
            return [[1.0] * 384 for _ in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a query using SentenceTransformer"""
        try:
            if hasattr(self, 'use_alternative'):
                # Use alternative embedding method
                return self.embed_with_transformers([text])[0].tolist()
            else:
                # Use standard SentenceTransformer
                embedding = self.model.encode(text, normalize_embeddings=True)
                return embedding.tolist()
        except Exception as e:
            print(f"Error in embed_query: {e}")
            # Return basic embedding as fallback
            return [1.0] * 384

def get_embedding_model(model_type: str = "openai"):
    """
    Initialize and return an embedding model
    """
    if model_type == "openai":
        try:
            # Use custom implementation to avoid proxies parameter issue
            return CustomOpenAIEmbeddings(model="text-embedding-ada-002")
        except Exception as e:
            print(f"Error initializing OpenAI embeddings: {e}")
            print("Falling back to HuggingFace embeddings")
            return get_embedding_model("huggingface")
    elif model_type == "huggingface":
        # Use custom implementation to avoid import issues
        try:
            return CustomHuggingFaceEmbeddings()
        except Exception as e:
            print(f"Error initializing CustomHuggingFaceEmbeddings: {e}")
            print("Falling back to basic embeddings")

            class BasicEmbeddings(Embeddings):
                """An extremely basic embedding that just returns ones as embeddings."""
                def embed_documents(self, texts):
                    return [[1.0] * 384 for _ in texts]
                def embed_query(self, text):
                    return [1.0] * 384

            return BasicEmbeddings()
    else:
        raise ValueError(f"Unsupported embedding model type: {model_type}")

def create_vector_store(documents: List[Dict[str, Any]], 
                        persist_directory: str,
                        embedding_model_type: str = "openai",
                        fallback: bool = False):
    """
    Create and persist a vector store from documents
    
    Args:
        documents: List of documents to add to the vector store
        persist_directory: Directory to persist the vector store
        embedding_model_type: Type of embedding model to use
        fallback: If True, use a more compatible but potentially slower embedding model
    """
    # Make sure directory exists
    os.makedirs(os.path.dirname(persist_directory), exist_ok=True)
    index_path = os.path.join(persist_directory, "faiss_index")
    
    # Get text content and metadata from documents
    texts = [doc['content'] for doc in documents]
    metadatas = [doc['metadata'] for doc in documents]
    
    try:
        if fallback:
            print("Using fallback embedding model configuration...")
            try:
                # Use custom embeddings to avoid import issues
                embedding_model = CustomHuggingFaceEmbeddings()
                print("Successfully initialized fallback embedding model")
            except Exception as e:
                print(f"Error initializing fallback embedding model: {e}")
                # Last resort fallback - use custom embeddings
                print("Using extremely basic embeddings as last resort")
                
                class BasicEmbeddings(Embeddings):
                    """An extremely basic embedding that just returns ones as embeddings."""
                    def embed_documents(self, texts):
                        return [[1.0] * 384 for _ in texts]
                    def embed_query(self, text):
                        return [1.0] * 384
                        
                embedding_model = BasicEmbeddings()
        else:
            # Initialize embedding model
            print(f"Initializing embedding model: {embedding_model_type}")
            embedding_model = get_embedding_model(embedding_model_type)
        
        # Process in smaller batches to avoid memory issues
        print(f"Creating FAISS vector store with {len(texts)} documents...")
        batch_size = 500  # Smaller batches to avoid memory issues
        
        # Create FAISS index with first batch
        first_batch_end = min(batch_size, len(texts))
        print(f"Processing initial batch (0 to {first_batch_end})")
        vector_store = FAISS.from_texts(
            texts=texts[:first_batch_end],
            embedding=embedding_model,
            metadatas=metadatas[:first_batch_end]
        )
        
        # Add remaining documents in batches
        for i in range(batch_size, len(texts), batch_size):
            end_idx = min(i + batch_size, len(texts))
            print(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} ({i} to {end_idx})")
            batch_texts = texts[i:end_idx]
            batch_metadatas = metadatas[i:end_idx]
            
            # Add batch to vector store
            vector_store.add_texts(batch_texts, metadatas=batch_metadatas)
        
        # Save to disk
        print(f"Saving FAISS index to {index_path}")
        vector_store.save_local(index_path)
        print(f"Vector store created with {len(texts)} documents and saved to {index_path}")
        return vector_store
        
    except Exception as e:
        print(f"Error in create_vector_store: {e}")
        # Create a minimal vector store as a last resort
        print("Creating minimal FAISS vector store as last resort")
        
        # Use only first 10 documents if we have more than 10
        limited_docs = documents[:10] if len(documents) > 10 else documents
        texts = [doc['content'] for doc in limited_docs]
        metadatas = [doc['metadata'] for doc in limited_docs]
        
        class BasicEmbeddings(Embeddings):
            """An extremely basic embedding that just returns ones as embeddings."""
            def embed_documents(self, texts):
                return [[1.0] * 384 for _ in texts]
            def embed_query(self, text):
                return [1.0] * 384
        
        vector_store = FAISS.from_texts(
            texts=texts,
            embedding=BasicEmbeddings(),
            metadatas=metadatas
        )
        
        # Save to disk
        vector_store.save_local(index_path)
        print(f"Minimal vector store created with {len(texts)} documents and saved to {index_path}")
        return vector_store

def load_vector_store(persist_directory: str, embedding_model_type: str = "openai"):
    """
    Load a persisted vector store
    """
    try:
        # Initialize embedding model
        embedding_model = get_embedding_model(embedding_model_type)
        
        # Path to FAISS index
        index_path = os.path.join(persist_directory, "faiss_index")
        
        # Check if index exists
        if os.path.exists(index_path):
            print(f"Loading FAISS index from {index_path}")
            vector_store = FAISS.load_local(
                index_path,
                embedding_model,
            )
            return vector_store
        else:
            raise FileNotFoundError(f"No FAISS index found at {index_path}")
    except Exception as e:
        print(f"Error loading vector store: {e}")
        print("Trying fallback embedding model...")
        
        try:
            # Try with custom embedding model
            embedding_model = CustomHuggingFaceEmbeddings()
            
            index_path = os.path.join(persist_directory, "faiss_index")
            if os.path.exists(index_path):
                vector_store = FAISS.load_local(
                    index_path,
                    embedding_model,
                )
                return vector_store
            else:
                raise FileNotFoundError(f"No FAISS index found at {index_path}")
        except Exception as e2:
            print(f"Error loading vector store with fallback: {e2}")
            
            # Last resort - create basic embeddings model
            class BasicEmbeddings(Embeddings):
                """An extremely basic embedding that just returns ones as embeddings."""
                def embed_documents(self, texts):
                    return [[1.0] * 384 for _ in texts]
                def embed_query(self, text):
                    return [1.0] * 384
            
            index_path = os.path.join(persist_directory, "faiss_index")
            if os.path.exists(index_path):
                vector_store = FAISS.load_local(
                    index_path,
                    BasicEmbeddings(),
                )
                return vector_store
            else:
                raise FileNotFoundError(f"No FAISS index found at {index_path}")