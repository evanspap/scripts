#!/bin/bash

# Rename Files Script
# This script renames files in a specified folder by replacing occurrences of a given search expression with a replacement expression.
# Usage:
#   ./rename_files.sh [folder] [search] [replace] [--dry-run]
# Example:
#   ./rename_files.sh folder1 input output
#   ./rename_files.sh folder1 input output --dry-run (only show changes, don't apply them)
# If no folder is provided, it defaults to "folder1".

# Check if arguments are provided
if [ $# -lt 3 ]; then
    echo "Usage: ./rename_files.sh [folder] [search] [replace] [--dry-run]"
    echo "Example: ./rename_files.sh folder1 input output"
    echo "         ./rename_files.sh folder1 input output --dry-run"
    exit 1
fi

# Set folder, search, and replace expressions from arguments
FOLDER=$1
SEARCH=$2
REPLACE=$3
DRY_RUN=false

# Check if dry-run option is set
if [[ "$4" == "--dry-run" ]]; then
    DRY_RUN=true
fi

# Check if folder exists
if [ ! -d "$FOLDER" ]; then
    echo "Error: Folder '$FOLDER' does not exist."
    exit 1
fi

# Check if there are files matching the pattern
shopt -s nullglob
FILES=("$FOLDER"/*$SEARCH*)
if [ ${#FILES[@]} -eq 0 ]; then
    echo "No files containing '$SEARCH' found in $FOLDER."
    exit 0
fi

# Dry run: Show intended changes
echo "Dry run - Showing renaming changes:"
for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        new_name="${file//$SEARCH/$REPLACE}"
        echo "Rename: $file -> $new_name"
    fi
done

# If dry-run, exit without renaming
if [ "$DRY_RUN" = true ]; then
    echo "Dry run mode enabled. No files were renamed."
    exit 0
fi

echo
read -p "Proceed with renaming? (y/n): " choice
if [[ "$choice" != "y" ]]; then
    echo "Operation cancelled."
    exit 0
fi

# Perform renaming
for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        new_name="${file//$SEARCH/$REPLACE}"
        mv "$file" "$new_name"
        echo "Renamed: $file -> $new_name"
    fi
done

echo "Renaming completed."
