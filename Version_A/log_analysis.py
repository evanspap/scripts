import sys
import os

def main():
   filepath = sys.argv[1]
  # print (filepath)

   if not os.path.isfile(filepath):
       print("File path {} does not exist. Exiting...".format(filepath))
       sys.exit()
       
   with open(filepath) as fp:
       cnt = 0
       cntcmp=0
       for line in fp:
            #print("line {} : {}".format(cnt, line))
            if line.strip().split(' ')[0] == '==>':
                print('\t')
                print(line.strip().split(' ')[1].split('.pdbqt')[0], end='', flush=True)
                cntcmp += 1
            if line.strip().split(' ')[0].isdigit():
                print(line.strip('\n'), end='', flush=True)
            cnt += 1
       print("Compounds= {}".format(cntcmp))
        
           
if __name__ == '__main__':
    main()