import streamlit as st
import sys
import os

# Add the project root to the path so we can import the src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import quran_rag_query, initialize_data_and_models

# App title
st.title("Quran Knowledge Explorer")
st.write("Ask questions about the Quran and receive answers based on the text and various tafsirs.")

# Initialize system on first run
if 'initialized' not in st.session_state:
    with st.spinner("Initializing knowledge base... This may take a minute."):
        try:
            initialize_data_and_models()
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"Error initializing system: {str(e)}")
            st.stop()

# Sidebar for filters
st.sidebar.header("Filters (Optional)")
surah_filter = st.sidebar.number_input("Surah Number", min_value=0, max_value=114, value=0, 
                                     help="Enter a surah number to restrict search (0 for all)")
verse_filter = st.sidebar.number_input("Verse Number", min_value=0, value=0,
                                    help="Enter a verse number to restrict search (0 for all)")

# Convert 0 to None for filtering
surah_filter = None if surah_filter == 0 else int(surah_filter)
verse_filter = None if verse_filter == 0 else int(verse_filter)

# Text input for question
question = st.text_area("Your Question:", height=100, 
                        placeholder="Example: What does the Quran say about patience?")

# Process the query when the button is clicked
if st.button("Get Answer"):
    if not question:
        st.warning("Please enter a question to proceed.")
    else:
        with st.spinner("Searching and generating response..."):
            try:
                answer = quran_rag_query(question, surah_filter, verse_filter)
                
                # Display results
                st.subheader("Answer:")
                st.write(answer)
                
                # Add info about filters if used
                if surah_filter or verse_filter:
                    filter_text = []
                    if surah_filter:
                        filter_text.append(f"Surah {surah_filter}")
                    if verse_filter:
                        filter_text.append(f"Verse {verse_filter}")
                    
                    st.info(f"Results filtered to: {', '.join(filter_text)}")
                    
            except Exception as e:
                st.error(f"Error processing your query: {str(e)}")

# Display some example questions
st.subheader("Example Questions:")
example_questions = [
    "What does Surah Al-Baqarah verse 255 (Ayatul Kursi) say?",
    "How does the Quran describe paradise?",
    "What does the Quran teach about respecting parents?",
    "Explain the concept of 'taqwa' in the Quran."
]
for q in example_questions:
    if st.button(q):
        st.session_state.question = q
        st.rerun()

# Add some helpful information
st.sidebar.markdown("---")
st.sidebar.subheader("About")
st.sidebar.write("""
This application uses a RAG (Retrieval-Augmented Generation) system to provide 
answers about the Quran based on the Quranic text and various tafsirs (explanations).
""")