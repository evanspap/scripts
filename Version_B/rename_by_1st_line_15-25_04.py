#!/usr/bin/env python3
import sys
import os
import glob


i=0
ix=float(0)

path = r'*pdbqt'
files = glob.glob(path)

s=len(files)
print(s)


for filename1 in files :
	i +=1
	#print(i)
	if i - ix*s >= s/100 :
		ix=float(i/s)
		print("{:.2f}".format(ix))
	f = open(filename1, "r")
	print(filename1)
	filename2= f.readline()[15:25]+'.pdbqt'
	print(filename2)
	os.system("mv "+filename1+" "+filename2)
