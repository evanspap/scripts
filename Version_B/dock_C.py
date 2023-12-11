#!/usr/bin/env python3
import sys
import os
import re
import glob


i=0
d=1

f =  open("dock.sh","a")

for d in  range(1,17) :
	f.write("bash docking_"+str(d)+".sh &\n")

