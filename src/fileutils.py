'''
Created on 12/07/2011
@author g3rg
'''

import shutil
import os

def copyFileIncludingDirectories(self, src, dest):
    dirs = dest.split(os.sep)
    dirs = dirs[0:len(dirs)-1]
    d = ""
    for dir in dirs:
        d = d + dir + os.sep
        if not os.path.exists(d):
            os.mkdir(d)
 
    shutil.copyfile(src, dest)
