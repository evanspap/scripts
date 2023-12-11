#!/usr/bin/env python3
import glob, os, fnmatch, sys
print('<table style="width:100%">')
#print('<col style="width:50%">')
#print('<col style="width:50%">')
#for file in glob.glob("mm1s*.png"):
#    print('<tr><td><img  src="'+file+'"/></td><td>'+os.path.splitext(file) [0]+'</td></tr>')
    
#print('</table>')
f = open(sys.argv[1], "r")
print('<tr>')
for line in f:
        print('<tr>')
        print('<td><img  src="'+line.split()[0][1:]+'.png "</td>')
        print('<td>' +line.split()[0]+ '</td>')
        print('<td><img  src="'+line.split()[3]+'.png "</td>')
        print('<td>' +line.split()[3]+ '</td>')
        print('<td> Tanimoto similarity=' +line.split()[5]+ '</td>')
        print('</tr>')
