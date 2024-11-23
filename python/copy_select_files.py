import os
import shutil
import sys

# Check if enough arguments are provided
if len(sys.argv) != 4:
    print("Usage: python copy_select_files.py <source_folder> <destination_folder> <identifiers_file>")
    sys.exit(1)

# Get source and destination folder paths and identifiers file from command-line arguments
source_folder = sys.argv[1]
destination_folder = sys.argv[2]
identifiers_file = sys.argv[3]

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Read identifiers from the provided file
try:
    with open(identifiers_file, 'r') as f:
        identifiers = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"Error: File '{identifiers_file}' not found.")
    sys.exit(1)

# Remove '>' and add '.fasta' to each identifier
file_names = [id.strip('> ') + '.fasta' for id in identifiers]

# Process each file
for file_name in file_names:
    source_file_path = os.path.join(source_folder, file_name)
    destination_file_path = os.path.join(destination_folder, file_name)

    # Check if the file exists in the source folder
    if os.path.exists(source_file_path):
        # Copy the file to the destination folder
        shutil.copy(source_file_path, destination_file_path)
        print(f"Copied: {file_name}")
    else:
        print(f"File not found: {file_name}")
