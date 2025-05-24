#!/usr/bin/env python3
"""
Extract arbitrary columns from a CSV file in the order given,
using the specified output delimiter.

Usage:
    extract_columns.py [-d DELIM] input.csv col1 [col2 ...]
Example:
    extract_columns.py -d ' ' BACE1.csv canonical_smiles chembl_id > out.txt
"""
import sys, csv, argparse

parser = argparse.ArgumentParser(__doc__)
parser.add_argument('-d','--delimiter', default=',',
                    help="output delimiter (default: comma)")
parser.add_argument('input', help="input CSV file")
parser.add_argument('cols', nargs='+',
                    help="column names to extract, in order")
args = parser.parse_args()

print(f"Running: python3 {sys.argv[0]} -d {args.delimiter!r} {args.input} {' '.join(args.cols)}")

with open(args.input, newline='') as f:
    reader = csv.DictReader(f)
    writer = csv.writer(sys.stdout, delimiter=args.delimiter)
    writer.writerow(args.cols)
    for row in reader:
        writer.writerow([row.get(c, "") for c in args.cols])
