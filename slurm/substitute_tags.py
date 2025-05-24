#!/usr/bin/env python3
"""
substitute_tags.py – Fill the placeholder tags inside a SLURM template and
(optional) choose sensible resources based on current idle nodes.

Tags recognised in the template (enclosed by double underscores):
    __INDIR__     – input ligand directory
    __OUTDIR__    – output directory for docked ligands
    __TRGTAG__    – string appended to each output file name
    __CONFIG__    – path to Vina conf file
    __THREADS__   – CPU cores per node (also passed to dock_adv_parallel.sh)
    __PARTITION__ – Slurm queue name
    __NODES__     – number of nodes to request
    __WALLTIME__  – wall‑clock limit (HH:MM:SS)

Usage
-----
Dry‑run (just print substituted script to STDOUT):

    python substitute_tags.py template.slurm --indir /path/in2 --outdir /path/out \
        --trg CFTR --cfg ./conf/conf3.txt --threads 96 --dry‑run

Create a ready‑to‑submit file, auto‑selecting idle nodes:

    python substitute_tags.py template.slurm dock_submit.slurm \
        --indir /path/in2 --outdir /path/out --trg CFTR \
        --cfg ./conf/conf3.txt --ligands 7000

If --partition / --nodes / --walltime are omitted the script runs `sinfo` and
picks the most suitable 96‑core queue with idle nodes (prefers medium‑96core,
then short‑96core, etc.).
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

# default minutes per ligand for scheduling estimate
MIN_PER_LIGAND = 0.25  # 15 min = 0.25 h

def run(cmd: list[str]) -> str:
    """Run a shell command and return stdout as text."""
    return subprocess.check_output(cmd, text=True).strip()


def parse_sinfo() -> dict[str, int]:
    """Return {partition: idle_nodes} from `sinfo | grep idle`."""
    out = run(["sinfo"])
    idle = {}
    for line in out.splitlines():
        if " idle " not in line:
            continue
        parts = line.split()
        part = parts[0]
        nodes_idle = int(parts[7])  # e.g. '5' in column before node list
        idle[part] = nodes_idle
    return idle


def choose_resources(idle: dict[str, int], ligands: int, threads: int):
    """Pick partition, nodes, walltime based on need and availability."""
    for queue in PREFERENCE_ORDER:
        if queue in idle and idle[queue] > 0:
            cores_per_node = 96 if "96core" in queue else 40
            waves = math.ceil(ligands / (idle[queue] * cores_per_node))
            est_hours = waves * MIN_PER_LIGAND
            walltime = timedelta(hours=min(max(est_hours, 1), 12))
            return queue, idle[queue], str(walltime)
    # fallback first available idle partition
    if idle:
        q, n = next(iter(idle.items()))
        walltime = "12:00:00"
        return q, min(n, 4), walltime
    raise RuntimeError("No idle nodes found! Cannot choose resources.")


def substitute(text: str, mapping: dict[str, str]):
    for key, val in mapping.items():
        text = text.replace(f"__{key}__", str(val))
    return text


def main():
    ap = argparse.ArgumentParser(description="Substitute tags in SLURM template")
    ap.add_argument("template", help="input SLURM template with placeholders")
    ap.add_argument("output", nargs="?", help="output file (omit for --dry-run)")

    ap.add_argument("--indir", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--trg", required=True)
    ap.add_argument("--cfg", required=True)
    ap.add_argument("--threads", type=int, default=96)
    ap.add_argument("--partition")
    ap.add_argument("--nodes", type=int)
    ap.add_argument("--walltime")
    ap.add_argument("--ligands", type=int, help="number of ligands to schedule")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # Auto‑choose resources if not provided
    partition = args.partition
    nodes = args.nodes
    walltime = args.walltime

    if not (partition and nodes and walltime):
        idle = parse_sinfo()
        if args.ligands is None:
            print("[WARN] --ligands not given; assuming 7000 for estimate", file=sys.stderr)
            ligands = 7000
        else:
            ligands = args.ligands
        partition, nodes, walltime = choose_resources(idle, ligands, args.threads)
        print(f"Selected resources: partition={partition} nodes={nodes} walltime={walltime}")

    mapping = {
        "INDIR": Path(args.indir).expanduser(),
        "OUTDIR": Path(args.outdir).expanduser(),
        "TRGTAG": args.trg,
        "CONFIG": Path(args.cfg).expanduser(),
        "THREADS": args.threads,
        "PARTITION": partition,
        "NODES": nodes,
        "WALLTIME": walltime,
    }

    template_text = Path(args.template).read_text()
    filled = substitute(template_text, mapping)

    if args.dry_run or args.output is None:
        print(filled)
    else:
        Path(args.output).write_text(filled)
        print(f"Running: sbatch {args.output}")

if __name__ == "__main__":
    main()
