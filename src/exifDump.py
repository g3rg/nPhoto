'''
Created on 11/07/2011
@author g3rg
'''

import sys

import Image
import ExifTags

def doMain():
    args = sys.argv

    if len(args) < 2:
        print "MORE ARGS!"
    else:
        img = Image.open(args[1])
        info = img._getexif()
        for tag, value in info.items():
            decoded = ExifTags.TAGS.get(tag, tag)
            print decoded, ":", value

#DateTimeOriginal
#ExifImageWidth
#Make
#Model
#Orientation
#DateTime
#ExifImageHeight

if __name__ == "__main__":
    doMain()
