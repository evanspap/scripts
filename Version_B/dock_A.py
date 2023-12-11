#!/usr/bin/env python3
import sys
import os
import re
import glob


i=0
d=1
ix=float(0)

path = r'./input/*pdbqt'
files = glob.glob(path)

s=len(files)
print(s)
print("n=")
n=int(s/16)
print(n)

os.system("mkdir process_"+str(d))

for filename1 in  files :
	i +=1;
	print (i)
	filename2=filename1.replace("input","process_"+str(d))
	if  i <=  n :
		print (filename1);
		print (filename2);
		os.system("cp "+filename1+" "+filename2)
	else:
		i=1
		d +=1;
		os.system("mkdir process_"+str(d))
		filename2=filename1.replace("input","process_"+str(d))
		print (filename1)
		print (filename2)
		os.system("cp "+filename1+" "+filename2)

