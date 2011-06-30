'''
Created on 29/06/2011

@author: g3rg
'''

FILENAME="nPhoto.config"
COMMENT_CHAR="#"
OPTION_CHAR="="


class Settings(object):
    '''
    classdocs
    '''
    optionKeys = ['library_dir', 'bkup_dirs', 'file_extensions', 'last_import_dir', 'width', 'height']
    guisettingKeys = ['library_dir', 'bkup_dirs', 'file_extensions']

    def __init__(self):
        '''
        Constructor
        '''
        self.parseConfig()


    def initEmptySettings(self):
        for option in self.optionKeys:
            setattr(self, option, "")
        
        self.width=600
        self.height=400
       
    def saveSettings(self, frame=None):
        f = open(FILENAME,'w')
        for option in self.optionKeys:
            if hasattr(self, option):
                f.write(option + OPTION_CHAR + str(getattr(self, option)) + "\n")
        
        # f.write("mainwindowwidth" + OPTION_CHAR + frame.)
        
        f.close()

    def parseConfig(self):
        self.initEmptySettings()
        try:
            f = open(FILENAME)
            for line in f:
                if COMMENT_CHAR in line:
                    # split on comment char, keep everything before comment
                    line, comment = line.split(COMMENT_CHAR,1)
                if OPTION_CHAR in line:
                    option, value = line.split(OPTION_CHAR,1)
                    option = option.strip()
                    value = value.strip()
                    setattr(self, option, value)
                    
            # set any missing settings
            f.close()
        except: 
            self.saveSettings()
