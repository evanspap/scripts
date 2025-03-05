#!/bin/bash

################################################################################
# Script Name: replace_text.sh
# Description: This script replaces a specified word in all files of a given 
#              format within the current directory and copies the modified 
#              files to a specified output directory.
#
# Usage: ./replace_text.sh <target_word> <replacement_word> <file_extension> <output_directory>
#
# Example: ./replace_text.sh pocket ASpock gb modified_files
#   - Replaces "pocket" with "ASpock" in all .gb files in the current directory.
#   - Saves modified files in the "modified_files" directory.
#
# Requirements:
#   - The script must be executed in a directory containing files with the given
#     extension.
#   - User must provide all four required arguments.
#
# Author: [EP]
# Version: 1.0
################################################################################

# Check if required arguments are provided
if [[ $# -ne 4 ]]; then
    echo "Usage: $0 <target_word> <replacement_word> <file_extension> <output_directory>"
    echo "Example: $0 pocket ASpock gb modified_files"
    exit 1
fi

TARGET_WORD=$1
REPLACEMENT_WORD=$2
FILE_EXTENSION=$3
OUTPUT_DIR=$4

# Create output folder if it does not exist
mkdir -p "$OUTPUT_DIR"

# Process files
for file in *."$FILE_EXTENSION"; do
    [[ -f "$file" ]] || continue  # Skip if no matching files
    sed -i "s/$TARGET_WORD/$REPLACEMENT_WORD/g" "$file"  # Modify file in place
    cp "$file" "$OUTPUT_DIR/"  # Copy modified file to output folder
    echo "Processed: $file → Copied to $OUTPUT_DIR/"
done

echo "Replacement complete! Modified files are in $OUTPUT_DIR/"
