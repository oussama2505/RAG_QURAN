#!/usr/bin/env python
"""
Streamlit App for RAG Quran System
This application provides a web interface for querying the Quran using the API.
"""
import os
import sys
import streamlit as st
import requests
import json
from dotenv import load_dotenv
import time

# Add parent directory to path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
from src.api_key_manager import load_api_key, ensure_api_key

# Load environment variables
load_dotenv()

# Define API query function
def query_api(question, surah_filter=None):
    """Query the API with a question"""
    try:
        # Build API URL with parameters
        api_endpoint = f"{API_URL}/api/ask"
        params = {
            "question": question
        }
        if surah_filter and surah_filter > 0:
            params["surah"] = surah_filter
        
        # Create a progress bar for the request
        progress_placeholder = st.empty()
        progress_bar = progress_placeholder.progress(0)
        status_text = st.empty()
        status_text.text("Initializing query...")
        
        # Make the request with better progress handling
        try:
            # Initial 2-second timeout just to verify the server is reachable
            requests.get(API_URL, timeout=2)
            
            # Now make the actual request
            status_text.text("Querying the Knowledge Base (0/3): Embedding your question...")
            progress_bar.progress(10)
            
            # Long timeout for heavy processing, but with progress updates
            response = requests.get(
                api_endpoint,
                params=params,
                timeout=180  # 3 minutes timeout for full RAG processing
            )
            # Only reaches here if successful
            progress_bar.progress(100)
            status_text.text("Query completed successfully!")
            time.sleep(0.5)  # Brief pause to show completion
            status_text.empty()
            progress_placeholder.empty()
            
        except requests.exceptions.ConnectTimeout:
            progress_bar.progress(100)
            progress_placeholder.empty()
            status_text.empty()
            st.error(f"⚠️ Connection to API server timed out. Make sure the API server is running at {API_URL}")
            st.info("You can start the API server by running: cd app && uvicorn api:app --reload --port 8000")
            return {
                "answer": "Error: Could not connect to the API server. Please make sure it's running.",
                "sources": []
            }
        except requests.exceptions.ConnectionError:
            progress_bar.progress(100)
            progress_placeholder.empty()
            status_text.empty()
            st.error(f"⚠️ Could not connect to API server at {API_URL}")
            st.info("You can start the API server by running: cd app && uvicorn api:app --reload --port 8000")
            return {
                "answer": "Error: Could not connect to the API server. Please make sure it's running.",
                "sources": []
            }
        except requests.exceptions.ReadTimeout:
            progress_bar.progress(100)
            progress_placeholder.empty()
            status_text.empty()
            st.error(f"⚠️ API request timed out after 3 minutes. The RAG pipeline processing is taking too long.")
            st.info("""This might be due to:
1. Heavy load on the server
2. Large document retrieval
3. Complex embedding generation""")
            return {
                "answer": "Error: The query processing took too long. Try a simpler question or try again later.",
                "sources": []
            }
            
        # Check response
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API error: Status code {response.status_code}")
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                return {
                    "answer": f"Error: {error_detail}",
                    "sources": [],
                    "filters_applied": {}
                }
            except:
                return {
                    "answer": f"Error: Unable to connect to API server. Please check if the API is running.",
                    "sources": [],
                    "filters_applied": {}
                }
                
    except Exception as e:
        st.error(f"Error communicating with API: {str(e)}")
        return {
            "answer": f"Error: {str(e)}",
            "sources": [],
            "filters_applied": {}
        }

