#!/usr/bin/env python3
import sys
import os
import time
import subprocess
import re
import glob



path = r'.\MMSEG_pdbqt\*.pdbqt'
files = glob.glob(path)

filename1: str
for filename1 in files:
	print(filename1)
	basename=os.path.basename(filename1).split('.')[0]
	print(basename)
	f = open('out.out', 'w')
	f.write("receptor =./conf/" + basename + ".pdbqt" + "\n")
	os.system('START /WAIT C:\ProgramData\pymol\PyMOLWin.exe -cq '+filename1+' .\scratch_02.pml' )
	#subprocess.run (['C:\ProgramData\pymol\PyMOLWin.exe -cq', filename1, ' .\scratch_02.pml'])
	f.close()
	#time.sleep(3)
	os.system('move out.out '+' .\MMSEG_pdbqt\\'+basename+'.conf')
	#time.sleep(1)
