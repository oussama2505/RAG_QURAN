"""
LLM client module to ensure consistent API access across the application.
"""
import os
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import LLMResult, Generation
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
            api_key = load_api_key()
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not available")
            
            try:
                # Initialize without proxies
                cls._client = openai.OpenAI(api_key=api_key)
            except (AttributeError, TypeError):
                openai.api_key = api_key
                cls._client = openai
        return cls._instance
    
    @property
    def client(self):
        return self._client

    def is_legacy_client(self):
        return not hasattr(self._client, 'chat')

class UnifiedLLMChat(BaseChatModel):
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0
    max_tokens: int = 1000
    openai_api_key: Optional[str] = None
    openai_client: Optional[OpenAIClient] = None
    
    def __init__(
        self, 
        model_name: str = "gpt-3.5-turbo", 
        temperature: float = 0, 
        max_tokens: int = 1000,
        **kwargs
    ):
        """Initialize the UnifiedLLMChat with model parameters."""
        try:
            # Remove proxies from kwargs if present
            kwargs.pop('proxies', None)
            kwargs.pop('http_client', None)
            
            super().__init__(**kwargs)
            self.model_name = model_name
            self.temperature = temperature
            self.max_tokens = max_tokens
            self.openai_api_key = load_api_key()
            
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not found or invalid")
            
            self.openai_client = OpenAIClient()
            if not self.openai_client or not self.openai_client.client:
                raise ValueError("Failed to initialize OpenAI client")
            print(f"Successfully initialized UnifiedLLMChat with model {model_name}")
                
        except Exception as e:
            print(f"Error in UnifiedLLMChat initialization: {str(e)}")
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
                message_dicts.append({"role": "user", "content": str(message.content)})
        return message_dicts
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate using OpenAI client with proper response formatting."""
        try:
            if not self.openai_client:
                raise ValueError("OpenAI client not initialized")

            # Convert LangChain messages to OpenAI format
            message_dicts = self._convert_messages_to_openai_format(messages)

            # Call the OpenAI API
            response = self.openai_client.client.chat.completions.create(
                model=self.model_name,
                messages=message_dicts,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=stop,
                stream=False
            )

            # Log the raw response for debugging
            print("Raw OpenAI response:", response)

            # Extract content from the response
            if hasattr(response, 'choices') and response.choices:
                # Extract the first choice's message content
                content = response.choices[0].message.content
            else:
                # Fallback to string representation if choices are missing
                content = str(response)

            # Create a proper Generation object for LangChain
            generation = Generation(
                text=content,
                generation_info={"finish_reason": response.choices[0].finish_reason if response.choices else "unknown"}
            )
            return LLMResult(generations=[[generation]])

        except Exception as e:
            error_msg = f"Error in UnifiedLLMChat._generate: {str(e)}"
            print(error_msg)
            # Return error in proper LangChain format
            generation = Generation(
                text=f"I encountered an error: {str(e)}",
                generation_info={"finish_reason": "error"}
            )
            return LLMResult(generations=[[generation]])
    
    def _llm_type(self) -> str:
        return "unified_openai_chat"
        
    @property
    def _identifying_params(self) -> Dict[str, Any]:
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
