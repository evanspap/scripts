#!/usr/bin/env python3
"""
Split a large file into multiple smaller files with approximately equal number of lines.

Usage: python split_file.py <input_file> <number_of_chunks>

Example: python split_file.py data.txt 6
This will split data.txt into 6 files: data_chunk_001.txt, data_chunk_002.txt, etc.
"""

import sys
import os
from pathlib import Path


def count_lines(filename):
    """Count the total number of lines in a file efficiently."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            count = sum(1 for _ in f)
        return count
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(filename, 'r', encoding='latin-1') as f:
            count = sum(1 for _ in f)
        return count


def split_file(input_file, num_chunks):
    """Split a file into multiple chunks with approximately equal lines."""
    
    # Validate inputs
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    if num_chunks < 2:
        print("Error: Number of chunks must be at least 2.")
        sys.exit(1)
    
    # Count total lines
    total_lines = count_lines(input_file)
    print(f"Total lines in file: {total_lines}")
    
    if total_lines < num_chunks:
        print(f"Warning: File has fewer lines ({total_lines}) than chunks requested ({num_chunks}).")
        num_chunks = total_lines
    
    # Calculate lines per chunk
    lines_per_chunk = total_lines // num_chunks
    remainder = total_lines % num_chunks
    
    print(f"Splitting into {num_chunks} chunks...")
    print(f"Lines per chunk: {lines_per_chunk} (with {remainder} chunks having 1 extra line)")
    
    # Get output file prefix
    input_path = Path(input_file)
    output_prefix = input_path.stem
    output_dir = input_path.parent
    
    # Read and split the file
    chunk_number = 1
    current_chunk_lines = 0
    current_chunk_file = None
    chunk_files = []
    
    try:
        # Open first chunk file
        chunk_filename = output_dir / f"{output_prefix}_chunk_{chunk_number:03d}{input_path.suffix}"
        chunk_files.append(chunk_filename)
        current_chunk_file = open(chunk_filename, 'w', encoding='utf-8')
        
        # Determine lines for this chunk (add 1 to first 'remainder' chunks)
        target_lines = lines_per_chunk + (1 if chunk_number <= remainder else 0)
        
        with open(input_file, 'r', encoding='utf-8') as infile:
            for line_number, line in enumerate(infile, 1):
                current_chunk_file.write(line)
                current_chunk_lines += 1
                
                # Check if current chunk is full
                if current_chunk_lines >= target_lines and chunk_number < num_chunks:
                    current_chunk_file.close()
                    chunk_number += 1
                    current_chunk_lines = 0
                    
                    # Open next chunk file
                    chunk_filename = output_dir / f"{output_prefix}_chunk_{chunk_number:03d}{input_path.suffix}"
                    chunk_files.append(chunk_filename)
                    current_chunk_file = open(chunk_filename, 'w', encoding='utf-8')
                    target_lines = lines_per_chunk + (1 if chunk_number <= remainder else 0)
        
        # Close the last chunk file
        if current_chunk_file:
            current_chunk_file.close()
        
        # Print summary
        print("\nFile split successfully!")
        print("Output files created:")
        for i, chunk_file in enumerate(chunk_files, 1):
            line_count = count_lines(str(chunk_file))
            print(f"  {i}. {chunk_file.name} ({line_count} lines)")
        
    except UnicodeDecodeError:
        # Retry with different encoding
        if current_chunk_file:
            current_chunk_file.close()
        
        # Clean up partial files
        for cf in chunk_files:
            if cf.exists():
                cf.unlink()
        
        print("Error: Could not decode file with UTF-8 encoding. Trying with latin-1...")
        split_file_with_encoding(input_file, num_chunks, 'latin-1')
    
    except Exception as e:
        print(f"Error: {e}")
        # Clean up partial files
        if current_chunk_file:
            current_chunk_file.close()
        for cf in chunk_files:
            if cf.exists():
                cf.unlink()
        sys.exit(1)


def split_file_with_encoding(input_file, num_chunks, encoding):
    """Split a file using specified encoding."""
    
    total_lines = count_lines(input_file)
    lines_per_chunk = total_lines // num_chunks
    remainder = total_lines % num_chunks
    
    input_path = Path(input_file)
    output_prefix = input_path.stem
    output_dir = input_path.parent
    
    chunk_number = 1
    current_chunk_lines = 0
    current_chunk_file = None
    chunk_files = []
    
    try:
        chunk_filename = output_dir / f"{output_prefix}_chunk_{chunk_number:03d}{input_path.suffix}"
        chunk_files.append(chunk_filename)
        current_chunk_file = open(chunk_filename, 'w', encoding=encoding)
        
        target_lines = lines_per_chunk + (1 if chunk_number <= remainder else 0)
        
        with open(input_file, 'r', encoding=encoding) as infile:
            for line in infile:
                current_chunk_file.write(line)
                current_chunk_lines += 1
                
                if current_chunk_lines >= target_lines and chunk_number < num_chunks:
                    current_chunk_file.close()
                    chunk_number += 1
                    current_chunk_lines = 0
                    
                    chunk_filename = output_dir / f"{output_prefix}_chunk_{chunk_number:03d}{input_path.suffix}"
                    chunk_files.append(chunk_filename)
                    current_chunk_file = open(chunk_filename, 'w', encoding=encoding)
                    target_lines = lines_per_chunk + (1 if chunk_number <= remainder else 0)
        
        if current_chunk_file:
            current_chunk_file.close()
        
        print("\nFile split successfully!")
        print("Output files created:")
        for i, chunk_file in enumerate(chunk_files, 1):
            line_count = count_lines(str(chunk_file))
            print(f"  {i}. {chunk_file.name} ({line_count} lines)")
    
    except Exception as e:
        print(f"Error: {e}")
        if current_chunk_file:
            current_chunk_file.close()
        for cf in chunk_files:
            if cf.exists():
                cf.unlink()
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python split_file.py <input_file> <number_of_chunks>")
        print("\nExample:")
        print("  python split_file.py data.txt 6")
        print("\nThis will split data.txt into 6 files named:")
        print("  data_chunk_001.txt")
        print("  data_chunk_002.txt")
        print("  ... and so on")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        num_chunks = int(sys.argv[2])
    except ValueError:
        print(f"Error: '{sys.argv[2]}' is not a valid integer.")
        sys.exit(1)
    
    split_file(input_file, num_chunks)


if __name__ == "__main__":
    main()
