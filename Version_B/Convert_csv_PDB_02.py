'''
Created on Jul 25, 2022

@author: Evangelos
'''
#!/usr/bin/env python3
import sys
import os
import glob


i=0

path = r'*.csv'
files = glob.glob(path)


for filename1 in files :
#    print(filename1)
    i=0
    f = open(filename1, "r")
    file=filename1.split('.')
    filename2= file[0]+'_.pdb'
    print(filename2)
    f_out=open(filename2, "w")    
    for ln in f:
        #print (ln)
        i +=1
    #print(i)
        if i>1 :
            line= ln.split(',')
            out= 'ATOM  '+str(i-1).rjust(5)+ '  CA ALA A '+str(i-1).rjust(5)+'  ' \
            +str('{:.3f}'.format(float(line[0]))).rjust(8) \
            +str('{:.3f}'.format(float(line[1]))).rjust(8)\
            +str('{:.3f}'.format(float(line[2]))).rjust(8) \
            +'  0.0   0.0           C'+'\n'
            print(out)
            f_out.write(out)
    f.close()
    f_out.close()
    
