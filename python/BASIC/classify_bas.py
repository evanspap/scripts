"""
BAS File Classifier
====================
This script takes a list of file paths (one per line) from a .list file,
and for each file determines whether it is ASCII (plain text) or binary
(tokenized or otherwise).

Usage:
  python classify_bas.py BAS.list

Requirements:
  The .list file should contain absolute or relative paths to .BAS files.

Author: Your Name
Date: 2025-04-20
"""

import sys
from pathlib import Path

# Heuristic to determine if a file is ASCII or binary
def classify_bas_file(file_path: str) -> str:
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(512)
            # ASCII = mostly printable characters or common control chars
            ascii_score = sum((32 <= b <= 126 or b in (9, 10, 13)) for b in chunk)
            ratio = ascii_score / len(chunk) if chunk else 0
            return "ASCII" if ratio > 0.95 else "Binary"
    except Exception:
        return "Missing"

def main():
    if len(sys.argv) < 2:
        print("Usage: python classify_bas.py BAS.list")
        sys.exit(1)

    list_file = Path(sys.argv[1])
    if not list_file.is_file():
        print(f"List file not found: {list_file}")
        sys.exit(1)

    with open(list_file, "r", encoding="utf-8", errors="ignore") as f:
        files = [line.strip() for line in f if line.strip()]

    results = [(f, classify_bas_file(f)) for f in files]

    print("\nFile Classification:\n---------------------")
    for fname, ftype in results:
        print(f"{fname:60} {ftype}")

if __name__ == "__main__":
    main()
