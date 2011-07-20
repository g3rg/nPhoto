'''
Created on 12/07/2011
@author g3rg
'''

import shutil
import os
import sys

import Image
import ExifTags

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QImage, QPixmap

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

def loadQPixMap(image, fname, width, height, thumb=False):
    qpx = None
    message = ""
    if fname:
        if os.path.exists(fname):
            path = fname
            if thumb:
                if os.path.exists(os.path.splitext(fname)[0] + ".thumbnail"):
                    path = os.path.splitext(fname)[0] + ".thumbnail"
                    
            image = QImage(path)
            if image.isNull():
                message = "Failed to read %s" % path
            else:
                #width = self.imageLabels[0][0].width()
                #height = self.imageLabels[0][0].height()
                img = image.scaled(width, height, Qt.KeepAspectRatio)
                qpx = QPixmap(QPixmap.fromImage(img))
                message = "Loaded %s" % fname

    #self.status.showMessage(message, 10000)
    return qpx

def processRotate(image, orientation):
    #TODO Process the rotate... do we actually want to do this? Or is it better for small screen to keep them all the same
    return image

def createThumbnail(infile, overwrite=False, width=256, height=256):
    size = width, height
    
    outfile = os.path.splitext(infile)[0] + ".thumbnail"
    if infile != outfile:
        try:
            if overwrite:
                if os.path.exists(outfile):
                    os.remove(outfile)
                    
            im = Image.open(infile)
            exif = loadExif(infile)
            if exif['orientation']:
                im = processRotate(im, exif['orientation'])
                
            im.thumbnail(size)
            im.save(outfile, "JPEG")
        except IOError:
            print "cannot create thumbnail for", infile
