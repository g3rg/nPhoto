'''
Created on 28/06/2011

@author: g3rg
'''
from Tkinter import Tk, Frame, Menu, Label, Entry
import Image
import ImageTk

import tkMessageBox
import tkFileDialog

import os
import shutil
import datetime

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

class ImportMetadataDialog(Dialog):
    comment = None
    keywords = None
    album = None
    okPressed = False
    
    def body(self, master):
        Label(master, text="Album").grid(row=0)
        self.album_field = Entry(master)
        self.album_field.grid(row=0, column=1)
        Label(master, text="Comment").grid(row=1)
        self.comment_field = Entry(master)
        self.comment_field.grid(row=1, column=1)
        Label(master, text="Keywords").grid(row=2)
        self.keywords_field = Entry(master)
        self.keywords_field.grid(row=2, column=1)

    def apply(self):
        self.album = self.album_field.get()
        self.comment = self.comment_field.get()
        self.keywords = self.keywords_field.get()
        self.okPressed = True


class LibraryImage:
    album = None
    path = None
    importPath = ''
    comment = ''
    keywords = {}
    #exif

class App:
    settings = Settings()
    
    def __init__(self, master):
        master.config()

        
        self.frame = Frame(master, width=self.settings.width, height=self.settings.height)


        self.menubar = Menu(self.frame)
        self.actionmenu = Menu(self.menubar, tearoff=0)
        
        self.actionmenu.add_command(label="Settings", command=self.showSettings)
        self.actionmenu.add_command(label="Import", command=self.doImport)
        self.actionmenu.add_command(label="Backup", command=self.doBackup)
        self.actionmenu.add_command(label="Quit", command=self.quit)
        
        self.menubar.add_cascade(label="Actions", menu=self.actionmenu)
        master.protocol("WM_DELETE_WINDOW", self.handleClose)
        master.config(menu=self.menubar)

        
        #x = Image.open("/home/g3rgz/1228465149000.jpg")
        #x = x.resize((250,250))
        #self.image = ImageTk.PhotoImage(x)
        #self.image_label = Label(self.frame, image=self.image, bd=0)
        #self.image_label.pack()
        
        self.frame.pack()
        
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
            
        if not self.settings.file_extensions or self.settings.file_extensions in (None, ''):
            tkMessageBox.showerror("Import Failed", message="You need to specify file extensions to manage in your settings")
            return

        importFrom = tkFileDialog.askdirectory(initialdir=self.settings.last_import_dir,title="Import Source")
        if importFrom in (None,  ''):
            return
        
        if not os.path.exists(importFrom) or os.path.isfile(importFrom):
            tkMessageBox.showerror("Import Failed", message="The import directory either doesn't exist, or is not a directory")
            return

        if importFrom == self.settings.library_dir:
            tkMessageBox.showerror("Import Failed", message="Your import directory and library directory can not be the same")
            return

        imd = ImportMetadataDialog(self.frame.master)
        
        if not imd.okPressed:
            return
        
        if imd.keywords and imd.keywords not in (None, ''):
            keywords = imd.keywords
        else:
            keywords = ""

        if imd.comment and imd.comment not in (None, ''):
            comment = imd.comment
        else:
            comment = ""

        if imd.album and imd.album not in (None,  ''):
            album = imd.album + os.sep
        else:
            album = ''

        paths = self.buildFileList(importFrom)
        numTotal = len(paths)
        
        nonDupes = self.removeDuplicates(paths, importFrom,  album)
        numDuplicates = numTotal - len(nonDupes)
        
        if tkMessageBox.askyesno("Import",  message="Out of %d photos found, %d look to be duplicates. Continue with import?" % (numTotal,  numDuplicates)):
            self.settings.last_import_dir = importFrom
            self.settings.saveSettings()
            
            for path in nonDupes:
                dest = self.buildLibPath(importFrom, path,  album)
                self.copyFileIncludingDirectories(path, dest)
                # TODO Handle copy failure exceptions!
                
                if not os.path.exists(dest):
                    tkMessageBox.showerror("Import Failed", "The file <%s> was not imported properly, aborting import" % (path))
                    return

                self.buildSideCarFile(path, dest, comment, keywords)
                # add file info to DB
            
            tkMessageBox.showinfo("Import", message="Import completed")
            #verify all files again?

    def buildSideCarFile(self, path, dest, comments, keywords):
        sidecarFilePath = dest + os.extsep + "sidecar"
        f = open(sidecarFilePath, "w")
        f.write("originalpath=" + path + "\n")
        f.write("keywords=%s\n" % (keywords))
        f.write("comment=%s\n" % (comments))
        f.write("exif:\n")
        f.close()
        # read info from file and populate sidecar
        

    def copyFileIncludingDirectories(self, src, dest):
        dirs = dest.split(os.sep)
        dirs = dirs[0:len(dirs)-1]
        d = ""
        for dir in dirs:
            d = d + dir + os.sep
            if not os.path.exists(d):
                os.mkdir(d)
        
        shutil.copyfile(src, dest)
        pass
    
    def buildLibPath(self, importFrom, path,  album):
        relPath = path[len(importFrom):]
        libPath = self.settings.library_dir + os.sep + album + relPath
        
        return libPath
        
    def removeDuplicates(self, paths, importFrom,  album):
        nonDupes = []
        
        for path in paths:
            libPath = self.buildLibPath(importFrom, path,  album)
            if not os.path.exists(libPath):
                nonDupes.append(path)
        
        return nonDupes
        
    def isImageFile(self, filepath):
        extensionList = self.settings.file_extensions.split(",")
        for extension in extensionList:
            if filepath.upper().endswith(extension.upper()):
                return True
        return False
        
    def buildFileList(self, importFrom):
        paths = []
        for f in os.listdir(importFrom):
            fullpath = importFrom + os.sep + f
            
            if not os.path.isfile(fullpath):
                paths.extend(self.buildFileList(fullpath))
            else:
                if self.isImageFile(fullpath):
                    paths.append(fullpath)
        return paths
        
        
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

        dt = datetime.date.today()
        bkupDirName = str(dt.year) + str(dt.month) + str(dt.day)

        for path in self.settings.bkup_dirs.split(","):
            if not os.path.exists(path.strip()) or os.path.isfile(path.strip()):
                tkMessageBox.showerror("Backup Failed", message="The backup directory <%s> in your settings either doesn't exist, or its not a directory" % (path))
                return
        
            if os.path.exists(path.strip() + os.sep + bkupDirName):
                tkMessageBox.showerror("Backup Failed", message="There is already a backup for today in a backup directory <%s>" % (path.strip()))
                return
        
        for path in self.settings.bkup_dirs.split(","):
            shutil.copytree(self.settings.library_dir, path.strip() + os.sep + bkupDirName)
        
        tkMessageBox.showinfo("Backup", message="Backup completed!")
        # shutil.copytree(src, dest)
        
        
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
