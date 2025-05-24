#!/usr/bin/env python3
"""
substitute_tags.py – Fill placeholder tags in a SLURM template and optionally
select suitable resources from `sinfo`.

NEW IN v1.4  (2025‑05‑23)
────────────────────────
* **Fixes indentation bug** that caused an `IndentationError`.
* **Cleans duplicate code** and streamlines auto‑resource selection.
* Counts `*.pdbqt` files in `indir` when `ligands` not supplied.
* `--param-file` remains available; CLI flags still override.
"""

from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys
from datetime import timedelta
from glob import glob
from pathlib import Path

# queues in order of preference for docking jobs
PREFERENCE_ORDER = [
    "short-96core",          # fastest queue if idle nodes available
    "medium-96core",
    "short-96core-shared",
    "medium-96core-shared",
]

# minutes a single ligand typically needs on one core
MINUTES_PER_LIGAND = 15

###############################################################################
# Utility helpers
###############################################################################

def run(cmd: list[str]) -> str:
    """Run a shell command and capture its stdout (stripped)."""
    return subprocess.check_output(cmd, text=True).strip()


def parse_param_file(path: str | Path) -> dict[str, str]:
    """Parse KEY=VALUE lines (shell‑style) into a dict."""
    params: dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            params[k.strip().lower()] = v.strip()
    return params


def parse_sinfo() -> dict[str, int]:
    """Return a {partition: idle_nodes} mapping from `sinfo`."""
    out = run(["sinfo", "--noheader", "--Format=partition,stateslong,nodelist"])
    idle: dict[str, int] = {}
    for row in out.splitlines():
        part, state, nodelist = row.split(None, 2)
        if state != "idle":
            continue
        # crude count of nodes in the bracket notation
        count = 0
        for seg in nodelist.split(","):
            if "[" in seg and "]" in seg:
                rng = seg.split("[")[1].rstrip("]")
                start, end = (rng.split("-", 1) + [rng])[:2]
                count += int(end) - int(start) + 1
            else:
                count += 1
        idle[part] = count
    return idle


def choose_resources(idle: dict[str, int], ligands: int, threads: int):
    """Pick (partition, nodes, walltime) based on current idle nodes."""
    for queue in PREFERENCE_ORDER:
        nodes_idle = idle.get(queue, 0)
        if nodes_idle == 0:
            continue
        cores_per_node = 96 if "96core" in queue else 40
        waves = math.ceil(ligands / (cores_per_node * nodes_idle))
        est_hours = waves * (MINUTES_PER_LIGAND / 60)
        # cap walltime within each queue's maximum (4 h for short, 12 h for medium)
        max_hours = 4 if "short" in queue else 12
        walltime = str(timedelta(hours=min(max(est_hours, 1), max_hours)))
        return queue, nodes_idle, walltime
    # default fallback
    return "debug-40core", 1, "01:00:00"


def substitute(text: str, mapping: dict[str, str]):
    for key, val in mapping.items():
        text = text.replace(f"__{key}__", str(val))
    return text

###############################################################################
# Main program
###############################################################################

def main():
    ap = argparse.ArgumentParser(description="Substitute tags in a SLURM template")
    ap.add_argument("template", help="input SLURM template with placeholders")
    ap.add_argument("output", nargs="?", help="output file (defaults to STDOUT with --dry-run)")

    ap.add_argument("--param-file", help="file with KEY=VALUE lines (shell style)")

    # individual overrides
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

    # initialise param dict
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

    # merge param-file (if any)
    if args.param_file:
        for k, v in parse_param_file(args.param_file).items():
            params.setdefault(k, v)

    # convert numeric strings → int
    for key in ("threads", "nodes", "ligands"):
        if isinstance(params[key], str):
            params[key] = int(params[key])

    # required
    missing = [k for k in ("indir", "outdir", "trg", "cfg") if params[k] is None]
    if missing:
        sys.exit("Missing required params: " + ", ".join(missing))

    # defaults
    if params["threads"] is None:
        params["threads"] = 96

    # count ligands automatically if not provided
    if params["ligands"] is None:
        try:
            pattern = os.path.join(os.path.expanduser(params["indir"]), "*.pdbqt")
            params["ligands"] = len(glob(pattern))
        except OSError:
            params["ligands"] = 7000

    # choose resources if any of the trio missing
    if not (params["partition"] and params["nodes"] and params["walltime"]):
        idle = parse_sinfo()
        part, nod, wtime = choose_resources(idle, int(params["ligands"]), int(params["threads"]))
        params.setdefault("partition", part)
        params.setdefault("nodes", nod)
        params.setdefault("walltime", wtime)

    # build mapping for substitution
    mapping = {
        "INDIR": Path(params["indir"]).expanduser(),
        "OUTDIR": Path(params["outdir"]).expanduser(),
        "TRGTAG": params["trg"],
        "CONFIG": Path(params["cfg"]).expanduser(),
        "THREADS": params["threads"],
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
