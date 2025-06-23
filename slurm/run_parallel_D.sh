#!/usr/bin/env bash

#SBATCH --job-name=array_test
#SBATCH --output=array_test.%A_%a.log
#SBATCH -N 1
#SBATCH -p short-40core
#SBATCH -t 04:00:00
#SBATCH --array=1-40

mkdir temp

module load anaconda/3
module load gnu-parallel/6.0

START=$SLURM_ARRAY_TASK_ID
NUMLINES=100
STOP=$((SLURM_ARRAY_TASK_ID*NUMLINES))
START="$(($STOP - $(($NUMLINES - 1))))"

echo "START=$START"
echo "STOP=$STOP"

for (( N = $START; N > temp/tasks_${START}_${STOP}
done

cat temp/tasks_${START}_${STOP} | parallel --jobs 40 --verbose python number_square.py {}

# clean up the temp files
rm temp/tasks_${START}_${STOP}