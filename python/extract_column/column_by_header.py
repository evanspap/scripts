#!/home/geras/python_envs/data_env/bin/python
"""
Script: column_by_header.py
Summary:
    Extract a single column from a CSV or TSV file by matching its header name
    and print the column values to standard output.

Author:
    Project maintainer

Version:
    1.0.0

Dependencies:
    - Python 3
    - pandas

Arguments:
    input_file   Path to the input CSV or TSV file.
    header       Column header to extract.
    --separator  Optional delimiter override. If omitted, CSV/TSV is
                 auto-detected from the file extension.

Output:
    Writes the selected column to standard output without the header row or
    index column.

Example usage:
    python column_by_header.py data.csv compound_id
    python column_by_header.py data.tsv smiles
    python column_by_header.py data.txt score --separator "|"
"""

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a CSV/TSV column to standard output by header name."
    )
    parser.add_argument("input_file", help="Path to the input CSV or TSV file.")
    parser.add_argument("header", help="Column header to extract.")
    parser.add_argument(
        "--separator",
        "-s",
        default=None,
        help="Optional delimiter. If omitted, CSV/TSV is auto-detected.",
    )
    return parser.parse_args()


def load_table(input_path: Path, separator: str | None):
    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'pandas'. Install it with: pip install -r requirements.txt"
        ) from exc

    if not input_path.exists():
        raise FileNotFoundError(f"Input file was not found: {input_path}")

    if separator is not None:
        return pd.read_csv(input_path, sep=separator)

    suffix = input_path.suffix.lower()
    if suffix == ".tsv":
        return pd.read_csv(input_path, sep="\t")

    return pd.read_csv(input_path)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_file)

    try:
        dataframe = load_table(input_path, args.separator)
    except Exception as exc:
        print(f"Failed to read input file: {exc}", file=sys.stderr)
        return 1

    if args.header not in dataframe.columns:
        print(
            f"Header '{args.header}' was not found. Available headers: "
            f"{', '.join(map(str, dataframe.columns))}",
            file=sys.stderr,
        )
        return 1

    column = dataframe[args.header]
    column.to_csv(sys.stdout, index=False, header=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