# App title and configuration
st.set_page_config(
    page_title="Quran AI Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-header {
        font-size: 1.25rem;
        font-weight: bold;
        margin-top: 1rem;
        color: #333;
    }
    .source-item {
        padding: 0.5rem;
        background-color: #f5f5f5;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    .quran-source {
        border-left: 4px solid #4CAF50;
    }
    .tafsir-source {
        border-left: 4px solid #2196F3;
    }
    .answer-container {
        padding: 1.5rem;
        background-color: #f9f9f9;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# API settings
API_URL = "http://127.0.0.1:8000"  # Using explicit IP instead of localhost

# Function to check and save API key
def check_api_key():
    """Check if API key is available in session state or environment"""
    # First check if key is in session state
    if 'api_key' not in st.session_state or not st.session_state.api_key:
        # Then check environment/file
        api_key = load_api_key()
        if api_key:
            st.session_state.api_key = api_key
            return True
        else:
            # If still not found, we need user input
            return False
    return True

def save_api_key(api_key):
    """Save API key to .env file"""
    try:
        with open('../.env', 'a+') as f:
            f.seek(0)
            content = f.read()
            if 'OPENAI_API_KEY' not in content:
                f.write(f"\nOPENAI_API_KEY={api_key}\n")
                return True
            else:
                # Update existing key
                import re
                new_content = re.sub(
                    r'OPENAI_API_KEY=.*', 
                    f'OPENAI_API_KEY={api_key}', 
                    content
                )
                f.seek(0)
                f.truncate()
                f.write(new_content)
                return True
    except Exception as e:
        st.error(f"Error saving API key: {str(e)}")
        return False

# Display functions for Streamlit

def display_sources(sources):
    """Display the sources in a readable format"""
    if not sources:
        st.info("No sources were found for this query.")
        return
        
    st.markdown('<p class="source-header">Sources:</p>', unsafe_allow_html=True)
    
    for source in sources:
        source_type = source['source_type'] if 'source_type' in source else source.get('type', 'unknown')
        reference = source['reference']
        content = source['content']
        
        if source_type == "quran":
            st.markdown(
                f'<div class="source-item quran-source">'
                f'<strong>Quran {reference}</strong><br>{content}'
                f'</div>',
                unsafe_allow_html=True
            )
        elif source_type.startswith("tafsir_"):
            tafsir_name = source_type.replace("tafsir_", "")
            st.markdown(
                f'<div class="source-item tafsir-source">'
                f'<strong>Tafsir {tafsir_name} on {reference}</strong><br>{content}'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="source-item">'
                f'<strong>{source_type} {reference}</strong><br>{content}'
                f'</div>',
                unsafe_allow_html=True
            )

def main():
    st.markdown('<h1 class="main-header">Quran AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask questions about the Quran and receive answers based on authentic sources</p>', unsafe_allow_html=True)
    
    # Sidebar for settings and information
    with st.sidebar:
        st.title("Settings")
        
        # API key input
        if not check_api_key():
            st.warning("OpenAI API key is required for this application.")
            api_key = st.text_input("Enter your OpenAI API key:", type="password")
            save_key = st.checkbox("Save API key for future sessions")
            
            if st.button("Save API Key"):
                if api_key:
                    # Set in session state
                    st.session_state.api_key = api_key
                    # Set in environment
                    os.environ["OPENAI_API_KEY"] = api_key
                    # Save to file if requested
                    if save_key:
                        if save_api_key(api_key):
                            st.success("API key saved to .env file!")
                        else:
                            st.warning("API key saved for this session only.")
                    else:
                        st.success("API key saved for this session!")
                    st.experimental_rerun()
                else:
                    st.error("Please enter a valid API key")
        
        # Filters
        st.subheader("Filters")
        surah_filter = st.number_input("Filter by Surah number (0 for no filter):", 
                                       min_value=0, max_value=114, value=0)
        
        # API status check
        try:
            response = requests.get(f"{API_URL}", timeout=5)  # Short timeout for quick check
            if response.status_code == 200:
                st.success("✅ API is running and accessible")
                # Show API info
                api_info = response.json()
                st.info(f"API Status: {api_info.get('status', 'Unknown')}")
            else:
                st.error(f"❌ API error: Status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API is not accessible: {type(e).__name__}")
            st.info("To start the API server, run this in your terminal:\n```\ncd app && uvicorn api:app --reload --port 8000\n```")
        
        # About section
        st.subheader("About")
        st.info(
            "This application uses Retrieval-Augmented Generation (RAG) to provide "
            "accurate answers about the Quran based on Quranic verses and tafsir sources. "
            "Questions are processed using embedding-based similarity search and then "
            "answered using OpenAI's language models."
        )
    
    # Main input area
    query = st.text_area("Enter your question about the Quran:", height=100)
    
    # Process the query when the button is clicked
    if st.button("Submit Question"):
        if not query:
            st.warning("Please enter a question.")
        else:
            st.write("")
            with st.container():
                st.write("**Processing your query...**")
                # Call the API
                result = query_api(query, surah_filter=surah_filter if surah_filter > 0 else None)
                
                if 'answer' in result:
                    # Check if it's an error message
                    if result['answer'].startswith("Error:"):
                        st.warning(result['answer'])
                    else:
                        # Display the answer
                        st.markdown('<div class="answer-container">', unsafe_allow_html=True)
                        st.markdown("### Answer")
                        st.write(result['answer'])
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Display the sources
                        if 'sources' in result and result['sources']:
                            display_sources(result['sources'])
                        elif not result['answer'].startswith("Error:"):
                            st.info("No specific sources were provided for this answer.")
    
    # Sample questions to help users get started
    st.subheader("Sample Questions")
    sample_questions = [
        "What does the Quran say about kindness to parents?",
        "What are the major themes of Surah Al-Baqarah?",
        "How does the Quran describe Paradise?",
        "What is the significance of Ramadan in the Quran?",
        "What does the Quran say about honesty and truthfulness?"
    ]
    
    col1, col2 = st.columns(2)
    for i, question in enumerate(sample_questions):
        if i < 3:
            with col1:
                if st.button(question, key=f"q_{i}"):
                    # Set the query and automatically press submit
                    result = query_api(question, surah_filter=surah_filter if surah_filter > 0 else None)
                    
                    # Display the answer
                    st.markdown('<div class="answer-container">', unsafe_allow_html=True)
                    st.markdown("### Answer")
                    st.write(result['answer'])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display the sources
                    if 'sources' in result:
                        display_sources(result['sources'])
        else:
            with col2:
                if st.button(question, key=f"q_{i}"):
                    # Set the query and automatically press submit
                    result = query_api(question, surah_filter=surah_filter if surah_filter > 0 else None)
                    
                    # Display the answer
                    st.markdown('<div class="answer-container">', unsafe_allow_html=True)
                    st.markdown("### Answer")
                    st.write(result['answer'])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display the sources
                    if 'sources' in result:
                        display_sources(result['sources'])

if __name__ == "__main__":
    main()
