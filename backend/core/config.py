import os
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
QURAN_DATA_PATH = os.path.join(DATA_DIR, 'quran.json')
TAFSIR_DIR_PATH = os.path.join(DATA_DIR, 'tafsirs')
VECTOR_DB_PATH = os.path.join(BASE_DIR, 'vector_db')

# Model settings
EMBEDDING_MODEL_TYPE = os.getenv('EMBEDDING_MODEL_TYPE', 'openai')
LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME', 'gpt-4-turbo')

# Processing settings
CHUNK_SIZE = 1000