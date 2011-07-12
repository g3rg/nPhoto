'''
Created on 12/07/2011
@author g3rg
'''

import os


class Photo():
    srcPath = None
    path = None
    date = None
    comment = None
    orientation = None
    keywords = []
    exif = None

    def setExif(self, exif):
        self.exif = exif

        bkupDt = self.date
        self.date = None
        
        for tag in self.exif.keys():
            if tag == "DateTimeOriginal":
                self.date = self.exif[tag]
            elif tag == "DateTime" and not self.date:
                self.date = self.exif[tag]
            elif tag == "Orientation":
                self.orientation = self.exif[tag]

        if not self.date:
            self.date = bkupDt

    def buildSideCarFile(self, dest):
        sidecarFilePath = dest + os.extsep + "sidecar"
        f = open(sidecarFilePath, "w")
        f.write("originalpath=" + self.srcPath + "\n")
        f.write("keywords=%s\n" % (" ".join(self.keywords)))
        f.write("comment=%s\n" % (self.comment))
        f.write("date=%s\n" % (self.date))
        f.write("orientation=%s\n" % (self.orientation))
        f.write("exif:\n")
        if self.exif:
            for tag in self.exif.keys():
                f.write(tag)
                f.write("=")
                f.write(self.exif[tag])
                f.write("\n")
        f.close()


    @classmethod
    def loadSideCarFile(cls, path):
        ph = Photo()
        f = open(path)
        for line in f:
            if line.startswith("originalpath="):
                ph.srcPath = line[len("originalpath="):]
            elif line.startswith("keywords="):
                keywords = line[len("keywords="):]
                for keyword in keywords.split(","):
                    ph.keywords.append(keyword.strip())
            elif line.startswith("comment="):
                ph.comment = line[len("comment="):]
            else:
                if line.startswith("DateTimeOriginal="):
                    ph.date = line[len("DateTimeOriginal="):]
                elif line.startswith("DateTime=") and not ph.date:
                    ph.date = line[len("DateTime="):]
                elif line.startswith("Orientation="):
                    ph.orientation = line[len("Orientation"):]
            
        f.close()
        return ph
        
class Album():
    name = None
    path = None
    comment = None
    albums = {}
    photos = []

    def __init__(self, name=None):
        if name != None:
            self.name = name

