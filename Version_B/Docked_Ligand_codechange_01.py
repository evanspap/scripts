#!/usr/bin/env python3
import sys
import os
import re
import glob



path = r'*.pdbqt'
files = glob.glob(path)

for filename1 in files:
	name=os.path.basename(filename1).split('.')[0]
	print(filename1)
	print(name)
	print(name[14:17])
	command="sed -i 's/UNL /"+sys.argv[1]+name[14:17]+"/g' "+filename1
	print(command)
	if sys.argv[2] == "True":
		os.system(command)
