'''
Created on 28/06/2011

@author: g3rg
'''
from Tkinter import Tk, Frame, Button, LEFT, Menu
from nphoto.settings import Settings

class App:
    settings = Settings()
    
    def __init__(self, master):
        self.frame = Frame(master)
        self.frame.pack()
        
        # build the menu
        self.menubar = Menu(self.frame)
        self.actionmenu = Menu(self.menubar, tearoff=0)
        
        
        self.actionmenu.add_command(label="Settings", command=self.showSettings)
        self.actionmenu.add_command(label="Import", command=self.doImport)
        self.actionmenu.add_command(label="Backup", command=self.doBackup)
        self.actionmenu.add_command(label="Quit", command=self.quit)
        
        self.menubar.add_cascade(label="Actions", menu=self.actionmenu)
        
        master.config(menu=self.menubar)
        
    def showSettings(self):
        print "Show settings!"
        
    def doImport(self):
        print "Do Import!"
        
    def doBackup(self):
        print "Do Backup!"
        
    def quit(self):
        self.settings.saveSettings()
        self.frame.quit()
        
    def say_hi(self):
        print "Dir is: " + self.settings.import_dir


def doMain():
    root = Tk()
    app = App(root)
    
    root.mainloop()
    

if __name__ == '__main__':
    doMain()