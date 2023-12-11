#!/bin/bash

for filename in ./in2/*.pdbqt
do
	name=$(basename -- "$filename")
	/usr/local/ADFRsuite-1.0/ADFRsuite_x86_64Linux_1.0/bin/adfr -c 16 -l ./in2/${name%.*}.pdbqt  -t ./target/7SV7_wo_ligand_reduce_Tezacaftor.trg -J CFTR_ -n 16 --maxEvals 5000000 -O -o ./out_AGFR_1/${name%.*}_CFTR
done