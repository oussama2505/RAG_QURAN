# src/generator.py
import os
from typing import List, Dict, Any
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema import Document
from langchain_core.language_models.chat_models import BaseChatModel
from dotenv import load_dotenv
from src.retriever import retrieve_relevant_context, format_context_from_docs
from src.llm_client import get_chat_model, UnifiedLLMChat

load_dotenv()

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

Ensure your response is well-structured with:
1. A direct answer to the question
2. Supporting evidence from the Quran verses and/or tafsir provided in the context
3. If applicable, mention different scholarly interpretations

Cite specific Surah and verse numbers when referencing Quranic text (e.g., "Quran 2:255").
"""
    
    human_template = "{question}"
    
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    return ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

def create_answer_generator(model_name="gpt-3.5-turbo", temperature=0, max_tokens=1000):
    """
    Create an LLM chain for generating answers
    """
    # Get an LLM instance using our unified client
    llm = get_chat_model(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    prompt = create_quran_rag_prompt()
    return LLMChain(llm=llm, prompt=prompt)

def generate_answer(generator, context: str, question: str) -> str:
    """
    Generate an answer based on the context and question
    """
    try:
        # Log query details for debugging
        print(f"Generating answer for question: {question[:50]}...")
        print(f"Context length: {len(context)} characters")
        
        # Run the chain with timeout handling
        response = generator.run(context=context, question=question)
        return response
    except Exception as e:
        error_msg = f"Error generating answer: {str(e)}"
        print(error_msg)
        return "I encountered an error processing your query. Please try again or rephrase your question."

def process_query(retriever, generator, query: str, filters: Dict = None):
    """
    End-to-end process to answer a query using RAG
    """
    print(f"\n{'='*50}\nProcessing query: {query}\n{'='*50}")
    
    try:
        # Retrieve relevant documents
        documents = retrieve_relevant_context(retriever, query, filters)
        
        if not documents:
            print("No relevant documents found")
            return "I couldn't find any relevant information for your query. Could you please rephrase or provide more details?"
        
        print(f"Retrieved {len(documents)} relevant documents")
        
        # Format context from documents
        context = format_context_from_docs(documents)
        
        # Log sources for debugging
        sources = [f"{doc.metadata.get('source', 'unknown')}: {doc.metadata.get('reference', 'unknown')}" 
                  for doc in documents]
        print(f"Sources: {sources}")
        
        # Try direct OpenAI implementation first
        try:
            from src.direct_openai import generate_answer_with_openai
            print("Using direct OpenAI implementation")
            answer = generate_answer_with_openai(context, query)
            if answer and not answer.startswith("I encountered an error"):
                return answer
            print("Direct OpenAI implementation failed, falling back to LangChain")
        except Exception as e:
            print(f"Error with direct OpenAI implementation: {e}")
        
        # Fall back to LangChain if direct implementation fails
        answer = generate_answer(generator, context, query)
        
        return answer
    except Exception as e:
        error_msg = f"Error in RAG pipeline: {str(e)}"
        print(error_msg)
        return "I encountered a technical issue while processing your query. Please try again later."