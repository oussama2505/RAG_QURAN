#!/bin/bash

# This script automates the process of creating a new release
# It updates the CHANGELOG.md and README.md files and commits the changes

set -e

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if version argument is provided
if [ -z "$1" ]; then
    echo "Error: Please provide a version number"
    echo "Usage: ./release.sh <version> [release-type]"
    echo "Example: ./release.sh 1.2.0 minor"
    exit 1
fi

VERSION=$1
RELEASE_TYPE=${2:-minor}  # Default to minor if not specified

# Validate version format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in format X.Y.Z"
    exit 1
fi

# Validate release type
if [[ ! "$RELEASE_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo "Error: Release type must be one of: major, minor, patch"
    exit 1
fi

# Run the Python script to update documentation
python3 update_release_docs.py "$VERSION" --type "$RELEASE_TYPE"

# Ask if the user wants to commit the changes
read -p "Do you want to commit these changes? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd ..
    git add CHANGELOG.md README.md
    git commit -m "docs: prepare release v$VERSION"
    git tag "v$VERSION"
    
    echo "Changes committed and tag created locally."
    read -p "Do you want to push the changes and tag to the remote repository? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        git push origin "v$VERSION"
        echo "✅ Changes and tag pushed to remote repository."
    else
        echo "Changes committed locally. Remember to push when ready:"
        echo "git push origin main && git push origin v$VERSION"
    fi
else
    echo "Changes not committed. You can review and commit manually."
fi

echo "🎉 Release $VERSION preparation completed!"
