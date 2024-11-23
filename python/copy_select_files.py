import os
import shutil
import sys

def print_usage():
    print("Usage: python script.py <source_folder> <destination_folder> <identifiers_file> <strip_characters> [--dry-run]")
    sys.exit(1)

# Check if enough arguments are provided
if len(sys.argv) < 5 or len(sys.argv) > 6:
    print_usage()

# Get source and destination folder paths, identifiers file, and characters to strip
source_folder = sys.argv[1]
destination_folder = sys.argv[2]
identifiers_file = sys.argv[3]
strip_characters = sys.argv[4]
dry_run = "--dry-run" in sys.argv

# Ensure the destination folder exists (if not a dry run)
if not dry_run:
    os.makedirs(destination_folder, exist_ok=True)

# Read identifiers from the provided file
try:
    with open(identifiers_file, 'r') as f:
        identifiers = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"Error: File '{identifiers_file}' not found.")
    sys.exit(1)

# Remove specified characters and add '.fasta' to each identifier
file_names = [id.strip(strip_characters) + '.fasta' for id in identifiers]

# Process each file
for file_name in file_names:
    source_file_path = os.path.join(source_folder, file_name)
    destination_file_path = os.path.join(destination_folder, file_name)

    # Check if the file exists in the source folder
    if os.path.exists(source_file_path):
        if dry_run:
            print(f"Would copy: {source_file_path} to {destination_file_path}")
        else:
            shutil.copy(source_file_path, destination_file_path)
            print(f"Copied: {file_name}")
    else:
        print(f"File not found: {file_name}")

# Dry-run feedback
if dry_run:
    print("\nDry run complete. No files were copied.")
