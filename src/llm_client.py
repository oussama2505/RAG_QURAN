"""
LLM client module to ensure consistent API access across the application.
This centralizes OpenAI API interactions and provides fallback mechanisms.
"""
import os
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import LLMResult
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from src.api_key_manager import load_api_key

load_dotenv()

class OpenAIClient:
    """Singleton class to manage OpenAI API client instances"""
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
            # Use the API key manager to get the key
            api_key = load_api_key()
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not available. Please set it in your .env file or environment variables.")
            cls._client = openai.OpenAI(api_key=api_key)
        return cls._instance
    
    @property
    def client(self):
        """Get the OpenAI client instance"""
        return self._client

class UnifiedLLMChat(BaseChatModel):
    """
    Unified LLM Chat interface that works reliably with OpenAI's API.
    Implements both the LangChain interface and direct API calls.
    """
    
    # These need to be class variables for LangChain validation
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0
    max_tokens: int = 1000
    openai_api_key: Optional[str] = None
    
    def __init__(
        self, 
        model_name: str = "gpt-3.5-turbo", 
        temperature: float = 0, 
        max_tokens: int = 1000,
        **kwargs
    ):
        """Initialize the UnifiedLLMChat with model parameters."""
        # Filter out problematic kwargs
        filtered_kwargs = {k: v for k, v in kwargs.items() 
                        if k not in ["proxies", "http_client"]}
        
        super().__init__(**filtered_kwargs)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.openai_api_key = load_api_key()
        
        # Get OpenAI client
        try:
            self.client = OpenAIClient().client
            print(f"Successfully initialized UnifiedLLMChat with model {model_name}")
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            raise
    
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
        """Generate using OpenAI client directly with improved error handling."""
        message_dicts = self._convert_messages_to_openai_format(messages)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=message_dicts,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=stop,
                stream=False
            )
            
            # Process the response into LangChain format
            ai_message = AIMessage(content=response.choices[0].message.content)
            return LLMResult(generations=[[ai_message]])
        except Exception as e:
            # Print helpful error info
            print(f"Error in UnifiedLLMChat: {e}")
            # Return error response
            return LLMResult(generations=[[AIMessage(content=f"I encountered an error: {str(e)}")]])
            
    def _llm_type(self) -> str:
        """Return the type of LLM."""
        return "unified_openai_chat"
        
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

def get_chat_model(
    model_name: str = "gpt-3.5-turbo", 
    temperature: float = 0,
    max_tokens: int = 1000
) -> BaseChatModel:
    """
    Get a chat model instance ready to use with proper error handling
    
    Args:
        model_name: The OpenAI model to use (default: gpt-3.5-turbo)
        temperature: Sampling temperature (default: 0)
        max_tokens: Maximum tokens to generate (default: 1000)
        
    Returns:
        An instance of BaseChatModel
    """
    try:
        # Initialize our unified client
        return UnifiedLLMChat(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    except Exception as e:
        # If UnifiedLLMChat fails, raise the error directly
        print(f"❌ CRITICAL ERROR creating UnifiedLLMChat: {e}")
        # Optionally, return a dummy model or re-raise
        # Re-raising might be better to halt startup if LLM is crucial
        # raise e # Uncomment this to halt on error
        
        # Return dummy chat model that returns error message
        from langchain.llms.fake import FakeListLLM
        error_message = f"Sorry, failed to initialize the language model ({type(e).__name__}). Please check configuration and API keys."
        print(f"Returning FakeListLLM due to error: {error_message}")
        return FakeListLLM(responses=[error_message])
