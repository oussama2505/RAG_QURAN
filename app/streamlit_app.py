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
import random

# Handle the module import - with fallback if the module doesn't exist
try:
    # Add parent directory to path so we can import from src
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
    from src.api_key_manager import load_api_key, ensure_api_key
except ImportError:
    # Define fallback functions if the module doesn't exist
    def load_api_key():
        """Fallback function to load API key from environment"""
        return os.environ.get("OPENAI_API_KEY", "")
    
    def ensure_api_key():
        """Fallback function to ensure API key exists"""
        return os.environ.get("OPENAI_API_KEY", "")

# Load environment variables
load_dotenv()

# API settings with better error handling
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

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
        
        # Create a progress bar with animated stages
        progress_placeholder = st.empty()
        progress_bar = progress_placeholder.progress(0)
        status_text = st.empty()
        status_text.text("✨ Initializing your query...")
        
        # Make the request with animated progress handling
        try:
            # Initial quick timeout just to verify the server is reachable
            try:
                requests.get(API_URL, timeout=2)
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
                progress_bar.progress(100)
                progress_placeholder.empty()
                status_text.empty()
                st.error(f"⚠️ Cannot connect to API server at {API_URL}")
                st.info("You can start the API server by running: cd app && uvicorn api:app --reload --port 8000")
                return {
                    "answer": f"Error: Could not connect to the API server at {API_URL}. Please make sure it's running.",
                    "sources": []
                }
            
            # Now make the actual request with animated progress
            status_text.text("🔍 Querying the Knowledge Base (1/4): Embedding your question...")
            for i in range(10, 30):
                time.sleep(0.05)
                progress_bar.progress(i)
            
            status_text.text("📚 Querying the Knowledge Base (2/4): Retrieving relevant passages...")
            for i in range(30, 60):
                time.sleep(0.05)
                progress_bar.progress(i)
                
            status_text.text("🧩 Querying the Knowledge Base (3/4): Analyzing context...")
            for i in range(60, 85):
                time.sleep(0.05)
                progress_bar.progress(i)
                
            status_text.text("✍️ Querying the Knowledge Base (4/4): Formulating response...")
            for i in range(85, 95):
                time.sleep(0.05)
                progress_bar.progress(i)
            
            # Request with timeout handling
            try:
                response = requests.get(
                    api_endpoint,
                    params=params,
                    timeout=180  # 3 minutes timeout for full RAG processing
                )
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
            except requests.exceptions.ConnectionError:
                progress_bar.progress(100)
                progress_placeholder.empty()
                status_text.empty()
                st.error(f"⚠️ Connection lost to API server at {API_URL}")
                return {
                    "answer": "Error: Connection to the API server was lost. Please check if it's still running.",
                    "sources": []
                }
                
            # Only reaches here if successful
            for i in range(95, 101):
                time.sleep(0.03)
                progress_bar.progress(i)
                
            status_text.text("✅ Query completed successfully!")
            time.sleep(0.8)  # Slightly longer pause to show completion
            status_text.empty()
            progress_placeholder.empty()
            
            # Check response
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    st.error("⚠️ API returned invalid JSON response")
                    return {
                        "answer": "Error: The API response was not in the expected format.",
                        "sources": []
                    }
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
                        "answer": f"Error: Unable to process API response. Status code: {response.status_code}",
                        "sources": [],
                        "filters_applied": {}
                    }
                    
        except Exception as e:
            st.error(f"Error during API request: {str(e)}")
            return {
                "answer": f"Error: {str(e)}",
                "sources": []
            }
                
    except Exception as e:
        st.error(f"Error communicating with API: {str(e)}")
        return {
            "answer": f"Error: {str(e)}",
            "sources": [],
            "filters_applied": {}
        }

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
        st.info("📚 No sources were found for this query.")
        return
        
    st.markdown('<p class="source-header">📖 Sources:</p>', unsafe_allow_html=True)
    
    for source in sources:
        source_type = source['source_type'] if 'source_type' in source else source.get('type', 'unknown')
        reference = source['reference']
        content = source['content']
        
        if source_type == "quran":
            st.markdown(
                f'<div class="source-item quran-source">'
                f'<strong>🕋 Quran {reference}</strong><br>{content}'
                f'</div>',
                unsafe_allow_html=True
            )
        elif source_type.startswith("tafsir_"):
            tafsir_name = source_type.replace("tafsir_", "")
            st.markdown(
                f'<div class="source-item tafsir-source">'
                f'<strong>📜 Tafsir {tafsir_name} on {reference}</strong><br>{content}'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="source-item">'
                f'<strong>📚 {source_type} {reference}</strong><br>{content}'
                f'</div>',
                unsafe_allow_html=True
            )

