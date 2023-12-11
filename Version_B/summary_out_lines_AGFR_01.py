#!/usr/bin/env python3
import sys
import os

f = open(sys.argv[1], "r")
print_flag=0

for ln in f:
	#print(ln)
	if print_flag== 1 :
		out=ln.rstrip()
		print(out, end=" ");
		print("", end='\n');
		print_flag=0

	if ln!='\n':
		args=ln.split()
		if args[0]=='==>':	
#			print("", end='\n');
			out=ln.rstrip()
			print(out, end=" ");
		else:
			if args[0]=='-----+------------+--------+------+--------+------+--------+------+':
				print_flag=1
			
