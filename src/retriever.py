# src/retriever.py
import os
from typing import List, Dict, Any
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

# Direct OpenAI client implementation to avoid LangChain's proxies issue
import openai
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import LLMResult
from typing import Dict, List, Optional, Any, Mapping, Sequence
from langchain_core.messages import BaseMessage
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

class DirectOpenAIChat(BaseChatModel):
    """Direct implementation using OpenAI client instead of langchain_openai."""
    
    model_name: str = "gpt-3.5-turbo"  # Default model name
    temperature: float = 0  # Default temperature
    openai_api_key: Optional[str] = None
    
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0, **kwargs):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.temperature = temperature
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        # Remove any proxies from environment to avoid the error
        openai_kwargs = {"api_key": self.openai_api_key}
        # Filter out problematic kwargs
        filtered_kwargs = {k: v for k, v in kwargs.items() 
                           if k not in ["proxies", "http_client"]}
        openai_kwargs.update(filtered_kwargs)
        self.client = openai.OpenAI(**openai_kwargs)
    
    def _convert_messages_to_openai_format(self, messages: List[BaseMessage]) -> List[Dict]:
        """Convert LangChain messages to OpenAI format."""
        message_dicts = []
        for message in messages:
            if isinstance(message, HumanMessage):
                message_dicts.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                message_dicts.append({"role": "assistant", "content": message.content})
            elif isinstance(message, SystemMessage):
                message_dicts.append({"role": "system", "content": message.content})
            else:
                # Default to user role for any other type
                message_dicts.append({"role": "user", "content": str(message.content)})
        return message_dicts
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate using OpenAI client directly."""
        message_dicts = self._convert_messages_to_openai_format(messages)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=message_dicts,
                temperature=self.temperature,
                stream=False
            )
            
            # Process the response into LangChain format
            ai_message = AIMessage(content=response.choices[0].message.content)
            return LLMResult(generations=[[ai_message]])
        except Exception as e:
            # Print helpful error info
            print(f"Error in DirectOpenAIChat: {e}")
            # Return empty response
            return LLMResult(generations=[[AIMessage(content="I encountered an error processing your request.")]])
            
    def _llm_type(self) -> str:
        """Return the type of llm."""
        return "direct_openai_chat"
        
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model_name": self.model_name, "temperature": self.temperature}

def create_basic_retriever(vector_store, k=5):
    """
    Create a simple retriever from a vector store
    """
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

def create_enhanced_retriever(vector_store, k=5, use_compression=True):
    """
    Create an advanced retriever with optional contextual compression
    """
    base_retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": k,
            "score_threshold": 0.5,  # Lower threshold to retrieve more results
        }
    )
    
    if not use_compression:
        return base_retriever
        
    # Add contextual compression for more focused results
    try:
        # Try standard OpenAI first
        from langchain_openai import ChatOpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Skip compression if no API key
        if not openai_api_key:
            print("No OpenAI API key found, skipping compression.")
            return base_retriever
            
        try:
            print("Trying to create compression with standard ChatOpenAI")
            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo", 
                temperature=0,
                openai_api_key=openai_api_key,
                api_kwargs={"timeout": 30}  # Add timeout instead of proxies
            )
            compressor = LLMChainExtractor.from_llm(llm)
            print("Successfully created LLM compressor with ChatOpenAI")
        except Exception as e1:
            print(f"Error creating standard ChatOpenAI compressor: {e1}")
            
            # Try our custom implementation
            try:
                print("Trying direct OpenAI implementation")
                llm = DirectOpenAIChat(temperature=0)
                compressor = LLMChainExtractor.from_llm(llm)
                print("Successfully created LLM compressor with DirectOpenAIChat")
            except Exception as e2:
                print(f"Error creating DirectOpenAIChat compressor: {e2}")
                return base_retriever
        
        # Create the compression retriever
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
        
        return compression_retriever
    except Exception as e:
        print(f"Warning: Could not create LLM compressor: {e}")
        return base_retriever  # Fall back to base retriever if compression fails

def retrieve_relevant_context(retriever, query: str, filter_criteria: Dict = None):
    """
    Retrieve relevant documents for a query with optional filtering
    """
    search_kwargs = {}
    if filter_criteria:
        search_kwargs["filter"] = filter_criteria
    
    # Handle different retriever types
    if hasattr(retriever, 'search_kwargs'):
        original_kwargs = retriever.search_kwargs.copy()
        if filter_criteria:
            retriever.search_kwargs.update(search_kwargs)
    
    documents = retriever.get_relevant_documents(query)
    
    # Reset search_kwargs if modified
    if hasattr(retriever, 'search_kwargs') and filter_criteria:
        retriever.search_kwargs = original_kwargs
    
    return documents

def format_context_from_docs(documents: List[Any]) -> str:
    """
    Format retrieved documents into a context string
    """
    context_parts = []
    
    for doc in documents:
        source = doc.metadata.get("source", "unknown")
        ref = doc.metadata.get("reference", "")
        
        # Format differently based on source
        if source == "quran":
            context_parts.append(f"[Quran {ref}]: {doc.page_content}")
        elif source.startswith("tafsir_"):
            tafsir_name = source.replace("tafsir_", "")
            context_parts.append(f"[Tafsir {tafsir_name} on {ref}]: {doc.page_content}")
    
    return "\n\n".join(context_parts)