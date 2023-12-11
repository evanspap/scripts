#!/usr/bin/env python3
import sys
import os
import re
import glob



path = r'*.pdbqt'
files = glob.glob(path)

for filename1 in files:
	name=os.path.basename(filename1).split('.')[0]
	extension=os.path.basename(filename1).split('.')[1]
	print(filename1)
	print(name)
	print(extension)

	#print(name[14:17])
	command="mv "+filename1+" "+sys.argv[1]+name+sys.argv[2]+"."+extension
	print(command)
	if sys.argv[3] == "True":
		os.system(command)
