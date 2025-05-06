#!/usr/bin/env python3
"""
Replace specific text at the start of lines across multiple files.
Usage: {script_name} <input_dir> <output_dir> <ext> <in_text> <out_text>
Example: {script_name} input_dir output_dir txt '     Pocket' '     F_Pock'
"""
import sys
import os
import re

def print_header():
    script = os.path.basename(sys.argv[0])
    print("Replace specific text at the start of lines across multiple files.")
    print(f"Usage: {script} <input_dir> <output_dir> <ext> <in_text> <out_text>")
    print(f"Example: {script} input_dir output_dir txt '     Pocket' '     F_Pock'")
    print()

def main():
    print_header()
    if len(sys.argv) != 6:
        sys.exit(1)

    input_dir, output_dir, ext, in_text, out_text = sys.argv[1:]

    # Validate input_dir exists
    if not os.path.isdir(input_dir):
        print(f"❌ Error: Input directory '{input_dir}' does not exist.")
        sys.exit(1)

    # Validate in_text and out_text
    if len(in_text) != len(out_text):
        print("❌ Error: <in_text> and <out_text> must be the same length.")
        sys.exit(1)
    if in_text.count(' ') != out_text.count(' '):
        print("❌ Error: <in_text> and <out_text> must have the same number of spaces.")
        sys.exit(1)

    # Normalize extension
    ext = ext if ext.startswith('.') else f".{ext}"

    # Prepare output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Dry run preview
    pattern = re.compile(r'^' + re.escape(in_text))
    print(f"🧪 Dry Run Preview (up to 5 matches) in '{input_dir}' for '*{ext}':")
    matches = 0
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(ext):
                with open(os.path.join(root, file), 'r') as f:
                    for line in f:
                        if pattern.match(line):
                            replaced = pattern.sub(out_text, line)
                            print(f"{line.rstrip()} -> {replaced.rstrip()}")
                            matches += 1
                            if matches >= 5:
                                break
                    if matches >= 5:
                        break
        if matches >= 5:
            break
    print()

    # Perform replacements
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(ext):
                infile_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, input_dir)
                target_dir = os.path.join(output_dir, rel_path)
                os.makedirs(target_dir, exist_ok=True)
                outfile_path = os.path.join(target_dir, file)
                print(f"Running: processing '{infile_path}' -> '{outfile_path}'")
                with open(infile_path, 'r') as fin, open(outfile_path, 'w') as fout:
                    for line in fin:
                        fout.write(pattern.sub(out_text, line))

if __name__ == '__main__':
    main()
