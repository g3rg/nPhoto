'''
Created on 02/07/2011
@author g3rg
'''

import os
import sys
import shutil
import datetime

from PyQt4.QtCore import Qt, QTime, QTimer, QSettings, QVariant, QPoint, QSize, SIGNAL
from PyQt4.QtGui import QApplication, QLabel, QImage, QMainWindow, QPixmap, QAction, QIcon

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
        #Add Import menu option
        fileImportAction = self.createAction("&Import", self.doImport, "Ctrl-I", "fileimport", "Import photos into your library")
        #Add Backup menu option
        fileBackupAction = self.createAction("&Backup", self.doBackup, "Ctrl-B", "filebkup", "Backup your library")
        #Add Settings menu option
        fileSettingsAction = self.createAction("&Action", self.doSettings, "Ctrl-S", "filesettings", "Settings")
        
        #Add Separator
        #Add Quit menu option
        fileQuitAction = self.createAction("&Quit", self.close, "Ctrl+Q", "filequit", "Close the application")

        self.addActions(fileMenu, (fileImportAction, fileBackupAction, fileSettingsAction, None, fileQuitAction))


    
        settings = QSettings()
        size = settings.value("MainWindow/Size", QVariant(QSize(600,500))).toSize()
        self.resize(size)
        position = settings.value("MainWindow/Position", QVariant(QPoint(0,0))).toPoint()
        self.move(position)
        self.restoreState(settings.value("MainWindow/State").toByteArray())
        self.setWindowTitle("nPhoto")

        if settings.value("LibraryPath").toString() not in (None, ''):
            QTimer.singleShot(0, self.loadLibrary)
        else:
            self.status.showMessage("No Library Path in settings", 10000)

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def doImport(self):
        print "Importing"

    def doBackup(self):
        print "Backing up"

    def doSettings(self):
        print "Show settings"

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

    def loadAlbum(self, albumName):
        pass

    def loadLibrary(self):
        self.status.showMessage("Loading Photo Library")

        if self.rootAlbum == None:
            self.rootAlbum = Album(name="Library")

        self.loadAlbum(self.rootAlbum)
        self.loadInitialPhoto()

        self.status.showMessage("Library successfully loaded", 5000)

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
        print "Closing"
        settings = QSettings()
        #Last file / album?
        settings.setValue("MainWindow/Size", QVariant(self.size()))
        settings.setValue("MainWindow/Position", QVariant(self.pos()))
        settings.setValue("MainWindow/State", QVariant(self.saveState()))
        print "Closed"
        
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
