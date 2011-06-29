'''
Created on 28/06/2011

@author: g3rg
'''
from Tkinter import Tk, Frame, Menu, Label, Entry
from nphoto.settings import Settings
from nphoto.ui import Dialog

app = None
        
class SettingsDialog(Dialog):
    
    def __init__(self, master, settings):
        self.settings = settings
        Dialog.__init__(self, master)
    
    def body(self, master):
        if hasattr(self, 'settings'):
            print "Loading settings!"
            x = 0
            self.fields = {}
            for option in self.settings.guisettingKeys:
                Label(master, text=option).grid(row=x)
                e = Entry(master)
                e.grid(row=x, column=1)
                if hasattr(self.settings, option):
                    e.insert(0,getattr(self.settings, option))
                self.fields[option] = e
                x = x + 1
                
            return self.fields[self.fields.keys()[0]]
        else:
            Label(master, text="WHERE IS MY SETTINGS OBJECT!").grid(row=0)

    def apply(self):
        for option in self.settings.guisettingKeys:
            setattr(self.settings, option, self.fields[option].get())
        
        self.settings.saveSettings()
        
        print "Save the settings!"

class App:
    settings = Settings()
    
    def __init__(self, master):
        master.config()
        
        self.frame = Frame(master, width=self.settings.width, height=self.settings.height)
        self.frame.pack()
        
        # build the menu
        self.menubar = Menu(self.frame)
        self.actionmenu = Menu(self.menubar, tearoff=0)
        
        self.actionmenu.add_command(label="Settings", command=self.showSettings)
        self.actionmenu.add_command(label="Import", command=self.doImport)
        self.actionmenu.add_command(label="Backup", command=self.doBackup)
        self.actionmenu.add_command(label="Quit", command=self.quit)
        
        self.menubar.add_cascade(label="Actions", menu=self.actionmenu)
        master.protocol("WM_DELETE_WINDOW", self.handleClose)
        master.config(menu=self.menubar)
        
    def handleClose(self):
        self.quit()
        
    def showSettings(self):
        settingsDialog = SettingsDialog(self.frame.master, self.settings)
        
    def doImport(self):
        print "Do Import!"

        
        
    def doBackup(self):
        print "Do Backup!"

        
        
    def quit(self):
        self.settings.width=self.frame.master.winfo_width()
        self.settings.height=self.frame.master.winfo_height()
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