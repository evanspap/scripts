#!/usr/bin/env python3
import sys
import os
import glob

total = len(sys.argv)
start = str(sys.argv[1])
end = str(sys.argv[2])
act = str(sys.argv[3])

print (total)
print (start)
print (end)
print (act)
print (sys.argv)

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
	filename2= f.readline()[int(float(start)):int(float(end))]+'.pdbqt'
	if act == "1" :
		os.system("mv "+filename1+" "+filename2)
	else:
		print("mv "+filename1+" "+filename2)
