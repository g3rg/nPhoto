'''
Created on 12/07/2011
@author g3rg
'''


class Photo():
    srcPath = None
    path = None
    date = None
    comment = None
    orientation = None
    keywords = []
    
class Album():
    name = None
    path = None
    comment = None
    albums = {}
    photos = []

    def __init__(self, name=None):
        if name != None:
            self.name = name