# Quote of the day function
def get_daily_quote():
    """Return a random Islamic quote for display"""
    quotes = [
        {"text": "The best among you are those who have the best manners and character.", "author": "Prophet Muhammad (PBUH)"},
        {"text": "Verily, with hardship comes ease.", "author": "Quran 94:6"},
        {"text": "The cure for ignorance is to question.", "author": "Ibn Rushd"},
        {"text": "Be in this world as if you were a stranger or a traveler.", "author": "Prophet Muhammad (PBUH)"},
        {"text": "Knowledge is better than wealth because knowledge protects you while you have to protect wealth.", "author": "Ali ibn Abi Talib (RA)"},
        {"text": "Seek knowledge from the cradle to the grave.", "author": "Prophet Muhammad (PBUH)"},
        {"text": "The greatest jihad is to battle your own soul; to fight the evil within yourself.", "author": "Prophet Muhammad (PBUH)"},
        {"text": "For indeed, with hardship [will be] ease. Indeed, with hardship [will be] ease.", "author": "Quran 94:5-6"},
        {"text": "Richness is not having many possessions. Rather, true richness is the richness of the soul.", "author": "Prophet Muhammad (PBUH)"}
    ]
    return random.choice(quotes)

def load_sample_questions():
    """Load sample questions for the app"""
    return [
        "What does the Quran say about seeking knowledge?",
        "How does the Quran describe Paradise?",
        "What is the importance of patience in Islam?",
        "What does the Quran say about kindness to parents?",
        "How does the Quran describe the creation of the universe?"
    ]

