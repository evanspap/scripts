#!/bin/bash

# General Bash Script to Process a List of Lines and Create a Two-Column CSV
# ---------------------------------------------------------------------------
# This script reads a file containing a list of lines (one per line),
# replaces occurrences of a specified search word with a replacement word in each line,
# and outputs a two-column CSV where:
#   - Column 1: Original line
#   - Column 2: Modified line
#
# Usage:
#   ./modify_lines.sh <input_file> <search_word> <replacement_word>
#
# Example:
#   ./modify_lines.sh files_list.txt BACKUP_BAS ASCII
#
# The result will be printed to the standard output (stdout).
#
# Author: Vaggelis
# Date: 27 April 2025

# Check if all three arguments were provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_file> <search_word> <replacement_word>"
    exit 1
fi

input_file="$1"
search_word="$2"
replacement_word="$3"

# Process the input file
while read -r line; do
    modified=$(echo "$line" | sed "s/${search_word}/${replacement_word}/")
    echo "$line,$modified"
done < "$input_file"
