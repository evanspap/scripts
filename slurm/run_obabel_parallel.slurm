#!/bin/bash
#SBATCH --nodes=1
#SBATCH -p short-40core
#SBATCH --mem=175G
#SBATCH --time=04:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --job-name=obabel_parallel
#SBATCH --output=obabel_%j.out
#SBATCH --error=obabel_%j.err

###############################################################################
# SLURM batch script: Convert every .smi file in an input directory to .pdbqt   
# in a dedicated OUTPUT directory, using Open Babel + GNU Parallel.            
# It prints a one‑line percentage update whenever another 1 % of the total     
# files have finished converting ‑‑ robust even when the usual --bar output    
# is swallowed by Slurm.                                                       
#                                                                              
# USAGE                                                                        
#   sbatch run_obabel_parallel.slurm <INPUT_DIR> [OUTPUT_DIR]                  
#                                                                              
# EXAMPLE                                                                      
#   sbatch run_obabel_parallel.slurm \                                         
#     /gpfs/projects/DengYasarGroup/GENOVA/Docking_BACE1/Compounds/SMI         
#                                                                              
# NOTES                                                                        
#   * Requires modules: openbabel, gnu-parallel/6.0                            
#   * OUTPUT_DIR defaults to <INPUT_DIR>/PDBQT if not provided.                
###############################################################################

# --------------------------- Parse Arguments ---------------------------------
if [[ $# -lt 1 ]]; then
  echo "Convert every *.smi in INPUT_DIR to *.pdbqt in OUTPUT_DIR (parallel)."
  echo "Usage:   sbatch $(basename "$0") <INPUT_DIR> [OUTPUT_DIR]"
  echo "Example: sbatch $(basename "$0") /path/to/SMI /path/to/out/PDBQT"
  exit 1
fi

INPUT_DIR=$(realpath "$1")
OUTPUT_DIR=${2:-"${INPUT_DIR%/}/PDBQT"}
OUTPUT_DIR=$(realpath -m "$OUTPUT_DIR")

# --------------------------- Environment -------------------------------------
module load gnu-parallel/6.0
module load openbabel

# Make sure OUTPUT_DIR exists
mkdir -p "$OUTPUT_DIR" || { echo "Cannot create $OUTPUT_DIR"; exit 2; }

# Default SLURM_CPUS_PER_TASK if not exported
: "${SLURM_CPUS_PER_TASK:=40}"

# --------------------------- Gather Input ------------------------------------
mapfile -t SMIFILES < <(find "$INPUT_DIR" -maxdepth 1 -type f -name '*.smi' | sort)
NFILES=${#SMIFILES[@]}
if (( NFILES == 0 )); then
  echo "No .smi files found in $INPUT_DIR. Exiting."; exit 3
fi

PARALLEL_J=$(( NFILES < SLURM_CPUS_PER_TASK ? NFILES : SLURM_CPUS_PER_TASK ))

echo "Found $NFILES .smi files -> $OUTPUT_DIR (using $PARALLEL_J parallel jobs)."

echo "Launching Open Babel conversions …"

# --------------------------- Launch Parallel Jobs ----------------------------
parallel -j "$PARALLEL_J" \
  obabel -ismi {} --gen3d best -p --partialcharge eem -O "$OUTPUT_DIR"/{/.}.pdbqt ::: "${SMIFILES[@]}" &
PAR_PID=$!

# --------------------------- Progress Monitor --------------------------------
LAST_PERCENT=-1
while kill -0 "$PAR_PID" 2>/dev/null; do
  DONE=$(find "$OUTPUT_DIR" -type f -name '*.pdbqt' | wc -l)
  PERCENT=$(( 100 * DONE / NFILES ))
  if (( PERCENT > LAST_PERCENT )); then
    printf '%(%Y-%m-%d %H:%M:%S)T  Completed %d / %d  (%d%%)\n' -1 "$DONE" "$NFILES" "$PERCENT"
    LAST_PERCENT=$PERCENT
  fi
  sleep 5
done
wait "$PAR_PID"

printf '%(%Y-%m-%d %H:%M:%S)T  All conversions finished (%d files).\n' -1 "$NFILES"
