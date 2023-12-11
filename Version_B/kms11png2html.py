import glob, os, fnmatch
print('<table style="width:100%">')
#print('<col style="width:50%">')
#print('<col style="width:50%">')
#for file in glob.glob("mm1s*.png"):
#    print('<tr><td><img  src="'+file+'"/></td><td>'+os.path.splitext(file) [0]+'</td></tr>')
    
#print('</table>')
    
for dirpath, dirs, files in os.walk('.'):
    print('<tr>')
    for filename in fnmatch.filter(files, '*kms11*.png'):
        print('<td><img  src="'+os.path.join(dirpath, filename)+'"</td>')
    
    print('</tr>')
