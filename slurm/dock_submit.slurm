#!/usr/bin/env bash
###############################################################################
# dock_submit.slurm  –  parallel docking of ~7000 ligands on Seawulf‑Milan
#
# Template with placeholder tags to be filled by substitute_tags.py
###############################################################################
#SBATCH --job-name=dock7000
#SBATCH --partition=__PARTITION__
#SBATCH --nodes=__NODES__
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=__THREADS__
#SBATCH --time=__WALLTIME__
#SBATCH --mem=0
#SBATCH --output=dock_%j.out
#SBATCH --error=dock_%j.err

module load gnu-parallel/6.0
module load vina/1.2.5

export indir=__INDIR__
export outdir=__OUTDIR__
export trg=__TRGTAG__
export cfg=__CONFIG__
threads=__THREADS__

# Launch docking on the cores allocated to this single node or multi‑node job.
./dock_adv_parallel.sh "$indir" "$outdir" "$trg" "$cfg" "$threads"

echo "Finished at $(date)"
