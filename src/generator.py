# src/generator.py
import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema import Document
from langchain_core.language_models.chat_models import BaseChatModel
from dotenv import load_dotenv
from src.retriever import retrieve_relevant_context, format_context_from_docs

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

def create_quran_rag_prompt():
    """
    Create a prompt template for Quran RAG
    """
    system_template = """You are a knowledgeable Quran scholar assistant. Your task is to provide accurate, respectful, and helpful information about the Quran based on the context provided. Consider different interpretations where relevant, but avoid making claims without textual support.

Context information is below:
-----------------
{context}
-----------------

Given this context, provide a thoughtful response to the user's question. If the context doesn't contain sufficient information to answer fully, acknowledge the limitations while providing what you can based on the available information.
"""
    
    human_template = "{question}"
    
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    return ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

def create_answer_generator(model_name="gpt-3.5-turbo", temperature=0):
    """
    Create an LLM chain for generating answers
    """
    # Set API key explicitly
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_api_key:
        print("WARNING: No OpenAI API key found. Set the OPENAI_API_KEY environment variable.")
    
    try:
        # Try using the standard OpenAI integration first
        from langchain_openai import ChatOpenAI
        
        print(f"Attempting to use standard ChatOpenAI with model {model_name}")
        # Create with minimal options to avoid errors
        llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=openai_api_key,
            api_kwargs={"timeout": 30}  # Add timeout instead of proxies
        )
        print(f"Successfully initialized ChatOpenAI with model {model_name}")
    except Exception as e1:
        print(f"Error using standard ChatOpenAI: {e1}")
        
        try:
            # Fall back to our custom implementation
            print(f"Trying direct OpenAI implementation with model {model_name}")
            llm = DirectOpenAIChat(model_name=model_name, temperature=temperature)
            print(f"Successfully initialized DirectOpenAIChat with model {model_name}")
        except Exception as e2:
            print(f"Error using DirectOpenAIChat: {e2}")
            print("Could not initialize OpenAI model. Check your API key and network connection.")
            
            # Return a simple dummy LLM that just returns a fixed response
            from langchain.llms.fake import FakeListLLM
            llm = FakeListLLM(responses=["I'm sorry, but I couldn't connect to the language model. Please check your OpenAI API key and try again."])
            print("Using fallback FakeListLLM as a last resort")
    
    prompt = create_quran_rag_prompt()
    return LLMChain(llm=llm, prompt=prompt)

def generate_answer(generator, context: str, question: str) -> str:
    """
    Generate an answer based on the context and question
    """
    return generator.run(context=context, question=question)

def process_query(retriever, generator, query: str, filters: Dict = None):
    """
    End-to-end process to answer a query using RAG
    """
    # Retrieve relevant documents
    documents = retrieve_relevant_context(retriever, query, filters)
    
    if not documents:
        return "I couldn't find any relevant information for your query. Could you please rephrase or provide more details?"
    
    # Format context from documents
    context = format_context_from_docs(documents)
    
    # Generate answer
    answer = generate_answer(generator, context, query)
    
    return answer