#!/usr/bin/env python3
import re
import json
import os

def extract_sura_name(comment_line):
    """Extract surah name from SQL comment line"""
    # Pattern matches "-- Sura X (name)" format
    pattern = r'-- Sura (\d+) \((.*?)\)'
    match = re.search(pattern, comment_line)
    if match:
        return match.group(2)  # Return the name portion
    return f"Surah {match.group(1)}" if match else "Unknown"

def parse_sql_file(file_path):
    """Parse the SQL file and convert to our JSON structure"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Prepare the result structure
    result = {"surahs": []}
    
    # Split by surah comments to process one surah at a time
    surah_blocks = re.split(r'-- Sura \d+', content)
    
    # Skip the first block (before any surah)
    surah_blocks = surah_blocks[1:]
    
    # Extract surah names
    surah_names = []
    for line in content.split('\n'):
        if '-- Sura' in line:
            name = extract_sura_name(line)
            surah_names.append(name)
    
    current_surah = 0
    
    # Process each surah block
    for i, block in enumerate(surah_blocks):
        if i >= len(surah_names):
            break
            
        # Extract the INSERT statements
        insert_matches = re.findall(r'\(\d+, (\d+), (\d+), \'(.*?)\'\)', block)
        
        # Skip if no verses found
        if not insert_matches:
            continue
        
        # Get surah number from first match
        surah_num = int(insert_matches[0][0])
        
        # Create a new surah object
        surah = {
            "number": surah_num,
            "name": surah_names[i],
            "verses": []
        }
        
        # Add all verses
        for match in insert_matches:
            surah_num = int(match[0])
            verse_num = int(match[1])
            verse_text = match[2]
            
            surah["verses"].append({
                "number": verse_num,
                "text": verse_text
            })
        
        # Add surah to result
        result["surahs"].append(surah)
    
    return result

def main():
    # Input and output file paths
    input_file = 'quran-simple.sql'
    output_file = 'data/quran.json'
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Parse SQL file and get JSON structure
    quran_data = parse_sql_file(input_file)
    
    # Sort surahs by number to ensure correct order
    quran_data["surahs"].sort(key=lambda x: x["number"])
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(quran_data, file, ensure_ascii=False, indent=2)
    
    print(f"Conversion complete! JSON data written to {output_file}")
    print(f"Total surahs: {len(quran_data['surahs'])}")
    
    # Print some stats
    total_verses = sum(len(surah['verses']) for surah in quran_data['surahs'])
    print(f"Total verses: {total_verses}")

if __name__ == "__main__":
    main()
