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
    optionKeys = ['import_dir', 'bkup_dirs']

    def __init__(self):
        '''
        Constructor
        '''
        self.parseConfig()


    def initEmptySettings(self):
        self.options = {}
        for option in self.optionKeys:
            self.options[option] = ""
        
    def setOptionFields(self):
        for option in self.optionKeys:
            if option in self.options:
                setattr(self, option, self.options[option])
            else:
                setattr(self, option, "")
        
    def saveSettings(self):
        f = open(FILENAME,'w')
        for option in self.options:
            f.write(option + OPTION_CHAR + self.options[option] + "\n")
        
        f.close()

    def parseConfig(self):
        self.options = {}
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
                    self.options[option] = value
            f.close()
        except: 
            self.initEmptySettings()
            self.saveSettings()
            
            
        self.setOptionFields()
                
