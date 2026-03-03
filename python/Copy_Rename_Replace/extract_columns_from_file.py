#!/usr/bin/env python3
"""
===============================================================================
Script Name : extract_columns_from_csv.py
Author      : Evangelos Papadopoulos
Version     : 1.1.0
License     : MIT License
Date        : 2026-02-23
===============================================================================

Description
-----------
Robust CSV column extractor supporting multiple arbitrary columns
in user-defined order. Uses Python's built-in csv module for
correct handling of quoted fields and embedded delimiters.

Features
--------
- Extract one or more columns by header name
- Preserve arbitrary column order
- Optional inclusion/exclusion of header in output
- Configurable input delimiter
- Configurable output delimiter
- Memory-efficient streaming (suitable for large files)
- UTF-8 safe

Usage
-----

Basic usage (multiple columns):

    python extract_columns_from_csv.py input.csv Smiles Name

Custom output delimiter (space):

    python extract_columns_from_csv.py input.csv Smiles Name \
        --output-delimiter ' '

Include header in output (default behavior):

    python extract_columns_from_csv.py input.csv Smiles Name

Exclude header:

    python extract_columns_from_csv.py input.csv Smiles Name \
        --no-header

Custom input delimiter (e.g., TSV file):

    python extract_columns_from_csv.py input.tsv Smiles Name \
        --input-delimiter '\t'

Write to file:

    python extract_columns_from_csv.py input.csv Smiles Name \
        -o output.txt

Exit Codes
----------
0  Success
1  Column not found
2  File error

===============================================================================
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
===============================================================================
"""

import argparse
import csv
import sys
from pathlib import Path


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extract one or more columns from a CSV file by header name."
    )

    parser.add_argument(
        "input_file",
        type=str,
        help="Path to input CSV file"
    )

    parser.add_argument(
        "columns",
        nargs='+',
        help="Column names to extract, in desired order"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Optional output file (default: stdout)"
    )

    parser.add_argument(
        "--input-delimiter",
        type=str,
        default=",",
        help="Input CSV delimiter (default: ',')"
    )

    parser.add_argument(
        "--output-delimiter",
        type=str,
        default=",",
        help="Output delimiter (default: ',')"
    )

    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Do NOT write header row in output"
    )

    return parser.parse_args()


def extract_columns(input_path, columns, output_path=None,
                    input_delimiter=",", output_delimiter=",",
                    include_header=True):

    try:
        infile = open(input_path, newline="", encoding="utf-8")
    except Exception as e:
        print(f"ERROR: Cannot open file '{input_path}': {e}", file=sys.stderr)
        sys.exit(2)

    reader = csv.DictReader(infile, delimiter=input_delimiter)

    if reader.fieldnames is None:
        print("ERROR: Could not detect header row.", file=sys.stderr)
        sys.exit(2)

    missing = [c for c in columns if c not in reader.fieldnames]
    if missing:
        print(
            "ERROR: The following columns were not found:\n  - "
            + "\n  - ".join(missing)
            + "\n\nAvailable columns:\n  - "
            + "\n  - ".join(reader.fieldnames),
            file=sys.stderr
        )
        sys.exit(1)

    if output_path:
        outfile = open(output_path, "w", encoding="utf-8", newline="")
    else:
        outfile = sys.stdout

    writer = csv.writer(outfile, delimiter=output_delimiter)

    if include_header:
        writer.writerow(columns)

    for row in reader:
        writer.writerow([row.get(c, "") for c in columns])

    infile.close()
    if output_path:
        outfile.close()


def main():
    args = parse_arguments()

    extract_columns(
        input_path=args.input_file,
        columns=args.columns,
        output_path=args.output,
        input_delimiter=args.input_delimiter,
        output_delimiter=args.output_delimiter,
        include_header=not args.no_header
    )


if __name__ == "__main__":
    main()
