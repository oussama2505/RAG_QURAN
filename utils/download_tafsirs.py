#!/usr/bin/env python3
import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import time

# Create necessary directories
os.makedirs('data/tafsirs', exist_ok=True)

# Base URL for the tafsir API
BASE_URL = "https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main"

def fetch_json(url):
    """Fetch JSON from URL with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error fetching {url}, retrying... ({e})")
                time.sleep(2)  # Wait before retrying
            else:
                print(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                return None

def get_available_editions():
    """Get list of available tafsir editions"""
    url = f"{BASE_URL}/tafsir/editions.json"
    editions = fetch_json(url)
    if not editions:
        print("Failed to fetch editions list!")
        return []
    print(f"Found {len(editions)} available tafsir editions")
    return editions

def download_tafsir(edition, selected_surah=None):
    """
    Download tafsir for a specific edition
    
    Args:
        edition: The edition info dict
        selected_surah: If provided, only download this surah number
    """
    surah_range = [selected_surah] if selected_surah else range(1, 115)
    edition_slug = edition['slug']  # Using the correct field name 'slug'
    language = edition.get('language_name', 'unknown')  # Using language_name
    name = edition['name']
    author = edition.get('author_name', 'Unknown')
    
    print(f"Downloading {name} by {author} ({language}) tafsir...")
    
    tafsir_data = []
    
    for surah_num in tqdm(surah_range, desc=f"Downloading {edition_slug}"):
        # Get the tafsir for this surah
        surah_url = f"{BASE_URL}/tafsir/{edition_slug}/{surah_num}.json"
        surah_data = fetch_json(surah_url)
        
        if not surah_data:
            continue
            
        # Extract and reformat the ayahs into our desired structure
        for ayah in surah_data.get('ayahs', []):
            ayah_num = ayah.get('number')
            text = ayah.get('text', '')
            
            # Skip empty texts
            if not text or text.strip() == '':
                continue
                
            # Create the reference in format "surah:ayah"
            reference = f"{surah_num}:{ayah_num}"
            
            # Add to our formatted data
            tafsir_data.append({
                'reference': reference,
                'explanation': text
            })
    
    # Save the formatted data
    output_file = f"data/tafsirs/{edition_slug}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tafsir_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(tafsir_data)} verses of tafsir to {output_file}")
    return len(tafsir_data)

def main():
    # Get all available editions
    editions = get_available_editions()
    
    if not editions:
        print("No editions found. Exiting.")
        return
    
    # Filter for Arabic tafsirs
    arabic_editions = [e for e in editions if e.get('language_name', '').lower() == 'arabic']
    print(f"Found {len(arabic_editions)} Arabic tafsir editions")
    
    # Print available Arabic editions for user to choose
    print("\nAvailable Arabic Tafsir Editions:")
    for idx, edition in enumerate(arabic_editions):
        author = edition.get('author_name', 'Unknown')
        print(f"{idx+1}. {edition['name']} by {author} - {edition['slug']}")
    
    # Ask user which editions to download
    print("\nOptions:")
    print("1. Download all Arabic editions")
    print("2. Download specific Arabic editions")
    print("3. Download the most popular Arabic tafsirs")
    print("4. Download 3 random Arabic tafsirs for testing")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        # Download all Arabic editions
        for edition in arabic_editions:
            download_tafsir(edition)
    
    elif choice == '2':
        # Ask for specific editions
        selected_indices = input("Enter the numbers of editions to download (comma separated, e.g., 1,3,5): ").strip()
        try:
            indices = [int(idx.strip()) - 1 for idx in selected_indices.split(',')]
            selected_editions = [arabic_editions[idx] for idx in indices if 0 <= idx < len(arabic_editions)]
            
            for edition in selected_editions:
                download_tafsir(edition)
        except (ValueError, IndexError) as e:
            print(f"Error selecting editions: {e}")
    
    elif choice == '3':
        # Download popular Arabic tafsirs
        # Look for common popular tafsir identifiers
        popular_tafsirs = [
            edition for edition in arabic_editions 
            if any(name in edition['slug'].lower() for name in 
            ['ibn-kathir', 'jalalayn', 'tabari', 'qurtubi', 'muyassar'])
        ]
        
        if not popular_tafsirs:
            print("No popular Arabic tafsirs found. Downloading first 3 Arabic editions instead.")
            popular_tafsirs = arabic_editions[:3] if len(arabic_editions) >= 3 else arabic_editions
        
        print(f"Downloading {len(popular_tafsirs)} popular Arabic tafsirs:")
        for edition in popular_tafsirs:
            print(f"- {edition['name']} by {edition.get('author_name', 'Unknown')}")
        
        for edition in popular_tafsirs:
            download_tafsir(edition)
    
    elif choice == '4':
        # Download 3 random Arabic tafsirs for testing but only first 3 surahs
        test_editions = arabic_editions[:3] if len(arabic_editions) >= 3 else arabic_editions
        print(f"Downloading first 3 surahs from {len(test_editions)} Arabic tafsirs for testing:")
        
        for edition in test_editions:
            print(f"- {edition['name']} by {edition.get('author_name', 'Unknown')}")
        
        for edition in test_editions:
            # Only download first 3 surahs to save time
            for surah_num in range(1, 4):
                download_tafsir(edition, surah_num)
    
    else:
        print("Invalid choice. Exiting.")
        return
    
    print("\nDownload complete! Tafsir files are ready in data/tafsirs/")

if __name__ == "__main__":
    main()
