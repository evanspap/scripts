#!/bin/bash

out="out_adv_4"
trg="CFTR"

date1=$(date +"%s")
date

i=0
for filename in ./in2/*.pdbqt
do
	((i=i+1))
#	echo $filename
	name=$(basename -- "$filename")
	echo "==>" ${name%.*} $i
	if test -f ./$out/${name%.*}_$trg.pdbqt
	then
	echo "tested"
	else
	vina --config ./conf/conf3.txt --ligand $filename  --out ./$out/${name%.*}_$trg.pdbqt --spacing 0.1
	fi
#	mv $filename ./done/${name%.*}.pdbqt
done

date2=$(date +"%s")
date

date -u -d "0 $date2 seconds - $date1 seconds" +"%H:%M:%S"

#tail -n+1 ./out/*.txt > total_out.txt

#python sumary_out_lines_03.py total_out.txt > summary_out.txt
