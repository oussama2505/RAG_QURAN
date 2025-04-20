#!/usr/bin/env python3

import os
import re
import sys
import argparse
from datetime import datetime

def parse_arguments():
    parser = argparse.ArgumentParser(description="Update CHANGELOG.md and README.md for a new release")
    parser.add_argument('version', help="New version number (e.g. 1.2.0)")
    parser.add_argument('--type', choices=['major', 'minor', 'patch'], default='minor',
                        help="Type of release (major, minor, patch)")
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'),
                        help="Release date (YYYY-MM-DD)")
    parser.add_argument('--changelog-path', default="../CHANGELOG.md",
                        help="Path to CHANGELOG.md file")
    parser.add_argument('--readme-path', default="../README.md",
                        help="Path to README.md file")
    
    return parser.parse_args()

def update_changelog(version, date, changelog_path, release_type):
    try:
        with open(changelog_path, 'r') as file:
            content = file.read()
        
        # Define the template for the new release section
        new_release_template = f"""## [{version}] - {date}

### Added
- 

### Changed
- 

### Fixed
- 

"""
        
        # Find where to insert the new release section
        pattern = r'## \[\d+\.\d+\.\d+\] - \d{4}-\d{2}-\d{2}'
        match = re.search(pattern, content)
        
        if match:
            # Insert the new release section before the first existing release section
            updated_content = content[:match.start()] + new_release_template + content[match.start():]
            
            with open(changelog_path, 'w') as file:
                file.write(updated_content)
                
            print(f"✅ CHANGELOG.md updated with new {version} release section")
            return True
        else:
            print("❌ Couldn't find a proper insertion point in CHANGELOG.md")
            return False
            
    except Exception as e:
        print(f"❌ Error updating CHANGELOG.md: {str(e)}")
        return False

def update_readme(version, readme_path):
    try:
        with open(readme_path, 'r') as file:
            content = file.read()
        
        # Update version badge in README
        version_pattern = r'version-(\d+\.\d+\.\d+)-blue'
        updated_content = re.sub(version_pattern, f'version-{version}-blue', content)
        
        # Update any other version references
        other_version_pattern = r'Version (\d+\.\d+\.\d+)'
        updated_content = re.sub(other_version_pattern, f'Version {version}', updated_content)
        
        # Update "last updated" references if they exist
        date_pattern = r'Last updated: \d{4}-\d{2}-\d{2}'
        today = datetime.now().strftime('%Y-%m-%d')
        updated_content = re.sub(date_pattern, f'Last updated: {today}', updated_content)
        
        with open(readme_path, 'w') as file:
            file.write(updated_content)
            
        print(f"✅ README.md updated with version {version}")
        return True
            
    except Exception as e:
        print(f"❌ Error updating README.md: {str(e)}")
        return False

def main():
    args = parse_arguments()
    
    # Normalize paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    changelog_path = os.path.join(script_dir, args.changelog_path)
    readme_path = os.path.join(script_dir, args.readme_path)
    
    print(f"🚀 Preparing release v{args.version} ({args.date})")
    
    # Update CHANGELOG.md
    changelog_updated = update_changelog(args.version, args.date, changelog_path, args.type)
    
    # Update README.md
    readme_updated = update_readme(args.version, readme_path)
    
    if changelog_updated and readme_updated:
        print(f"""
✅ Release documentation prepared successfully!

Next steps:
1. Edit the CHANGELOG.md to add details about what was added, changed, or fixed
2. Review README.md to ensure all version references are correct
3. Commit the changes with: git commit -m "docs: prepare release v{args.version}"
4. Create a new tag: git tag v{args.version}
5. Push changes and tags: git push origin main && git push origin v{args.version}
""")
    else:
        print("⚠️ There were some issues with updating the documentation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