# App config and styling
def set_app_styling():
    """Set up app configuration and styling"""
    # App title and configuration
    st.set_page_config(
        page_title="Quran Knowledge Explorer",
        page_icon="☪️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for Islamic-inspired elegant design
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Lateef:wght@400;600;700&family=Quicksand:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        .stApp {
            background-color: #FAFAFA;
            font-family: 'Quicksand', sans-serif;
            color: #2D3748;
        }
        
        /* Main Header with Dynamic Gradient Effect */
        .main-header {
            font-family: 'Lateef', serif;
            font-size: 3.5rem;
            color: #234E52;
            text-align: center;
            margin: 1rem 0;
            padding: 2rem;
            background: linear-gradient(120deg, #D6FFFA 0%, #B2F5EA 50%, #D6FFFA 100%);
            background-size: 200% auto;
            border-radius: 20px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
            animation: gradient 6s ease infinite;
        }
        
        @keyframes gradient {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
        
        /* Sub Header */
        .sub-header {
            font-family: 'Quicksand', sans-serif;
            font-size: 1.4rem;
            color: #2C5282;
            text-align: center;
            margin-bottom: 2.5rem;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        
        /* Question Input Area with Focus Animation */
        .stTextArea textarea {
            border: 2px solid #E2E8F0;
            border-radius: 15px;
            font-size: 1.1rem;
            padding: 1.2rem;
            background-color: white;
            color: #2D3748;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
        }
        
        .stTextArea textarea:focus {
            border-color: #4299E1;
            box-shadow: 0 0 15px rgba(66, 153, 225, 0.15);
            transform: translateY(-2px);
        }
        
        /* Enhanced Button Styling with Hover Effects */
        .stButton > button {
            background: linear-gradient(135deg, #38B2AC 0%, #2C7A7B 100%);
            color: white;
            padding: 0.8rem 2rem;
            border-radius: 12px;
            border: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 12px rgba(44, 122, 123, 0.2);
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(44, 122, 123, 0.3);
            background: linear-gradient(135deg, #319795 0%, #2C7A7B 100%);
        }
        
        .stButton > button:active {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(44, 122, 123, 0.2);
        }
        
        /* Card-style Answer Container with Subtle Hover Effect */
        .answer-container {
            background-color: white;
            padding: 2.2rem;
            border-radius: 18px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
            margin: 2rem 0;
            color: #2D3748;
            transition: all 0.3s ease;
        }
        
        .answer-container:hover {
            box-shadow: 0 12px 20px rgba(0, 0, 0, 0.08);
            transform: translateY(-3px);
        }
        
        .answer-container h3 {
            color: #2C5282;
            font-family: 'Lateef', serif;
            font-size: 2rem;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid #4299E1;
            padding-bottom: 0.8rem;
        }
        
        /* Enhanced Source Items with Hover Animations */
        .source-header {
            font-family: 'Lateef', serif;
            font-size: 1.8rem;
            color: #2D3748;
            margin: 2rem 0 1.2rem 0;
        }
        
        .source-item {
            background-color: #F7FAFC;
            padding: 1.8rem;
            border-radius: 15px;
            margin-bottom: 1.2rem;
            border-left: 5px solid #4299E1;
            transition: all 0.25s ease;
            color: #2D3748;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
        }
        
        .source-item:hover {
            transform: translateX(8px);
            background-color: #EDF2F7;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.05);
        }
        
        .quran-source {
            border-left-color: #38A169;
            background-color: #F0FFF4;
            box-shadow: 0 4px 10px rgba(56, 161, 105, 0.05);
        }
        
        .quran-source:hover {
            box-shadow: 0 6px 12px rgba(56, 161, 105, 0.1);
        }
        
        .tafsir-source {
            border-left-color: #3182CE;
            background-color: #EBF8FF;
            box-shadow: 0 4px 10px rgba(49, 130, 206, 0.05);
        }
        
        .tafsir-source:hover {
            box-shadow: 0 6px 12px rgba(49, 130, 206, 0.1);
        }
        
        /* Sidebar Styling */
        .css-1d391kg, .css-1wrcr25, .css-ffhzg2 {
            background-color: #F7FAFC;
            border-right: 1px solid #E2E8F0;
            padding: 2.2rem 1.2rem;
        }
        
        .sidebar-title {
            font-family: 'Lateef', serif;
            font-size: 2rem;
            color: #2D3748;
            margin-bottom: 2.2rem;
            text-align: center;
            padding-bottom: 0.8rem;
            border-bottom: 2px solid #CBD5E0;
        }
        
        /* Sample Questions with Modern Card Design */
        .sample-question {
            background-color: white;
            padding: 1.2rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            border: 1px solid #E2E8F0;
            cursor: pointer;
            transition: all 0.3s ease;
            color: #2D3748;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
        }
        
        .sample-question:hover {
            background-color: #EBF8FF;
            border-color: #4299E1;
            transform: translateY(-4px);
            box-shadow: 0 8px 15px rgba(66, 153, 225, 0.15);
        }
        
        /* Animated Progress Bar */
        .stProgress > div > div {
            background: linear-gradient(90deg, #38B2AC 0%, #3182CE 50%, #38B2AC 100%);
            background-size: 200% auto;
            animation: progressGradient 2s linear infinite;
        }
        
        @keyframes progressGradient {
            0% {
                background-position: 0% 50%;
            }
            100% {
                background-position: 100% 50%;
            }
        }
        
        /* Enhanced Alert Messages */
        .stAlert {
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            padding: 1.2rem;
            margin: 1.2rem 0;
            transition: all 0.3s ease;
        }
        
        .stAlert:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
        }
        
        /* Info messages */
        .stInfo {
            background-color: #EBF8FF;
            color: #2C5282;
            border-radius: 12px;
            border-left: 5px solid #63B3ED;
        }
        
        /* Warning messages */
        .stWarning {
            background-color: #FEFCBF;
            color: #744210;
            border-radius: 12px;
            border-left: 5px solid #F6E05E;
        }
        
        /* Error messages */
        .stError {
            background-color: #FED7D7;
            color: #822727;
            border-radius: 12px;
            border-left: 5px solid #FC8181;
        }
        
        /* Success messages */
        .stSuccess {
            background-color: #C6F6D5;
            color: #22543D;
            border-radius: 12px;
            border-left: 5px solid #68D391;
        }
        
        /* Form inputs with modern styling */
        .stTextInput input, .stNumberInput input, .stSelectbox > div > div {
            color: #2D3748;
            background-color: white;
            border: 2px solid #E2E8F0;
            border-radius: 10px;
            padding: 0.6rem 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
        }
        
        .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox > div > div:focus {
            border-color: #4299E1;
            box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
            transform: translateY(-2px);
        }
        
        /* Checkbox */
        .stCheckbox label {
            color: #2D3748;
            font-weight: 500;
        }
        
        /* Daily quote section */
        .daily-quote {
            background-color: #EDF2F7;
            padding: 1.5rem;
            border-radius: 15px;
            margin-top: 2rem;
            border-left: 5px solid #718096;
            font-family: 'Lateef', serif;
            font-size: 1.3rem;
            line-height: 1.6;
            color: #2D3748;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
        }
        
        .daily-quote-author {
            text-align: right;
            font-size: 1.1rem;
            font-style: italic;
            margin-top: 1rem;
            color: #4A5568;
        }
        
        /* Surah selector with modern style */
        .surah-selector {
            background-color: white;
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
            margin-bottom: 1.5rem;
        }
        
        /* Recent questions */
        .recent-questions {
            background-color: white;
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
            margin-bottom: 1.5rem;
        }
        
        .recent-question {
            background-color: #F0FFF4;
            padding: 0.8rem 1.2rem;
            border-radius: 30px;
            margin-bottom: 0.8rem;
            font-size: 0.9rem;
            display: inline-block;
            transition: all 0.2s ease;
            cursor: pointer;
            border: 1px solid #C6F6D5;
        }
        
        .recent-question:hover {
            background-color: #C6F6D5;
            transform: translateY(-2px);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
            color: #718096;
            font-size: 0.9rem;
            border-top: 1px solid #E2E8F0;
        }
        
        /* Fix for expander header */
        .streamlit-expanderHeader {
            font-family: 'Quicksand', sans-serif;
            font-weight: 600;
            color: #2D3748;
        }
        
        /* Add subtle pulse animation to search button */
        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(44, 122, 123, 0.4);
            }
            70% {
                box-shadow: 0 0 0 10px rgba(44, 122, 123, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(44, 122, 123, 0);
            }
        }
        
        .pulse-button {
            animation: pulse 2s infinite;
        }
        
        /* Sample question buttons */
        .sample-btn {
            background-color: #EBF8FF;
            border: 1px solid #BEE3F8;
            border-radius: 10px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.7rem;
            font-size: 0.95rem;
            color: #2C5282;
            transition: all 0.2s ease;
            text-align: left;
            font-weight: 500;
        }
        
        .sample-btn:hover {
            background-color: #BEE3F8;
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'question_history' not in st.session_state:
        st.session_state.question_history = []
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
        
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None

def main():
    # Set up app styling
    set_app_styling()
    
    # Initialize session state
    init_session_state()
    
    # Updated Header with Islamic-inspired design
    st.markdown('<h1 class="main-header">بِسْمِ ٱللَّٰهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ<br>Quran Knowledge Explorer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Explore the wisdom of the Holy Quran through AI-assisted research</p>', unsafe_allow_html=True)
    
    # Daily quote - wrapped in a try/except to avoid potential issues
    try:
        daily_quote = get_daily_quote()
        st.markdown(
            f'<div class="daily-quote">'
            f'"{daily_quote["text"]}"'
            f'<div class="daily-quote-author">— {daily_quote["author"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error displaying daily quote: {str(e)}")
    
    # Sidebar with improved styling
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🧭 Guide & Settings</div>', unsafe_allow_html=True)
        
        # API Key section
        if not check_api_key():
            st.warning("🔑 OpenAI API key is required")
            with st.form("api_key_form"):
                api_key = st.text_input("Enter your OpenAI API key:", type="password")
                save_key = st.checkbox("💾 Save API key for future sessions")
                submitted = st.form_submit_button("Save API Key")
                
                if submitted and api_key:
                    st.session_state.api_key = api_key
                    os.environ["OPENAI_API_KEY"] = api_key
                    if save_key and save_api_key(api_key):
                        st.success("✅ API key saved successfully!")
                    st.experimental_rerun()
        
        # Enhanced Surah Filter with description
        st.markdown('<div class="surah-selector">', unsafe_allow_html=True)
        st.markdown("### 📖 Surah Filter")
        surah_filter = st.number_input(
            "Select Surah number (0 for all):",
            min_value=0,
            max_value=114,
            value=0,
            help="Filter results to a specific Surah (1-114)"
        )
        
        if surah_filter > 0:
            surah_names = {
                1: "Al-Fatihah (The Opening)",
                2: "Al-Baqarah (The Cow)",
                3: "Ali 'Imran (Family of Imran)",
                4: "An-Nisa' (The Women)",
                5: "Al-Ma'idah (The Table Spread)",
                # Add more as needed or load dynamically
            }
            if surah_filter in surah_names:
                st.markdown(f"**Selected:** {surah_names[surah_filter]}")
            else:
                st.markdown(f"**Selected:** Surah {surah_filter}")
        else:
            st.markdown("**Selected:** All Surahs")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # API Status with animation
        st.markdown("### 🔄 System Status")
        try:
            response = requests.get(f"{API_URL}", timeout=3)
            if response.status_code == 200:
                st.success("✅ Knowledge base is online and ready")
                st.markdown('''
                <div style="display: flex; align-items: center; background-color: #F0FFF4; padding: 1rem; border-radius: 10px; margin-top: 0.5rem;">
                    <div style="margin-left: 0.5rem;">
                        <p style="margin: 0; color: #2F855A;">API Response Time: Fast ⚡</p>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        except requests.exceptions.RequestException:
            st.error("❌ Knowledge base is not accessible")
            st.info("To start the system, run:\n```\ncd app && uvicorn api:app --reload --port 8000\n```")
        
        # Sample questions
        st.markdown("### 💡 Sample Questions")
        sample_questions = load_sample_questions()
        for question in sample_questions:
            if st.button(question, key=question, help="Click to use this sample question"):
                st.session_state.current_question = question
                st.experimental_rerun()
    
    # Main content area
    st.markdown("## ❓ Ask a Question")
    question = st.text_area("Enter your question about the Quran:", value=st.session_state.current_question, height=100)
    
    if st.button("Search", key="search_button", help="Click to search the Quran for your question"):
        st.session_state.current_question = question
        st.session_state.question_history.append(question)
        st.session_state.last_result = query_api(question, surah_filter)
        st.experimental_rerun()
    
    # Display the last result
    if st.session_state.last_result:
        result = st.session_state.last_result
        st.markdown('<div class="answer-container">', unsafe_allow_html=True)
        st.markdown(f'<h3>Answer:</h3><p>{result["answer"]}</p>', unsafe_allow_html=True)
        display_sources(result["sources"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display recent questions
    if st.session_state.question_history:
        st.markdown("## 🕰️ Recent Questions")
        st.markdown('<div class="recent-questions">', unsafe_allow_html=True)
        for q in st.session_state.question_history[-5:]:
            if st.button(q, key=q, help="Click to search this question again"):
                st.session_state.current_question = q
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">Made with ❤️ by the Quran Knowledge Explorer Team</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()