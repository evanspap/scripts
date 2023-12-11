#!/bin/bash

date1=$(date +"%s")
date

i=0
for filename in ./input/*.pdbqt
do
	cp $filename ./processing/${name%.*}.pdbqt
	wait 
	let "i=i+1"
	echo $filename
	name=$(basename -- "$filename")

	echo ./processing/${name%.*}.pdbqt $i
	wait

	/usr/local/ADFRsuite-1.0/ADFRsuite_x86_64Linux_1.0/bin/adfr -c 1 -l /data/Jamie/processing/${name%.*}.pdbqt -t /data/Jamie/conf/3N3K_USP8.trg -J ADFR_USP8_ -n 16 --maxEvals 2500000 -O -o /data/Jamie/output/${name%.*}
	
done
