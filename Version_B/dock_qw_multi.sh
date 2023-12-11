#!/bin/bash

date
i=0
for filename1 in ./conf/*.pdbqt

do
  receptor_name=$(basename -- "$filename1")
  for filename in ./CTRP_compounds/*.pdbqt
  do
    ((i=i+1))
  	#echo $filename
    name=$(basename -- "$filename")
    echo ${name%.*} $i

    qvina-w --config ./conf/${receptor_name%.*}.conf --ligand $filename --log ./out/${receptor_name%.*}_${name%.*}.txt --out ./out/${receptor_name%.*}_${name%.*}.pdbqt
  done
done

#tail -n+1 ./out/*.txt > total_out.txt

#python sumary_out_lines_03.py total_out.txt > summary_out.txt
date