#!/usr/bin/env python3
import sys
import os
import re
import glob


i=0
d=1

for d in  range(1,17) :
	f =  open("docking_"+str(d)+".sh","a")
	f.write("mkdir output_"+str(d)+"\n")
	path =r'./process_'+str(d)+'/*pdbqt'
	files = glob.glob(path)
	print (path)
	print (files)
	for filename1 in files :
		filename2=filename1.replace("process_","output_").replace(".pdbqt","")
		f.write("/usr/local/ADFRsuite-1.0/ADFRsuite_x86_64Linux_1.0/bin/adfr -c 1 -l "+filename1+"  -t ./conf/3N3K_USP8.trg -J ADFR_USP8_ -n 16 --maxEvals 2500000 -O -o "+filename2+"\n")

