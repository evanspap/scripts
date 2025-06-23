#!/usr/bin/env bash

###############################################################################
# Script: run_python_inputfolder_ext_arguments.sh
#
# Description:
#   This script runs a specified Python script on all files with a given
#   extension within an input folder, passing along any additional arguments.
#
# Usage:
#   ./run_python_inputfolder_ext_arguments.sh [--dry-run] <python_script> <input_folder> <extension> [extra_args...]
#
# Example:
#   ./run_python_inputfolder_ext_arguments.sh annotation_counter.py /path/to/folder gb Fpockt# DGsite# ASpock#
#     - Actual run: executes the Python script on each .gb file.
#   ./run_python_inputfolder_ext_arguments.sh --dry-run annotation_counter.py /path/to/folder gb Fpockt# DGsite# ASpock#
#     - Dry run: only prints the commands without execution.
#
# Requirements:
#   - bash shell
#   - python available in PATH
#
# Author: EP
# Date: 2025-06-03
# Version: 1.2
###############################################################################

# Default: execute commands
DRY_RUN=false

# Scan for --dry-run anywhere in arguments, remove it
ARGS=()
for arg in "$@"; do
    if [ "$arg" == "--dry-run" ]; then
        DRY_RUN=true
    else
        ARGS+=("$arg")
    fi
done
set -- "${ARGS[@]}"

# Check if at least three arguments are provided after removing --dry-run
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 [--dry-run] <python_script> <input_folder> <extension> [extra_args...]"
    echo "Example: $0 --dry-run annotation_counter.py /path/to/folder gb Fpockt# DGsite# ASpock#"
    exit 1
fi

# Parse command-line arguments
PYTHON_SCRIPT="$1"
INPUT_FOLDER="$2"
EXTENSION="$3"
shift 3
EXTRA_ARGS=("$@")

# Verify that python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script '$PYTHON_SCRIPT' not found."
    exit 1
fi

# Verify that input folder exists and is a directory
if [ ! -d "$INPUT_FOLDER" ]; then
    echo "Error: Input folder '$INPUT_FOLDER' not found or is not a directory."
    exit 1
fi

# Enable nullglob so that no-match globs expand to empty
shopt -s nullglob

# Loop over all files with the given extension in the input folder
for file in "$INPUT_FOLDER"/*."$EXTENSION"; do
    # Construct command array
    CMD=(python "$PYTHON_SCRIPT" "$file" "${EXTRA_ARGS[@]}")
    # Print the command
    echo "Running: ${CMD[@]}"
    # Execute only if not a dry run
    if [ "$DRY_RUN" != true ]; then
        "${CMD[@]}"
    fi
    echo

done

# Disable nullglob, restore default behavior
shopt -u nullglob
