'''
Created on 12/07/2011
@author g3rg
'''

import shutil
import os

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

def loadQPixMap(image, fname, width, height):
    qpx = None
    message = ""
    if fname:
        image = QImage(fname)
        if image.isNull():
            message = "Failed to read %s" % fname
        else:
            #width = self.imageLabels[0][0].width()
            #height = self.imageLabels[0][0].height()
            img = image.scaled(width, height, Qt.KeepAspectRatio)
            qpx = QPixmap(QPixmap.fromImage(img))
            message = "Loaded %s" % fname

    #self.status.showMessage(message, 10000)
    return qpx
