#!/usr/bin/env bash
###############################################################################
# dock_adv_parallel.sh
#
# Dock every *.pdbqt ligand found in <input_dir> with AutoDock Vina, in parallel.
#   • Skips a ligand when its corresponding output file already exists.
#   • Accepts input/output directories, target tag, Vina config file,
#     and (optionally) the number of parallel jobs from the command line.
#   • Prints the exact Vina command it will run as:  Running: …
#   • Shows a running progress bar courtesy of GNU parallel.
#
# ─────────────────────────────────────────────────────────────────────────────
# Usage:
#   ./dock_adv_parallel.sh <input_dir> <output_dir> <target_id> <config_file> [threads]
#
# Example:
#   ./dock_adv_parallel.sh ./in2 ./out_adv CFTR ./conf/conf3.txt 40
#
# Dry-run (no docking, just show the commands that *would* be executed):
#   ./dock_adv_parallel.sh --dry-run ./in2 ./out_adv CFTR ./conf/conf3.txt 40
###############################################################################

set -euo pipefail

###############################################################################
# 1. Parse arguments
###############################################################################
dry_run=false
if [[ "$1" == "--dry-run" ]]; then
    dry_run=true
    shift
fi

if [[ $# -lt 4 ]]; then
    grep -E '^#( |\t)' "$0" | sed -n '2,35p'    # header, usage, example
    exit 1
fi

indir="$(readlink -f "$1")"
outdir="$(readlink -f "$2")"
trg="$3"
cfg="$(readlink -f "$4")"
threads="${5:-$(nproc)}"

###############################################################################
# 2. House-keeping
###############################################################################
[[ -d "$indir"  ]] || { echo "ERROR: Input dir $indir not found";  exit 1; }
[[ -f "$cfg"    ]] || { echo "ERROR: Config file $cfg not found";  exit 1; }
mkdir -p "$outdir"

echo "Input ligands : $indir"
echo "Output dir    : $outdir"
echo "Target tag    : $trg"
echo "Config file   : $cfg"
echo "Threads       : $threads"
echo "Dry-run       : $dry_run"
echo "Start         : $(date)"
echo "───────────────────────────────────────────────────────────────"

###############################################################################
# 3. Define the docking function that GNU parallel will invoke
###############################################################################
dock_one() {
    lig="$1"
    base=$(basename "$lig" .pdbqt)
    out_file="$outdir/${base}_${trg}.pdbqt"

    if [[ -f "$out_file" ]]; then
        echo "Skipping (exists): $out_file"
        return
    fi

    cmd="vina --config \"$cfg\" --ligand \"$lig\" --out \"$out_file\" --spacing 0.1"
    echo "Running: $cmd"
    if [[ "$dry_run" == "false" ]]; then
        eval $cmd
    fi
}
export -f dock_one
export outdir trg cfg dry_run

###############################################################################
# 4. Find ligands and launch parallel jobs
###############################################################################
find "$indir" -maxdepth 1 -name '*.pdbqt' | \
    parallel --jobs "$threads" --bar --eta dock_one {}

###############################################################################
# 5. Finish
###############################################################################
echo "Done          : $(date)"
