#!/usr/bin/env python3
"""
substitute_tags.py – Fill placeholder tags in a SLURM template and optionally
select suitable resources from `sinfo`.

NEW IN v1.3  (2025‑05‑23)
────────────────────────
* **Automatic ligand count** – If `ligands` is omitted, the script now
  counts `*.pdbqt` files in `indir` and uses that number when estimating
  resources.
* `--param-file` logic unchanged; CLI flags still override everything.

Usage examples
--------------
1) Params via file, write substituted script:

   python substitute_tags.py template.slurm filled.slurm \
          --param-file dock_params.txt

2) Same but *dry run* (print to screen):

   python substitute_tags.py template.slurm --param-file dock_params.txt --dry-run

3) Override just one value at the CLI:

   python substitute_tags.py template.slurm filled.slurm \
          --param-file dock_params.txt --threads 40
"""

import argparse
import math
import os
import re
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

PREFERENCE_ORDER = [
    "medium-96core",
    "short-96core",
    "medium-96core-shared",
    "short-96core-shared",
]

MIN_PER_LIGAND = 0.25  # hours per ligand (15 min)

###############################################################################
# Utility helpers
###############################################################################

def run(cmd: list[str]) -> str:
    """Run a shell command and capture stdout."""
    return subprocess.check_output(cmd, text=True).strip()


def parse_param_file(path: str | Path) -> dict[str, str]:
    """Return dict of key=value pairs from a simple text file."""
    params: dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            params[k.strip().lower()] = v.strip()
    return params


def parse_sinfo() -> dict[str, int]:
    """Return {partition: idle_nodes} parsed from `sinfo` output."""
    out = run(["sinfo", "--noheader", "--Format=partition,stateslong,nodelist"])
    idle: dict[str, int] = {}
    for line in out.splitlines():
        part, state, nodelist = line.split(None, 2)
        if state != "idle":
            continue
        # nodelist may contain ranges like dg[001-008]
        # count nodes roughly by commas + ranges
        count = 0
        for segment in nodelist.split(","):
            if "[" in segment and "]" in segment:
                prefix, rng = segment.split("[")
                rng = rng.rstrip("]")
                start, end = (rng.split("-", 1) + [rng])[:2]
                count += int(end) - int(start) + 1
            else:
                count += 1
        idle[part] = count
    return idle


def choose_resources(idle: dict[str, int], ligands: int, threads: int):
    for queue in PREFERENCE_ORDER:
        if idle.get(queue, 0) == 0:
            continue
        cores_per_node = 96 if "96core" in queue else 40
        # waves = ceil(ligands / (cores_per_node * nodes))
        nodes_avail = idle[queue]
        waves = math.ceil(ligands / (cores_per_node * nodes_avail))
        est_hours = waves * (threads / cores_per_node) * MIN_PER_LIGAND
        walltime = timedelta(hours=min(max(est_hours, 1), 4 if "short" in queue else 12))
        return queue, nodes_avail, str(walltime)
    # Fallback
    q, n = next(iter(idle.items())) if idle else ("debug-40core", 1)
    return q, n, "01:00:00"


def substitute(text: str, mapping: dict[str, str]):
    for k, v in mapping.items():
        text = text.replace(f"__{k}__", str(v))
    return text

###############################################################################
# Main CLI parser
###############################################################################

def main():
    ap = argparse.ArgumentParser(description="Substitute tags in a SLURM template")
    ap.add_argument("template", help="input SLURM template with placeholders")
    ap.add_argument("output", nargs="?", help="output file (omit for --dry-run)")

    # direct flags (override param-file)
    ap.add_argument("--param-file", help="file containing KEY=VALUE pairs")

    ap.add_argument("--indir")
    ap.add_argument("--outdir")
    ap.add_argument("--trg")
    ap.add_argument("--cfg")
    ap.add_argument("--threads", type=int)
    ap.add_argument("--partition")
    ap.add_argument("--nodes", type=int)
    ap.add_argument("--walltime")
    ap.add_argument("--ligands", type=int)

    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # gather parameters: order of precedence → CLI > param-file > default/None
    params: dict[str, str | int | None] = {
        "indir": args.indir,
        "outdir": args.outdir,
        "trg": args.trg,
        "cfg": args.cfg,
        "threads": args.threads,
        "partition": args.partition,
        "nodes": args.nodes,
        "walltime": args.walltime,
        "ligands": args.ligands,
    }

    if args.param_file:
        file_params = parse_param_file(args.param_file)
        for k, v in file_params.items():
            if params.get(k) is None:
                params[k] = v

    # Cast numeric strings → int
    if isinstance(params["threads"], str):
        params["threads"] = int(params["threads"])
    if isinstance(params["nodes"], str):
        params["nodes"] = int(params["nodes"])
    if isinstance(params["ligands"], str):
        params["ligands"] = int(params["ligands"])

    # Validate required params (indir/outdir/trg/cfg)
    missing = [k for k in ("indir", "outdir", "trg", "cfg") if params[k] is None]
    if missing:
        sys.exit(f"Missing required params: {', '.join(missing)}")

    # If ligands not provided, count *.pdbqt in indir
if params["ligands"] is None:
    try:
        from glob import glob
        params["ligands"] = len(glob(os.path.join(os.path.expanduser(params["indir"]), "*.pdbqt")))
    except OSError:
        params["ligands"] = 7000  # fallback

# Resource auto‑selection
if not (params["partition"] and params["nodes"] and params["walltime"]):
    idle = parse_sinfo()
    ligands = params["ligands"] or 7000
    part, nod, wtime = choose_resources(idle, ligands, params["threads"] or 96)
    params["partition"], params["nodes"], params["walltime"] = part, nod, wtime(idle, ligands, params["threads"] or 96)
        params["partition"], params["nodes"], params["walltime"] = part, nod, wtime

    mapping = {
        "INDIR": Path(params["indir"]).expanduser(),
        "OUTDIR": Path(params["outdir"]).expanduser(),
        "TRGTAG": params["trg"],
        "CONFIG": Path(params["cfg"]).expanduser(),
        "THREADS": params["threads"] or 96,
        "PARTITION": params["partition"],
        "NODES": params["nodes"],
        "WALLTIME": params["walltime"],
    }

    filled = substitute(Path(args.template).read_text(), mapping)

    if args.dry_run or args.output is None:
        print(filled)
    else:
        Path(args.output).write_text(filled)
        print(f"Running: sbatch {args.output}")

if __name__ == "__main__":
    main()
