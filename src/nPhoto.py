'''
Created on 02/07/2011
@author g3rg
'''

import os
import sys
import shutil
import datetime
import functools

from PyQt4.QtCore import Qt, QTime, QTimer, QVariant, QPoint, QSize, SIGNAL, SLOT
from PyQt4.QtGui import QApplication, QLabel, QImage, QMainWindow, QPixmap, QGridLayout, QLineEdit, \
     QMessageBox, QFileDialog, QTreeWidget, QTreeWidgetItem, QSplitter, QScrollArea, QPalette, \
     QSizePolicy, QFrame, QBoxLayout, QPushButton

from models import Photo, Album
from dialogs import EditPhotoDialog, ImportMetadataDialog, SettingsDialog
from fileutils import copyFileIncludingDirectories, loadExif, loadQPixMap
from qtutils import getSettingStr, getSettingQVar, saveSetting, addActions, createAction
from constants import EXIF_TAGS

__version__ = "0.1.0"

BROWSER_GRID_WIDTH = 4
BROWSER_GRID_HEIGHT = 3
BROWSER_THUMBS_PER_PAGE = BROWSER_GRID_WIDTH * BROWSER_GRID_HEIGHT
    
class NPhotoMainWindow(QMainWindow):
    rootAlbum = None
    currentPage = 0
    
    def __init__(self, parent=None):
        super(NPhotoMainWindow, self).__init__(parent)

        self.image = None 
        self.status = self.statusBar()
        self.status.setSizeGripEnabled(False)

        fileMenu = self.menuBar().addMenu("&File")
        fileEditAction = createAction(self, "&Edit", self.doEdit, "Ctrl-E", "fileedit", "Edit photo details")
        fileImportAction = createAction(self, "&Import", self.doImport, "Ctrl-I", "fileimport", "Import photos into your library")
        fileRescanLibraryAction = createAction(self, "&Rescan", self.doRescan, "Ctrl-R", "filerescan", "Rescan library folder and update sidecar files")
        fileBackupAction = createAction(self, "&Backup", self.doBackup, "Ctrl-B", "filebkup", "Backup your library")
        fileSettingsAction = createAction(self, "&Settings", self.doSettings, "Ctrl-S", "filesettings", "Settings")
        fileQuitAction = createAction(self, "&Quit", self.close, "Ctrl+Q", "filequit", "Close the application")

        helpMenu = self.menuBar().addMenu("&Help")
        helpAboutAction = createAction(self, "&About", self.doAbout, None, "helpabout", "About nPhoto")
        
        addActions(fileMenu, (fileEditAction, fileImportAction, fileRescanLibraryAction, fileBackupAction,
                                       fileSettingsAction, None, fileQuitAction))
        addActions(helpMenu, (helpAboutAction,))
    
        size = getSettingQVar("MainWindow/Size", QSize(600,500)).toSize()
        self.resize(size)
        position = getSettingQVar("MainWindow/Position", QPoint(0,0)).toPoint()
        self.move(position)
        self.restoreState(getSettingQVar("MainWindow/State").toByteArray())
        self.setWindowTitle("nPhoto")

        self.controlFrame = QFrame()
        self.controlLayout = QBoxLayout(QBoxLayout.TopToBottom)

        #TODO Make this a combo box that populates the tree by date or by folder
        self.viewByCombo = QLabel("PLACEHOLDER")
        
        self.tree = QTreeWidget()

        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Album"])
        self.tree.setItemsExpandable(True)

        self.connect(self.tree, SIGNAL("itemSelectionChanged()"), self.treeSelection)

        self.controlLayout.addWidget(self.viewByCombo)
        self.controlLayout.addWidget(self.tree)

        self.controlFrame.setLayout(self.controlLayout)

        self.browserFrame = QFrame()

        self.browserGrid = QGridLayout()

        self.imageLabels = []
        for row in range(0,BROWSER_GRID_HEIGHT):
            self.imageLabels.append([])
            for col in range(0,BROWSER_GRID_WIDTH):
                self.imageLabels[row].append(QLabel())
                self.imageLabels[row][col].setBackgroundRole(QPalette.Base)
                self.imageLabels[row][col].setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                self.imageLabels[row][col].setScaledContents = True
                self.imageLabels[row][col].setAlignment(Qt.AlignCenter)
                self.imageLabels[row][col].setStyleSheet("border:2px solid #000")

                dbl = functools.partial(self.imgDoubleClick, row, col)
                click = functools.partial(self.imgMouseRelease, row, col)
                
                self.imageLabels[row][col].mouseDoubleClickEvent = dbl
                self.imageLabels[row][col].mouseReleaseEvent = click
                self.browserGrid.addWidget(self.imageLabels[row][col],row,col)

        self.prevPage = QPushButton("Prev")
        self.pageInfoLabel = QLabel("Page 0 of 0")
        self.pageInfoLabel.setAlignment(Qt.AlignCenter)
        self.nextPage = QPushButton("Next")

        self.prevPage.clicked.connect(self.goPreviousPage)
        self.nextPage.clicked.connect(self.goNextPage)
        
        self.browserGrid.addWidget(self.prevPage, row+1, 0)
        self.browserGrid.addWidget(self.pageInfoLabel, row+1, 1)
        self.browserGrid.addWidget(self.nextPage, row+1, 2)

        self.browserFrame.setLayout(self.browserGrid)

        self.mainSplitter = QSplitter(Qt.Horizontal)
        self.mainSplitter.addWidget(self.controlFrame)
        self.mainSplitter.addWidget(self.browserFrame)
        self.mainSplitter.setStretchFactor(1,4)
        
        self.setCentralWidget(self.mainSplitter)

        self.mainSplitter.restoreState(getSettingQVar("MainWindow/Splitter").toByteArray())

        if getSettingStr("Paths/Library") not in (None, ''):
            QTimer.singleShot(0, self.loadLibrary)
        else:
            self.status.showMessage("No Library Path in settings", 10000)

    def getPhotoByBrowserLocation(self, row, col):
        idx = ((self.currentPage - 1) * BROWSER_THUMBS_PER_PAGE) + (row * BROWSER_GRID_WIDTH) + col
        return self.currentAlbum.photos[idx]

    def imgDoubleClick(self, row, col, event):

        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ControlModifier or event.modifiers() & Qt.AltModifier \
                    or event.modifiers() & Qt.ShiftModifier:
                pass
            else:
                self.currentSelection = [self.getPhotoByBrowserLocation(row,col),]
                self.doEdit()        

    def imgMouseRelease(self, row, col, event):
        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ControlModifier or event.modifiers() & Qt.AltModifier \
                or event.modifiers() & Qt.ShiftModifier:
                pass
            else:                
                pass
                #TODO Add or remove current image from self.currentSelection

    def doRescan(self):
        pass

    def treeSelection(self):
        curr = self.tree.currentItem()
        path = curr.data(0,0).toString()
        tmp = curr
        while tmp.parent() is not None:
            tmp = tmp.parent()
            path = tmp.data(0,0).toString() + "." + path

        album = self.getAlbum(path)
        if hasattr(self, 'currentAlbum'):
            if self.currentAlbum != album:
                self.currentAlbum = album
        else:
            self.currentAlbum = album
        self.changeAlbums()

    def changeAlbums(self):
        if len(self.currentAlbum.photos) == 0:
            self.currentPage = 0
        else:
            self.currentPage = 1
        
        for row in range(0, BROWSER_GRID_HEIGHT):
            for col in range(0, BROWSER_GRID_WIDTH):
                if len(self.currentAlbum.photos)<= (row*BROWSER_GRID_WIDTH + col):
                    self.imageLabels[row][col].setPixmap(QPixmap())
                else:
                    self.imageLabels[row][col].setPixmap(loadQPixMap(self.image, self.currentAlbum.photos[
                            (BROWSER_THUMBS_PER_PAGE * (self.currentPage - 1)) + row*BROWSER_GRID_WIDTH+col]
                                                                          .path, self.imageLabels[0][0].width(), self.imageLabels[0][0].height()))
                    self.imageLabels[row][col].adjustSize()

        self.updatePageInfo()

    def loadPageThumbs(self):
        for row in range(0, BROWSER_GRID_HEIGHT):
            for col in range(0, BROWSER_GRID_WIDTH):
                if len(self.currentAlbum.photos)<= (
                            (BROWSER_THUMBS_PER_PAGE * (self.currentPage - 1)) + row*BROWSER_GRID_WIDTH + col):
                    self.imageLabels[row][col].setPixmap(QPixmap())
                else:
                    self.imageLabels[row][col].setPixmap(self.loadQPixMap(self.image, self.currentAlbum.photos[
                            (BROWSER_THUMBS_PER_PAGE * (self.currentPage - 1)) + row*BROWSER_GRID_WIDTH+col]
                                                                          .path, self.imageLabels[0][0].width(), self.imageLabels[0][0].height()))
                    self.imageLabels[row][col].adjustSize()


    def goPreviousPage(self):
        if self.currentPage > 1:
            self.currentPage -= 1
            self.loadPageThumbs()
            self.updatePageInfo()

    def goNextPage(self):
        if self.currentPage < self.getMaxPage():
            self.currentPage += 1
            self.loadPageThumbs()
            self.updatePageInfo()

    def getMaxPage(self):
        totalPages = len(self.currentAlbum.photos) / BROWSER_THUMBS_PER_PAGE
        if (len(self.currentAlbum.photos) % BROWSER_THUMBS_PER_PAGE) != 0:
            totalPages += 1
        return totalPages
        

    def updatePageInfo(self):
        if self.currentPage == 0:
            self.pageInfoLabel.setText("Page 0 of 0")
        else:
            self.pageInfoLabel.setText("Page %d of %d" % (self.currentPage, self.getMaxPage()))
                                                   
    def getAlbum(self, path):
        nodes = path.split(".")
        if nodes[0] != 'Library':
            print "WTF?!?!?!"
        else:
            album = self.rootAlbum
            for albumName in nodes[1:]:
                album = album.albums[unicode(albumName)]

            return album
        
    def doBackup(self):
        libDir = getSettingStr("Paths/Library")
        bkupPaths = getSettingStr("Paths/Backup")
        
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


    def doEdit(self):
        if hasattr(self, "currentSelection"):
            if len(self.currentSelection) == 1:
                ph = self.currentSelection[0]
                comment = ph.comment
                keywords = (" ".join(ph.keywords)).strip()
                dialog = EditPhotoDialog(self, ph.path, comment, keywords)
                if dialog.exec_():
                    ph.comment = unicode(dialog.commentEdit.text()).strip()
                    ph.keywords = unicode(dialog.keywordEdit.text()).strip().split(" ")
                    ph.save(ph.path)

    def doSettings(self):
        libPath = getSettingStr("Paths/Library", "")
        backupPaths = getSettingStr("Paths/Backup", "")
        fileExt = getSettingStr("FileExtensions", "jpg, CR2")
        fileExtOther = getSettingStr("FileExtensionsOther", "mov, avi")
        
        
        dialog = SettingsDialog(self, libPath, backupPaths, fileExt, fileExtOther)
        if dialog.exec_():
            saveSetting("Paths/Library", dialog.libPathEdit.text())
            saveSetting("Paths/Backup", dialog.backupPathsEdit.text())
            saveSetting("FileExtensions", dialog.fileExtensionEdit.text())
            saveSetting("FileExtensionsOther", dialog.fileExtensionOtherEdit.text())
            
            self.status.showMessage("Settings updated", 5000)
            

    def buildTree(self, parentNode, parentAlbum):
        for name in parentAlbum.albums:
            childNode = QTreeWidgetItem(parentNode, [name])
            childAlbum = parentAlbum.albums[name]
            if childAlbum.albums != None and len(childAlbum.albums) > 0:
                self.buildTree(childNode, childAlbum)

    def loadLibrary(self):
        self.status.showMessage("Loading Photo Library")

        self.rootAlbum = self.loadAlbum(getSettingStr("Paths/Library"), "Library")

        if self.rootAlbum == None:
            self.rootAlbum = Album(name="Library")

        self.refreshTree()
        
        self.status.showMessage("Library successfully loaded", 5000)

    def refreshTree(self):
        self.tree.clear()
        node = QTreeWidgetItem(self.tree, ["Library"])
        self.buildTree(node, self.rootAlbum)
        self.tree.setCurrentItem(node)

    def loadAlbum(self, path, title = None):
        album = Album()
        if title not in (None, ''):
            album.name = title
        else:
            album.name = path[path.rfind(os.sep)+1:]
            
        album.albums = {}
        album.photos = []
        album.path = path

        files = os.listdir(path)
        files.sort()

        tmpPhotos = []
        for fl in files:
            if not os.path.isfile(path + os.sep + fl):
                album.albums[fl] = self.loadAlbum(path + os.sep + fl)
            else:
                if self.isImageFile(path + os.sep + fl):
                    ph = None
                    if os.path.exists(path + os.sep + fl + ".sidecar"):
                        ph = Photo.load(path + os.sep + fl + ".sidecar")
                    else:
                        ph = Photo()
                        ph.comment = ""
                        ph.keywords = {}
                        ph.srcPath = None
                        ph.path = path + os.sep + fl
                        exif = loadExif(path + os.sep + fl, EXIF_TAGS)
                        ph.setExif(exif)
                        ph.save(path + os.sep + fl)

                    ph.path = path + os.sep + fl
                    tmpPhotos.append(ph)

        album.photos = sorted(tmpPhotos, key = lambda photo: photo.date)
        return album

