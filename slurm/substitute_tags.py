#!/usr/bin/env python3
"""
substitute_tags.py  –  Fill __TAG__ placeholders in a SLURM template file.

Version 1.8  · 2025‑05‑23
────────────────────────
* Robust `parse_sinfo()` using only universally‑supported format codes.
* Auto‑count ligands ( *.pdbqt ) when `ligands` param omitted.
* Optional param‑file with KEY=VALUE pairs; CLI flags override file.
* Dry‑run prints substituted template to STDOUT.
"""

import argparse
import os
import re
import subprocess
import sys
from glob import glob

# ------------------------ Helpers ------------------------ #

def parse_param_file(path):
    vals = {}
    with open(path) as fh:
        for line in fh:
            line = line.split('#', 1)[0].strip()  # strip comments
            if not line:
                continue
            if '=' not in line:
                continue
            k, v = map(str.strip, line.split('=', 1))
            vals[k.lower()] = v
    return vals


def parse_sinfo():
    """Return dict {partition: idle_nodes}. Safe if sinfo unavailable."""
    try:
        out = subprocess.check_output(
            ["sinfo", "-h", "-t", "idle", "-o", "%P %D"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return {}

    idle = {}
    for row in out.strip().splitlines():
        if not row.strip():
            continue
        # Expect two fields: partition (* may be suffixed), #idle nodes
        parts = row.split(None, 1)
        if len(parts) != 2:
            continue
        part, n_nodes = parts
        part = part.rstrip('*')  # remove star on default partition
        try:
            idle[part] = int(n_nodes)
        except ValueError:
            continue
    return idle


def choose_resources(idle, ligands):
    """Return (partition, nodes, walltime, cores_per_node)."""
    # Candidate lists ordered by preference
    ordering_96 = [
        ("short-96core", 4, "04:00:00"),
        ("medium-96core", 6, "12:00:00"),
        ("long-96core", 6, "48:00:00"),
    ]
    ordering_40 = [
        ("short-40core", 4, "04:00:00"),
        ("medium-40core", 6, "12:00:00"),
        ("long-40core", 6, "48:00:00"),
    ]

    def _pick(order):
        for part, min_nodes, max_wall in order:
            if idle.get(part, 0) >= min_nodes:
                nodes = min(idle[part], 8 if part.startswith("short") else 16)
                cores = 96 if "96core" in part else 40
                est_hours = int((ligands / (nodes * cores) * 0.30) + 1)
                est_hours = max(1, est_hours)
                wall = f"{est_hours:02d}:00:00"
                # cap by queue max
                if _time_to_hours(wall) > _time_to_hours(max_wall):
                    wall = max_wall
                return part, nodes, wall, cores
        return None

    def _time_to_hours(t):
        h, m, s = map(int, t.split(":"))
        return h + m/60 + s/3600

    choice = _pick(ordering_96)
    if choice is None:
        choice = _pick(ordering_40)
    if choice is None:
        # fallback to any idle partition with most nodes
        if idle:
            part = max(idle, key=idle.get)
            nodes = idle[part]
            cores = 96 if "96core" in part else 40
            wall = "08:00:00"
            return part, nodes, wall, cores
        # No idle info
        return "medium-96core", 6, "12:00:00", 96
    return choice


# ------------------------ Main ------------------------ #

def main():
    ap = argparse.ArgumentParser(description="Substitute __TAG__ placeholders in a SLURM template.")
    ap.add_argument("template", help="Input SLURM template file (with tags)")
    ap.add_argument("output", nargs="?", help="Output file to write (omit for stdout)")

    # Param acquisition
    ap.add_argument("--param-file")
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

    params = {
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

    # Merge param-file (if any)
    if args.param_file:
        file_vals = parse_param_file(args.param_file)
        for k, v in file_vals.items():
            if params.get(k) is None:
                params[k] = v

    # Convert numeric strings → int
    for key in ("threads", "nodes", "ligands"):
        if isinstance(params[key], str) and params[key].isdigit():
            params[key] = int(params[key])

    # Auto‑count ligands if still None
    if params["ligands"] is None and params["indir"]:
        try:
            params["ligands"] = len(glob(os.path.join(os.path.expanduser(params["indir"]), "*.pdbqt")))
        except OSError:
            params["ligands"] = 7000
    if params["ligands"] is None:
        params["ligands"] = 7000

    # Auto resource select if any of (partition,nodes,walltime) unset
    if not (params["partition"] and params["nodes"] and params["walltime"]):
        idle = parse_sinfo()
        part, nod, wall, corespn = choose_resources(idle, params["ligands"])
        if params["partition"] is None:
            params["partition"] = part
        if params["nodes"] is None:
            params["nodes"] = nod
        if params["walltime"] is None:
            params["walltime"] = wall
        if params["threads"] is None:
        params["threads"] = 96 if "96core" in params["partition"] else 40

    # Read template
    with open(args.template) as fh:
        text = fh.read()

    # Substitutions
    # Map param‑key → placeholder(s) in template
    tagmap = {
        "indir": "INDIR",
        "outdir": "OUTDIR",
        "trg": "TRGTAG",      # template uses __TRGTAG__
        "cfg": "CONFIG",       # template uses __CONFIG__
        "threads": "THREADS",
        "partition": "PARTITION",
        "nodes": "NODES",
        "walltime": "WALLTIME",
    }

    for key, value in params.items():
        if key not in tagmap or value is None:
            continue
        text = text.replace(f"__{tagmap[key]}__", str(value))

    if args.dry_run or args.output is None:
        sys.stdout.write(text)
    else:
        with open(args.output, "w") as out:
            out.write(text)
        print(f"Filled template written to {args.output}")

if __name__ == "__main__":
    main()
