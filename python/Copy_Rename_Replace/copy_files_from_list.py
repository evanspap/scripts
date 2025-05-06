"""
copy_files_from_list.py
------------------------

This script copies a list of files from a given source folder
to a specified destination folder.

The list of files must be provided in a text file (one filename per line).
The paths inside the list are relative to the source folder.

Usage:
    python copy_files_from_list.py <source_folder> <destination_folder> <file_list.txt>

Arguments:
    <source_folder>      Parent folder where the files are located
    <destination_folder> Target folder where the files will be copied
    <file_list.txt>       Text file listing files to copy (one per line)

Example:
    python copy_files_from_list.py C:\BASIC C:\OutputBAS BAS.list

Notes:
- If destination folders don't exist, they will be created automatically.
- Paths are case-insensitive on Windows but case-sensitive on Linux/macOS.

Author: Vaggelis 
Date: 27 April 2025
"""

import sys
import shutil
import os

def copy_files(source_folder, destination_folder, list_file):
    # Ensure paths are absolute
    source_folder = os.path.abspath(source_folder)
    destination_folder = os.path.abspath(destination_folder)

    if not os.path.exists(source_folder):
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return

    if not os.path.isfile(list_file):
        print(f"Error: File list '{list_file}' does not exist.")
        return

    # Create destination if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    with open(list_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    total = len(lines)
    copied = 0

    for relative_path in lines:
        src_path = os.path.join(source_folder, relative_path)
        dest_path = os.path.join(destination_folder, relative_path)

        if not os.path.exists(src_path):
            print(f"Warning: File not found: {src_path}")
            continue

        # Create any needed subdirectories (if desired: currently, flat copy only)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        try:
            shutil.copy2(src_path, dest_path)
            print(f"Copied: {relative_path}")
            copied += 1
        except Exception as e:
            print(f"Failed to copy {relative_path}: {e}")

    print(f"\nCompleted: {copied}/{total} files copied successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage:\n    python copy_files_from_list.py <source_folder> <destination_folder> <file_list.txt>")
    else:
        source = sys.argv[1]
        destination = sys.argv[2]
        file_list = sys.argv[3]
        copy_files(source, destination, file_list)
