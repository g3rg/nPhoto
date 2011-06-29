'''
Created on 28/06/2011

@author: g3rg
'''
from Tkinter import Tk, Frame, Menu, Label, Entry
import tkMessageBox
import tkFileDialog
from nphoto.settings import Settings
from nphoto.ui import Dialog
import os

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
        if not hasattr(self.settings,  'library_dir') or self.settings.library_dir in (None,  ''):
            tkMessageBox.showerror("Import Failed",  message="You need to specify a library directory in your settings")
            return
        if not os.path.exists(self.settings.library_dir) or os.path.isfile(self.settings.library_dir):
            tkMessageBox.showerror("Import Failed", message="The library directory in your settings either doesn't exist, or its not a directory")
            return
            
        importFrom = tkFileDialog.askdirectory()
        if importFrom in (None,  ''):
            return
        
        if not os.path.exists(importFrom) or os.path.isfile(importFrom):
            tkMessageBox.showerror("Import Failed", message="The import directory either doesn't exist, or is not a directory")
            return

        if importFrom == self.settings.library_dir:
            tkMessageBox.showerror("Import Failed", message="Your import directory and library directory can not be the same")
            return

        numTotal = 0
        numDuplicates = 0

        tkMessageBox.showinfo("Import",  message="DUPLICATE TEST NOT IMPLEMENTED YET!")
        for f in os.listdir(importFrom):
            print f
            # is it a directory? if so RECURSE!
            # is it a JPEG?
            # is it a RAW file?
            # settings for types of files to care about?
            
            
        if tkMessageBox.askyesno("Import",  message="Out of %d photos found, %d look to be duplicates. Continue with import?" % (numTotal,  numDuplicates)):
            # copy all non duplicates
            # verify they have been copied
            # check for duplicates?
            pass
        
        
        
    def doBackup(self):
        if not hasattr(self.settings,  'library_dir') or self.settings.library_dir in (None,  ''):
            tkMessageBox.showerror("Backup Failed",  message="You need to specify a library directory in your settings")
            return
        if not os.path.exists(self.settings.library_dir) or os.path.isfile(self.settings.library_dir):
            tkMessageBox.showerror("Backup Failed", message="The library directory in your settings either doesn't exist, or its not a directory")
            return        
        
        
        if not hasattr(self.settings,  'bkup_dirs') or self.settings.bkup_dirs in (None,  ''):
            tkMessageBox.showerror("Backup Failed",  message="You need to specify at least one backup directory in your settings")
            return

        for path in self.settings.bkup_dirs.split(","):
            if not os.path.exists(path.strip()) or os.path.isfile(path.strip()):
                tkMessageBox.showerror("Backup Failed", message="The backup directory <%s> in your settings either doesn't exist, or its not a directory" % (path))
                return
        
        
    def quit(self):
        self.settings.width=self.frame.master.winfo_width()
        self.settings.height=self.frame.master.winfo_height()
        self.settings.saveSettings()
        self.frame.quit()


def doMain():
    root = Tk()
    root.title('nPhoto')
    app = App(root)
    root.mainloop()
    

if __name__ == '__main__':
    doMain()