##    def loadFile(self, fname):
##        if fname:
##            self.image = QImage(fname)
##            if self.image.isNull():
##                message = "Failed to read %s" % fname
##            else:
##                width = self.image.width()
##                height = self.image.height()
##                image = self.image.scaled(width, height, Qt.KeepAspectRatio)
##                for row in range(0,len(self.imageLabels)):
##                    for col in range(0,len(self.imageLabels[row])):
##                        self.imageLabels[row][col].setPixmap(QPixmap.fromImage(image))
##                        
##                message = "Loaded %s" % fname
##
##            self.status.showMessage(message, 10000)


    def doImport(self):
        libPath = getSettingStr("Paths/Library")
        fileExt = getSettingStr("FileExtensions")
        
        if libPath in (None,  ''):
            QMessageBox.warning(self, "Import Failed",  "You need to specify a library directory in your settings")
            return
        
        if not os.path.exists(libPath) or os.path.isfile(libPath):
            QMessageBox.warning(self, "Import Failed", "The library directory in your settings either doesn't exist, or its not a directory")
            return
            
        if not fileExt or fileExt in (None, ''):
            QMessageBox.warning(self, "Import Failed", "You need to specify file extensions to manage in your settings")
            return

        lastImport = getSettingStr("Paths/LastImport")

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
            
            if QMessageBox.question(self, "Import", "Out of %d files found, %d look to be duplicates. Continue with import?"
                                    % (numTotal,  numDuplicates), QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                
                saveSetting("Paths/LastImport", importFrom)
                
                for path in nonDupes:
                    dest = self.buildLibPath(importFrom, path, albumpath)
                    copyFileIncludingDirectories(path, dest)
                    # TODO Handle copy failure exceptions!
                    
                    if not os.path.exists(dest):
                        QMessageBox.warming(self, "Import Failed", "The file <%s> was not imported properly, aborting import" % (path))
                        return
                    if self.isImageFile(path):
                        exif = loadExif(unicode(path), EXIF_TAGS)
                        ph = Photo()
                        ph.path = dest
                        ph.srcPath = path
                        ph.comment = comments
                        ph.keywords = keywords
                        ph.setExif(exif)

                        ph.save(dest)
                        
                QMessageBox.information(self, "Import", "Import completed")

                self.loadLibrary()
            
    def buildLibPath(self, importFrom, path, albumpath):
        relPath = path[len(importFrom):]
        libPath = getSettingStr("Paths/Library") + os.sep + albumpath + relPath
        
        return libPath

        
    def isImageFile(self, filepath):
        extensionList = unicode(getSettingStr("FileExtensions")).split(",")
        for extension in extensionList:
            if unicode(filepath).upper().endswith(unicode(extension).upper()):
                return True
        return False

    def isOtherManagedFile(self, filepath):
        #TODO Implement list of other files to import into lib folders and to backup
        extensionList = unicode(getSettingStr("FileExtensionsOther")).split(",")
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
        #TODO Can probably be done with Glob or whatever it is?
        paths = []
        for f in os.listdir(importFrom):
            fullpath = importFrom + os.sep + f
            
            if not os.path.isfile(fullpath):
                paths.extend(self.buildFileList(fullpath))
            else:
                if self.isImageFile(fullpath):
                    paths.append(fullpath)
                elif self.isOtherManagedFile(fullpath):
                    paths.append(fullpath)
                    
        return paths

    def closeEvent(self, event):
        saveSetting("MainWindow/Size", self.size())
        saveSetting("MainWindow/Position", self.pos())
        saveSetting("MainWindow/State", self.saveState())
        saveSetting("MainWindow/Splitter", self.mainSplitter.saveState())

    def doAbout(self):
        QMessageBox.about(self, "About nPhoto",
                "<p>nPhoto allows simple reviewing, commenting, and keywording of images, useful for running"
                                " on a netbook while travelling, to then import into programs such as Lightroom"
                                " on return from your holiday</p>")

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
