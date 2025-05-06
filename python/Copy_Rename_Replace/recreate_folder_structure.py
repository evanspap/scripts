r"""
recreate_folder_structure.py
-----------------------------

This script recreates the directory (subfolder) structure of a given source folder
into a specified target folder, without copying any files.

Usage:
    python recreate_folder_structure.py <source_folder> <target_folder>

Arguments:
    <source_folder>    Folder containing the original directory tree
    <target_folder>    Folder where the directory structure will be recreated

Example:
    python recreate_folder_structure.py C:\BASIC C:\NewStructure

Notes:
- Only directories are created — no files are copied.
- If target folders already exist, they are skipped.
- Useful for setting up empty folder trees for file organization or backups.

Author: Vaggelis
Date: 27 April 2025
"""

import sys
import os

def recreate_structure(source_folder, target_folder):
    # Ensure absolute paths
    source_folder = os.path.abspath(source_folder)
    target_folder = os.path.abspath(target_folder)

    if not os.path.exists(source_folder):
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return

    print(f"Recreating folder structure from:\n  {source_folder}\nto:\n  {target_folder}\n")

    created_count = 0

    for dirpath, dirnames, filenames in os.walk(source_folder):
        # Calculate relative path
        rel_path = os.path.relpath(dirpath, source_folder)
        target_path = os.path.join(target_folder, rel_path)

        try:
            os.makedirs(target_path, exist_ok=True)
            print(f"Created: {target_path}")
            created_count += 1
        except Exception as e:
            print(f"Failed to create {target_path}: {e}")

    print(f"\nCompleted: {created_count} folders created.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:\n    python recreate_folder_structure.py <source_folder> <target_folder>")
    else:
        source = sys.argv[1]
        target = sys.argv[2]
        recreate_structure(source, target)
