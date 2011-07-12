'''
Created on 12/07/2011
@author g3rg
'''

import shutil
import os

import Image
import ExifTags

def copyFileIncludingDirectories(src, dest):
    dirs = dest.split(os.sep)
    dirs = dirs[0:len(dirs)-1]
    d = ""
    for dir in dirs:
        d = d + dir + os.sep
        if not os.path.exists(d):
            os.mkdir(d)
 
    shutil.copyfile(src, dest)


def loadExif(path, exifTags):
    img = Image.open(path)
    info = img._getexif()
    tags = {}
    for tag, value in info.items():
        decoded = ExifTags.TAGS.get(tag,tag)
        if decoded in exifTags:
            tags[decoded] = unicode(value)

    return tags
