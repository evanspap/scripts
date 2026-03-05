#!/usr/bin/env python3
"""Generate docking .conf files from CSV rows using ligand bounding boxes in PDB files.

Expected workflow:
1) Read an input CSV/TSV with at least PDB code and ligand 3-letter code columns.
2) Open each matching PDB from a bioassembly folder.
3) Select atoms for residues matching the ligand code (resname, case-insensitive).
4) Compute min/max coordinates, center = (min + max) / 2, size = (max - min) + padding.
5) Write one {PDB}.conf file per processed row.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Iterable, Optional

from Bio.PDB import PDBParser


def _normalize_pdb_code(raw: str) -> str:
    code = (raw or "").strip()
    match = re.search(r"[A-Za-z0-9]{4}", code)
    if not match:
        return ""
    return match.group(0).upper()


def _normalize_ligand_code(raw: str) -> str:
    code = (raw or "").strip().upper()
    return re.sub(r"[^A-Z0-9]", "", code)


def _guess_delimiter(path: Path, explicit: Optional[str]) -> str:
    if explicit:
        return "\t" if explicit.lower() == "tab" else explicit
    suffix = path.suffix.lower()
    if suffix == ".tsv":
        return "\t"
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        sample = fh.read(4096)
    tab_count = sample.count("\t")
    comma_count = sample.count(",")
    return "\t" if tab_count > comma_count else ","


def _candidate_pdb_paths(pdb_dir: Path, pdb_code: str) -> Iterable[Path]:
    code_u = pdb_code.upper()
    code_l = pdb_code.lower()
    names = [
        f"{code_u}.pdb",
        f"{code_l}.pdb",
        f"{code_u}.assembly1.pdb",
        f"{code_l}.assembly1.pdb",
        f"{code_u}.bio1.pdb",
        f"{code_l}.bio1.pdb",
        f"pdb{code_l}.ent",
        f"{code_u}.ent",
        f"{code_l}.ent",
    ]
    for name in names:
        yield pdb_dir / name


def _resolve_pdb_file(pdb_dir: Path, pdb_code: str) -> Optional[Path]:
    for candidate in _candidate_pdb_paths(pdb_dir, pdb_code):
        if candidate.exists():
            return candidate

    # Fallback for patterns like 1A4L.assembly1.pdb, 1a4l-*.pdb, etc.
    patterns = [
        f"{pdb_code}*.pdb",
        f"{pdb_code.lower()}*.pdb",
        f"{pdb_code.upper()}*.pdb",
    ]
    for pattern in patterns:
        matches = sorted(pdb_dir.glob(pattern))
        if matches:
            return matches[0]
    return None


def _extract_ligand_atoms(pdb_path: Path, ligand_code: str):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(pdb_path.stem, str(pdb_path))
    atoms = []
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.get_resname().strip().upper() != ligand_code:
                    continue
                for atom in residue.get_atoms():
                    atoms.append(atom)
    return atoms


def _bounds_from_atoms(atoms):
    xs = [atom.coord[0] for atom in atoms]
    ys = [atom.coord[1] for atom in atoms]
    zs = [atom.coord[2] for atom in atoms]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def _format_conf(
    pocket_name: str,
    receptor_value: str,
    center_x: float,
    center_y: float,
    center_z: float,
    size_x: float,
    size_y: float,
    size_z: float,
) -> str:
    return (
        f"# Pocket: {pocket_name}\n"
        f"receptor = {receptor_value}\n\n"
        f"center_x = {center_x:.3f}\n"
        f"center_y = {center_y:.3f}\n"
        f"center_z = {center_z:.3f}\n\n"
        f"size_x = {size_x:.3f}\n"
        f"size_y = {size_y:.3f}\n"
        f"size_z = {size_z:.3f}\n"
    )


def _get_col(row: dict[str, str], idx1: int) -> str:
    key = f"__col_{idx1}"
    return row.get(key, "")


def _make_row_dict(raw_row: list[str]) -> dict[str, str]:
    return {f"__col_{i + 1}": v for i, v in enumerate(raw_row)}


def run(args: argparse.Namespace) -> int:
    csv_path = Path(args.csv).expanduser().resolve()
    pdb_dir = Path(args.pdb_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not csv_path.exists():
        print(f"ERROR: CSV/TSV not found: {csv_path}", file=sys.stderr)
        return 2
    if not pdb_dir.exists():
        print(f"ERROR: PDB directory not found: {pdb_dir}", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)

    delimiter = _guess_delimiter(csv_path, args.delimiter)

    processed = 0
    skipped = 0

    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh, delimiter=delimiter)
        for row_num, raw_row in enumerate(reader, start=1):
            if not raw_row or all(not c.strip() for c in raw_row):
                continue

            # Skip header if requested and this is first row.
            if row_num == 1 and args.has_header:
                continue

            row = _make_row_dict(raw_row)

            pdb_code = _normalize_pdb_code(_get_col(row, args.pdb_col))
            ligand_code = _normalize_ligand_code(_get_col(row, args.ligand_col))

            if not pdb_code or not ligand_code:
                skipped += 1
                print(
                    f"SKIP row {row_num}: invalid pdb/ligand values "
                    f"(pdb='{_get_col(row, args.pdb_col)}', ligand='{_get_col(row, args.ligand_col)}')"
                )
                continue

            pdb_file = _resolve_pdb_file(pdb_dir, pdb_code)
            if pdb_file is None:
                skipped += 1
                print(f"SKIP row {row_num}: PDB file not found for {pdb_code} in {pdb_dir}")
                continue

            atoms = _extract_ligand_atoms(pdb_file, ligand_code)
            if not atoms:
                skipped += 1
                print(f"SKIP row {row_num}: ligand {ligand_code} not found in {pdb_file.name}")
                continue

            min_x, max_x, min_y, max_y, min_z, max_z = _bounds_from_atoms(atoms)

            center_x = (max_x + min_x) / 2.0
            center_y = (max_y + min_y) / 2.0
            center_z = (max_z + min_z) / 2.0
            size_x = (max_x - min_x) + args.padding
            size_y = (max_y - min_y) + args.padding
            size_z = (max_z - min_z) + args.padding

            if args.pocket_col and args.pocket_col > 0:
                pocket_name = _get_col(row, args.pocket_col).strip() or f"{pdb_code}_{ligand_code}"
            else:
                pocket_name = f"{pdb_code}_{ligand_code}"

            receptor_value = args.receptor_template.format(
                pdb=pdb_code,
                ligand=ligand_code,
                pocket=pocket_name,
            )

            conf_text = _format_conf(
                pocket_name=pocket_name,
                receptor_value=receptor_value,
                center_x=center_x,
                center_y=center_y,
                center_z=center_z,
                size_x=size_x,
                size_y=size_y,
                size_z=size_z,
            )

            out_path = out_dir / f"{pdb_code}.conf"
            out_path.write_text(conf_text, encoding="utf-8")
            processed += 1
            print(
                f"OK row {row_num}: {pdb_code} ligand {ligand_code} -> {out_path.name} "
                f"(center={center_x:.3f},{center_y:.3f},{center_z:.3f}; "
                f"size={size_x:.3f},{size_y:.3f},{size_z:.3f})"
            )

    print(f"DONE: wrote {processed} conf file(s), skipped {skipped} row(s).")
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate docking conf files from ligand bounding boxes in PDB structures."
    )
    p.add_argument("--csv", required=True, help="Input CSV/TSV path")
    p.add_argument("--pdb-dir", required=True, help="Folder containing PDB bioassembly files")
    p.add_argument("--out-dir", required=True, help="Output folder for .conf files")

    p.add_argument(
        "--pdb-col",
        type=int,
        default=3,
        help="1-based column index for PDB code (default: 3)",
    )
    p.add_argument(
        "--ligand-col",
        type=int,
        default=4,
        help="1-based column index for ligand 3-letter code (default: 4)",
    )
    p.add_argument(
        "--pocket-col",
        type=int,
        default=0,
        help="Optional 1-based column index for pocket name (default: disabled)",
    )
    p.add_argument(
        "--delimiter",
        default=None,
        help="Delimiter override (e.g. ',' or '\\t' or 'tab'). Auto-detected by default.",
    )
    p.add_argument(
        "--has-header",
        action="store_true",
        help="Treat first row as header and skip it",
    )
    p.add_argument(
        "--padding",
        type=float,
        default=7.0,
        help="Added to each box size axis: (max - min + padding). Default: 7",
    )
    p.add_argument(
        "--receptor-template",
        default="./pdbqt/{pdb}_b_filter_reduce.pdbqt",
        help=(
            "Format template for receptor line. Available tokens: {pdb}, {ligand}, {pocket}. "
            "Default: ./pdbqt/{pdb}_b_filter_reduce.pdbqt"
        ),
    )
    return p


if __name__ == "__main__":
    parser = build_arg_parser()
    sys.exit(run(parser.parse_args()))
