#!/usr/bin/env python

import os
import json
import requests
from tqdm import tqdm

def ensure_dir(file_path):
    """Make sure the directory exists."""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_ibn_kathir():
    """Download Ibn Kathir tafsir specifically."""
    output_dir = "data/tafsirs"
    tafsir_file = os.path.join(output_dir, "ar-tafsir-ibn-kathir.json")
    ensure_dir(tafsir_file)
    
    base_url = "https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir"
    edition_slug = "ar-tafsir-ibn-kathir"
    
    print(f"Downloading Ibn Kathir tafsir (Arabic)...")
    
    all_verses = {}
    
    # The Quran has 114 surahs
    progress_bar = tqdm(range(1, 115), desc=f"Downloading {edition_slug}")
    
    for surah_num in progress_bar:
        try:
            url = f"{base_url}/{edition_slug}/{surah_num}.json"
            response = requests.get(url)
            response.raise_for_status()
            
            surah_data = response.json()
            
            # Extract the verses from this surah
            for ayah_data in surah_data.get('ayahs', []):
                verse_key = f"{surah_num}:{ayah_data.get('ayah')}"
                all_verses[verse_key] = {
                    "surah": surah_num,
                    "verse": ayah_data.get('ayah'),
                    "text": ayah_data.get('text')
                }
                
        except Exception as e:
            print(f"Error downloading surah {surah_num}: {e}")
    
    # Save to file
    with open(tafsir_file, 'w', encoding='utf-8') as f:
        json.dump(all_verses, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(all_verses)} verses of tafsir to {tafsir_file}")

if __name__ == "__main__":
    download_ibn_kathir()
