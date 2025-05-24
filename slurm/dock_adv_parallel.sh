#!/usr/bin/env bash
###############################################################################
# dock_adv_parallel.sh
#
# Dock every *.pdbqt ligand in <input_dir> with AutoDock Vina **in parallel**.
#
#   • Skips a ligand if its output file already exists (idempotent re‑runs).
#   • Accepts an **optional** `--dry-run` flag and an **optional**
#     `--hostfile <file>` pair so the script can operate either on a single
#     node *or* spread work across a multi‑node Slurm allocation.
#   • Prints each executed Vina command prefixed with `Running:` (for logs).
#   • Shows a live progress bar courtesy of GNU parallel.
#
# ─────────────────────────────────────────────────────────────────────────────
# Usage
#   dock_adv_parallel.sh [--dry-run] <input_dir> <output_dir> <target_tag>
#                        <config_file> <threads> [--hostfile <file>]
#
# Example (single node, 96 threads):
#   dock_adv_parallel.sh ./in2 ./out CFTR conf.txt 96
#
# Example (multi‑node Slurm job with hostlist.$SLURM_JOB_ID):
#   dock_adv_parallel.sh --hostfile hostlist.$SLURM_JOB_ID \
#                        ./in2 ./out CFTR conf.txt 96
###############################################################################
set -euo pipefail

######################## 1. Parse flags  ######################################

dry_run=false
hostfile=""

while [[ $# -gt 0 && "$1" == --* ]]; do
    case "$1" in
        --dry-run)   dry_run=true;   shift ;;
        --hostfile)  hostfile="$2"; shift 2 ;;
        --help|-h)
            grep -E '^#' "$0" | head -n 50 | sed 's/^# //'; exit 0 ;;
        *) echo "ERROR: unknown option $1"; exit 1 ;;
    esac
done

######################## 2. Positional args ###################################

if [[ $# -lt 5 ]]; then
    echo "\nERROR: required arguments missing. Run with --help for usage."; exit 1
fi

indir="$(readlink -f "$1")"
outdir="$(readlink -f "$2")"
trg="$3"
cfg="$(readlink -f "$4")"
threads="$5"   # **integer** cores per node

######################## 3. House‑keeping #####################################

[[ -d "$indir" ]] || { echo "ERROR: input dir $indir not found";  exit 1; }
[[ -f "$cfg"   ]] || { echo "ERROR: config file $cfg not found"; exit 1; }
mkdir -p "$outdir"

cat <<EOF
Input ligands : $indir
Output dir    : $outdir
Target tag    : $trg
Config file   : $cfg
Threads/node  : $threads
Hostfile      : ${hostfile:-<none>}  
Dry‑run       : $dry_run
Start         : $(date)
───────────────────────────────────────────────────────────────
EOF

######################## 4. Docking worker ###################################

dock_one() {
    lig="$1"
    base=$(basename "$lig" .pdbqt)
    out_file="$outdir/${base}_${trg}.pdbqt"

    if [[ -f "$out_file" ]]; then
        echo "Skipping (exists): $out_file"; return
    fi

    cmd="vina --config \"$cfg\" --ligand \"$lig\" --out \"$out_file\""
    echo "Running: $cmd"
    [[ "$dry_run" == true ]] || eval $cmd
}
export -f dock_one
export outdir trg cfg dry_run

######################## 5. Launch GNU parallel ################################

lig_list=$(find "$indir" -maxdepth 1 -name '*.pdbqt' | sort)

if [[ -n "$hostfile" ]]; then
    # Multi‑node: use parallel's built‑in Slurm support so each task is wrapped
    # with srun and distributed across every node in the allocation.
    echo "Dispatch mode : SLURM multi‑node (hostfile $hostfile)"
    printf "%s\n" "$lig_list" | \
      parallel --slurm --bar --eta -j "$threads" dock_one {}
else
    # Single node: classic fork‑within‑node parallelism.
    echo "Dispatch mode : local fork (single node)"
    printf "%s\n" "$lig_list" | \
      parallel -j "$threads" --bar --eta dock_one {}
fi

######################## 6. Finish ############################################
echo "Done           : $(date)"
