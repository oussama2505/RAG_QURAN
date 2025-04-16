# backend/core/data_processing.py
import json
import os
from typing import Dict, List, Any
import re

def load_quran_data(quran_path: str) -> List[Dict[str, Any]]:
    """
    Load Quran text from JSON file and convert to document format
    """
    with open(quran_path, 'r', encoding='utf-8') as file:
        quran_data = json.load(file)
    
    documents = []
    for surah in quran_data['surahs']:
        surah_num = surah['number']
        surah_name = surah['name']
        
        for verse in surah['verses']:
            verse_num = verse['number']
            verse_text = verse['text']
            
            # Create document with metadata
            documents.append({
                'content': verse_text,
                'metadata': {
                    'source': 'quran',
                    'surah_num': surah_num,
                    'surah_name': surah_name,
                    'verse_num': verse_num,
                    'reference': f"{surah_num}:{verse_num}"
                }
            })
    
    return documents

def load_tafsir_data(tafsir_dir: str) -> List[Dict[str, Any]]:
    """
    Load tafsir documents from directory
    """
    tafsir_documents = []
    
    for tafsir_file in os.listdir(tafsir_dir):
        if not tafsir_file.endswith('.json'):
            continue
            
        tafsir_name = os.path.splitext(tafsir_file)[0]
        tafsir_path = os.path.join(tafsir_dir, tafsir_file)
        
        with open(tafsir_path, 'r', encoding='utf-8') as file:
            tafsir_data = json.load(file)
        
        # Handle different tafsir data formats
        if isinstance(tafsir_data, dict):
            # Dictionary format with reference as keys
            for reference, content in tafsir_data.items():
                # Extract surah and verse numbers from the key
                match = re.match(r'(\d+):(\d+)', reference)
                if match:
                    surah_num, verse_num = map(int, match.groups())
                    
                    # Get the explanation
                    explanation = content.get('text', '') if isinstance(content, dict) else str(content)
                    
                    tafsir_documents.append({
                        'content': explanation,
                        'metadata': {
                            'source': f'tafsir_{tafsir_name}',
                            'surah_num': surah_num,
                            'verse_num': verse_num,
                            'reference': reference
                        }
                    })
        elif isinstance(tafsir_data, list):
            # List format where each item is expected to have reference and explanation
            for item in tafsir_data:
                if isinstance(item, dict) and 'reference' in item and ('explanation' in item or 'text' in item):
                    reference = item.get('reference')
                    explanation = item.get('explanation', item.get('text', ''))
                    
                    # Extract surah and verse numbers
                    match = re.match(r'(\d+):(\d+)', reference)
                    if match:
                        surah_num, verse_num = map(int, match.groups())
                        
                        tafsir_documents.append({
                            'content': explanation,
                            'metadata': {
                                'source': f'tafsir_{tafsir_name}',
                                'surah_num': surah_num,
                                'verse_num': verse_num,
                                'reference': reference
                            }
                        })
        else:
            print(f"Warning: Unsupported data format in {tafsir_file}")
    
    return tafsir_documents

def create_document_chunks(documents: List[Dict[str, Any]], chunk_size: int = 1000) -> List[Dict[str, Any]]:
    """
    Split longer documents into chunks while preserving metadata
    """
    chunked_docs = []
    
    for doc in documents:
        content = doc['content']
        metadata = doc['metadata']
        
        # Only chunk if content exceeds chunk_size
        if len(content) <= chunk_size:
            chunked_docs.append(doc)
        else:
            # Simple chunking by splitting at periods
            sentences = content.split('. ')
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= chunk_size:
                    current_chunk += sentence + ". "
                else:
                    # Save current chunk and start a new one
                    if current_chunk:
                        chunked_docs.append({
                            'content': current_chunk.strip(),
                            'metadata': metadata.copy()
                        })
                    current_chunk = sentence + ". "
            
            # Add the last chunk if not empty
            if current_chunk:
                chunked_docs.append({
                    'content': current_chunk.strip(),
                    'metadata': metadata.copy()
                })
    
    return chunked_docs