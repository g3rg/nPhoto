'''
Created on 02/07/2011
@author g3rg
'''

import os
import sys
import shutil
import datetime

from PyQt4.QtCore import Qt, QTime, QTimer, QSettings, QVariant, QPoint, QSize, SIGNAL, SLOT
from PyQt4.QtGui import QApplication, QLabel, QImage, QMainWindow, QPixmap, QAction, \
            QIcon, QDialog, QDialogButtonBox, QGridLayout, QLineEdit, QMessageBox, QFileDialog

__version__ = "0.1.0"

class Photo():
    srcPath = None
    path = None
    comment = None
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

class ImportMetadataDialog(QDialog):
    def __init__(self, parent):
        super(ImportMetadataDialog, self).__init__(parent)
        albumLabel = QLabel("Album")
        self.albumEdit = QLineEdit()
        commentsLabel = QLabel("Comments")
        self.commentsEdit = QLineEdit()
        keywordsLabel = QLabel("Keywords")
        self.keywordsEdit = QLineEdit()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        self.connect(buttonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.setWindowTitle("Import")

        grid = QGridLayout()
        grid.addWidget(albumLabel, 0, 0)
        grid.addWidget(self.albumEdit, 0, 1)
        grid.addWidget(commentsLabel, 1, 0)
        grid.addWidget(self.commentsEdit, 1, 1)
        grid.addWidget(keywordsLabel, 2, 0)
        grid.addWidget(self.keywordsEdit, 2, 1)
        
        grid.addWidget(buttonBox, 3, 0, 1, 2)
        self.setLayout(grid)

class SettingsDialog(QDialog):
    def __init__(self, parent, libPath, backupPaths, extensions):
        super(SettingsDialog, self).__init__(parent)

        #self.parent = parent
        
        libPathLabel = QLabel("Library Path")
        self.libPathEdit = QLineEdit(libPath)
        backupPathsLabel = QLabel("Backup Paths")
        self.backupPathsEdit = QLineEdit(backupPaths)
        fileExtensionLabel = QLabel("File Extensions")
        self.fileExtensionEdit = QLineEdit(extensions)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        self.connect(buttonBox, SIGNAL("accepted()"),
        self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"),
        self, SLOT("reject()"))
        self.setWindowTitle("Settings")

        grid = QGridLayout()
        
        grid.addWidget(libPathLabel, 0, 0)
        grid.addWidget(self.libPathEdit, 0, 1)
        grid.addWidget(backupPathsLabel, 1, 0)
        grid.addWidget(self.backupPathsEdit, 1, 1)
        grid.addWidget(fileExtensionLabel, 2, 0)
        grid.addWidget(self.fileExtensionEdit, 2, 1)
        
        grid.addWidget(buttonBox, 3, 0, 1, 2)
        self.setLayout(grid)

class NPhotoMainWindow(QMainWindow):
    rootAlbum = None

    def __init__(self, parent=None):
        super(NPhotoMainWindow, self).__init__(parent)

        self.image = QImage()
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(200,200)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.imageLabel)

        self.status = self.statusBar()
        self.status.setSizeGripEnabled(False)

        fileMenu = self.menuBar().addMenu("&File")
        fileImportAction = self.createAction("&Import", self.doImport, "Ctrl-I", "fileimport", "Import photos into your library")
        fileBackupAction = self.createAction("&Backup", self.doBackup, "Ctrl-B", "filebkup", "Backup your library")
        fileSettingsAction = self.createAction("&Settings", self.doSettings, "Ctrl-S", "filesettings", "Settings")
        fileQuitAction = self.createAction("&Quit", self.close, "Ctrl+Q", "filequit", "Close the application")

        self.addActions(fileMenu, (fileImportAction, fileBackupAction, fileSettingsAction, None, fileQuitAction))
    
        settings = QSettings()
        size = settings.value("MainWindow/Size", QVariant(QSize(600,500))).toSize()
        self.resize(size)
        position = settings.value("MainWindow/Position", QVariant(QPoint(0,0))).toPoint()
        self.move(position)
        self.restoreState(settings.value("MainWindow/State").toByteArray())
        self.setWindowTitle("nPhoto")

        if settings.value("Paths/Library").toString() not in (None, ''):
            QTimer.singleShot(0, self.loadLibrary)
        else:
            self.status.showMessage("No Library Path in settings", 10000)

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)


        
    def doBackup(self):
        libDir = self.getSetting("Paths/Library")
        bkupPaths = self.getSetting("Paths/Backup")
        
        if libDir in (None,  ''):
            QMessageBox.warning(self, "Backup Failed", "You need to specify a library directory in your settings")
            return
        if not os.path.exists(libDir) or os.path.isfile(libDir):
            QMessageBox.warning(self, "Backup Failed", "The library directory in your settings either doesn't exist, or its not a directory")
            return        
        
        if bkupPaths in (None,  ''):
            QMessageBox.warning(self, "Backup Failed",  "You need to specify at least one backup directory in your settings")
            return

        dt = datetime.date.today()
        bkupDirName = str(dt.year) + str(dt.month) + str(dt.day)

        for path in bkupPaths.split(","):
            if not os.path.exists(path.strip()) or os.path.isfile(path.strip()):
                QMessageBox.warning(self, "Backup Failed", "The backup directory <%s> in your settings either doesn't exist, or its not a directory" % (path))
                return
        
            if os.path.exists(path.strip() + os.sep + bkupDirName):
                QMessageBox.warning(self, "Backup Failed", "There is already a backup for today in a backup directory <%s>" % (path.strip()))
                return
        
        for path in bkupPaths.split(","):
            shutil.copytree(libDir, path.strip() + os.sep + bkupDirName)
        
        QMessageBox.information(self, "Backup", "Backup completed!")


    def doSettings(self):
        settings = QSettings()
        libPath = settings.value("Paths/Library", "").toString()
        backupPaths = settings.value("Paths/Backup", "").toString()
        fileExt = settings.value("FileExtensions", "jpg, CR2").toString()
        
        dialog = SettingsDialog(self, libPath, backupPaths, fileExt)
        if dialog.exec_():
            settings = QSettings()
            settings.setValue("Paths/Library", QVariant(dialog.libPathEdit.text()))
            settings.setValue("Paths/Backup", QVariant(dialog.backupPathsEdit.text()))
            settings.setValue("FileExtensions", QVariant(dialog.fileExtensionEdit.text()))
            
            self.status.showMessage("Settings updated", 5000)
            

    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def loadInitialPhoto(self):
        self.loadFile("/home/g3rgz/1228465149000.jpg")

    def loadLibrary(self):
        self.status.showMessage("Loading Photo Library")

        self.rootAlbum = self.loadAlbum(self.getSetting("Paths/Library"), "Library")

        if self.rootAlbum == None:
            self.rootAlbum = Album(name="Library")
        
        self.loadInitialPhoto()

        self.status.showMessage("Library successfully loaded", 5000)

    def loadAlbum(self, path, title = None, regenSideCar = False):
        album = Album()
        if title not in (None, ''):
            album.name = title
        else:
            album.name = path[path.rfind(os.sep)+1:]
            #Quick hack for windows!
            #if album.name.startswith('\\'):
            #    album.name = album.name[1:]
            
        album.albums = {}
        album.photos = []
        album.path = path
        
        for fl in os.listdir(path):
            if not os.path.isfile(path + os.sep + fl):
                album.albums[fl] = self.loadAlbum(path + os.sep + fl)
            else:
                if self.isImageFile(path + os.sep + fl):
                    if not regenSideCar:
                        ph = None
                        if os.path.exists(path + os.sep + fl + ".sidecar"):
                            ph = self.loadSideCarFile(path + os.sep + fl + ".sidecar")
                        else:
                            ph = Photo()
                            ph.comment = ""
                            ph.keywords = {}
                            ph.srcPath = None
                            
                        ph.path = path + os.sep + fl
                        print ph.path
                        album.photos.append(ph)
                    else:
                        QMessageBox.information(self, "Loading", "Regenerating of sidecar information not implemented yet")

        return album

    def loadSideCarFile(self, path):
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
                # EXIF?!?!?!
                pass
            
        f.close()
        return ph



    def loadFile(self, fname):
        if fname:
            self.image = QImage(fname)
            if self.image.isNull():
                message = "Failed to read %s" % fname
            else:
                width = self.image.width()
                height = self.image.height()
                image = self.image.scaled(width, height, Qt.KeepAspectRatio)
                self.imageLabel.setPixmap(QPixmap.fromImage(image))
                message = "Loaded %s" % fname

            self.status.showMessage(message, 10000)

    def closeEvent(self, event):
        settings = QSettings()
        #TODO Store Last image file and album?
        settings.setValue("MainWindow/Size", QVariant(self.size()))
        settings.setValue("MainWindow/Position", QVariant(self.pos()))
        settings.setValue("MainWindow/State", QVariant(self.saveState()))


    def doImport(self):
        settings = QSettings()
        libPath = settings.value("Paths/Library").toString()
        fileExt = settings.value("FileExtensions").toString()
        
        if libPath in (None,  ''):
            QMessageBox.warning(self, "Import Failed",  "You need to specify a library directory in your settings")
            return
        
        if not os.path.exists(libPath) or os.path.isfile(libPath):
            QMessageBox.warning(self, "Import Failed", "The library directory in your settings either doesn't exist, or its not a directory")
            return
            
        if not fileExt or fileExt in (None, ''):
            QMessageBox.warning(self, "Import Failed", "You need to specify file extensions to manage in your settings")
            return

        lastImport = self.getSetting("Paths/LastImport")

        importFrom = QFileDialog.getExistingDirectory(self, "Choose a Path to Import From", lastImport)
        
        if importFrom in (None,  ''):
            return
        
        if not os.path.exists(importFrom) or os.path.isfile(importFrom):
            QMessageBox.warning(self, "Import Failed", "The import directory either doesn't exist, or is not a directory")
            return

        if importFrom == libPath:
            QMessageBox.warning(self, "Import Failed", "Your import directory and library directory can not be the same")
            return

        imd = ImportMetadataDialog(self)

        if imd.exec_():
            album = imd.albumEdit.text()
            comments = imd.commentsEdit.text()
            keywords = imd.keywordsEdit.text()
            
            if album and album not in (None, ''):
                albumpath = album + os.sep
            else:
                album = None
                albumpath = ""
            
            if not keywords or keywords in (None, ''):
                keywords = ""

            if not comments or comments in (None, ''):
                comments = ""

            paths = self.buildFileList(importFrom)
            numTotal = len(paths)
            
            nonDupes = self.removeDuplicates(paths, importFrom, albumpath)
            numDuplicates = numTotal - len(nonDupes)
            
            if QMessageBox.question(self, "Import", "Out of %d photos found, %d look to be duplicates. Continue with import?"
                                    % (numTotal,  numDuplicates), QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                
                settings.setValue("Paths/LastImport", QVariant(importFrom))
                
                for path in nonDupes:
                    dest = self.buildLibPath(importFrom, path, albumpath)
                    self.copyFileIncludingDirectories(path, dest)
                    # TODO Handle copy failure exceptions!
                    
                    if not os.path.exists(dest):
                        QMessageBox.warming(self, "Import Failed", "The file <%s> was not imported properly, aborting import" % (path))
                        return

                    self.buildSideCarFile(path, dest, comments, keywords)
                    # add file info to DB
                
                QMessageBox.information(self, "Import", "Import completed")
                #verify all files again?

                self.loadLibrary()

    def buildSideCarFile(self, path, dest, comments, keywords):
        sidecarFilePath = dest + os.extsep + "sidecar"
        f = open(sidecarFilePath, "w")
        f.write("originalpath=" + path + "\n")
        f.write("keywords=%s\n" % (keywords))
        f.write("comment=%s\n" % (comments))
        f.write("exif:\n")
        f.close()
        # read info from file and populate sidecar

            
    def buildLibPath(self, importFrom, path, albumpath):
        relPath = path[len(importFrom):]
        libPath = self.getSetting("Paths/Library") + os.sep + albumpath + relPath
        
        return libPath

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


    def getSetting(self, setting, default=None):
        settings = QSettings()
        return unicode(settings.value(setting, default).toString())

        
    def isImageFile(self, filepath):
        extensionList = unicode(self.getSetting("FileExtensions")).split(",")
        for extension in extensionList:
            if unicode(filepath).upper().endswith(unicode(extension).upper()):
                return True
        return False
        
    def removeDuplicates(self, paths, importFrom, albumpath):
        nonDupes = []
        
        for path in paths:
            libPath = self.buildLibPath(importFrom, path, albumpath)
            if not os.path.exists(libPath):
                nonDupes.append(path)
        
        return nonDupes

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


def doMain():
    app = QApplication(sys.argv)
    app.setOrganizationName("Three37")
    app.setOrganizationDomain("three37.com.au")
    app.setApplicationName("nPhoto")
    form = NPhotoMainWindow()
    form.show()
    app.exec_()

if __name__ == "__main__":
    doMain()
