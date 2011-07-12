''' Created on 02/07/2011 @author g3rg '''

import os
import sys
import shutil
import datetime

import Image
import ExifTags


from PyQt4.QtCore import Qt, QTime, QTimer, QSettings, QVariant, QPoint, QSize, SIGNAL, SLOT
from PyQt4.QtGui import QApplication, QLabel, QImage, QMainWindow, QPixmap, QAction, \
            QIcon, QDialog, QDialogButtonBox, QGridLayout, QLineEdit, QMessageBox, QFileDialog, QTreeWidget, \
            QTreeWidgetItem, QSplitter, QScrollArea, QPalette, QSizePolicy, QFrame, QBoxLayout

from models import Photo, Album
from dialogs import EditPhotoDialog, ImportMetadataDialog, SettingsDialog
from fileutils import copyFileIncludingDirectories

__version__ = "0.1.0"

EXIF_TAGS= ('DateTimeOriginal','ExifImageWidth','Make','Model','Orientation','DateTime','ExifImageHeight')

class NPhotoMainWindow(QMainWindow):
    rootAlbum = None

    def __init__(self, parent=None):
        super(NPhotoMainWindow, self).__init__(parent)

        self.status = self.statusBar()
        self.status.setSizeGripEnabled(False)

        fileMenu = self.menuBar().addMenu("&File")
        fileEditAction = self.createAction("&Edit", self.doEdit, "Ctrl-E", "fileedit", "Edit photo details")
        fileImportAction = self.createAction("&Import", self.doImport, "Ctrl-I", "fileimport", "Import photos into your library")
        fileRescanLibraryAction = self.createAction("&Rescan", self.doRescan, "Ctrl-R", "filerescan", "Rescan library folder and update sidecar files")
        fileBackupAction = self.createAction("&Backup", self.doBackup, "Ctrl-B", "filebkup", "Backup your library")
        fileSettingsAction = self.createAction("&Settings", self.doSettings, "Ctrl-S", "filesettings", "Settings")
        fileQuitAction = self.createAction("&Quit", self.close, "Ctrl+Q", "filequit", "Close the application")

        helpMenu = self.menuBar().addMenu("&Help")
        helpAboutAction = self.createAction("&About", self.doAbout, None, "helpabout", "About nPhoto")
        
        self.addActions(fileMenu, (fileEditAction, fileImportAction, fileRescanLibraryAction, fileBackupAction,
                                       fileSettingsAction, None, fileQuitAction))
        self.addActions(helpMenu, (helpAboutAction,))
    
        settings = QSettings()
        size = settings.value("MainWindow/Size", QVariant(QSize(600,500))).toSize()
        self.resize(size)
        position = settings.value("MainWindow/Position", QVariant(QPoint(0,0))).toPoint()
        self.move(position)
        self.restoreState(settings.value("MainWindow/State").toByteArray())
        self.setWindowTitle("nPhoto")

        self.controlFrame = QFrame()
        self.controlLayout = QBoxLayout(QBoxLayout.TopToBottom)

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
        for row in range(0,3):
            self.imageLabels.append([])
            for col in range(0,3):
                
                self.imageLabels[row].append(QLabel())
                self.imageLabels[row][col].setBackgroundRole(QPalette.Base)
                self.imageLabels[row][col].setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                self.imageLabels[row][col].setScaledContents = True
                self.imageLabels[row][col].setAlignment(Qt.AlignCenter)

                self.browserGrid.addWidget(self.imageLabels[row][col],row,col)

        self.browserFrame.setLayout(self.browserGrid)



        self.mainSplitter = QSplitter(Qt.Horizontal)
        self.mainSplitter.addWidget(self.controlFrame)
        self.mainSplitter.addWidget(self.browserFrame)
        self.mainSplitter.setStretchFactor(1,4)
        
        self.setCentralWidget(self.mainSplitter)

        self.mainSplitter.restoreState(settings.value("MainWindow/Splitter").toByteArray())

        if settings.value("Paths/Library").toString() not in (None, ''):
            QTimer.singleShot(0, self.loadLibrary)
        else:
            self.status.showMessage("No Library Path in settings", 10000)

    def doRescan(self):
        pass

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

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
        for row in range(0, 3):
            for col in range(0, 3):
                if len(self.currentAlbum.photos)<= (row*3 + col):
                    self.imageLabels[row][col].setPixmap(QPixmap())
                else:
                    self.imageLabels[row][col].setPixmap(self.loadQPixMap(self.currentAlbum.photos[row*3+col].path))
                    self.imageLabels[row][col].adjustSize()
                                                   
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


    def doEdit(self):
        comment = "No Comment"
        keywords = "one two three"
        dialog = EditPhotoDialog(self, comment, keywords)
        if dialog.exec_():
            print "Editing!"

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
        pass

    def buildTree(self, parentNode, parentAlbum):
        for name in parentAlbum.albums:
            childNode = QTreeWidgetItem(parentNode, [name])
            childAlbum = parentAlbum.albums[name]
            if childAlbum.albums != None and len(childAlbum.albums) > 0:
                self.buildTree(childNode, childAlbum)

    def loadLibrary(self):
        self.status.showMessage("Loading Photo Library")

        self.rootAlbum = self.loadAlbum(self.getSetting("Paths/Library"), "Library")

        if self.rootAlbum == None:
            self.rootAlbum = Album(name="Library")

        self.tree.clear()
        node = QTreeWidgetItem(self.tree, ["Library"])
        self.buildTree(node, self.rootAlbum)

        self.tree.setCurrentItem(node)
        self.loadInitialPhoto()

        self.status.showMessage("Library successfully loaded", 5000)

    def loadExif(self, path):
        img = Image.open(path)
        info = img._getexif()
        tags = {}
        for tag, value in info.items():
            decoded = ExifTags.TAGS.get(tag,tag)
            if decoded in EXIF_TAGS:
                tags[decoded] = unicode(value)

        return tags

    def loadAlbum(self, path, title = None, regenSideCar = False):
        album = Album()
        if title not in (None, ''):
            album.name = title
        else:
            album.name = path[path.rfind(os.sep)+1:]
            
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
                            exif = self.loadExif(path + os.sep + fl)
                            self.buildSideCarFile(path + os.sep + fl + ".sidecar", dest, ph.comment, ph.keywords)
                    
                            
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
                # EXIF
                if line.startsWith("DateTimeOriginal="):
                    ph.date = line[len("DateTimeOriginal="):]
                elif line.startsWith("DateTime=") and not ph.date:
                    ph.date = line[len("DateTime="):]
                elif line.startsWith("Orientation="):
                    ph.orientation = line[len("Orientation"):]
            
        f.close()
        return ph

    def loadQPixMap(self, fname):
        qpx = None
        message = ""
        if fname:
            self.image = QImage(fname)
            if self.image.isNull():
                message = "Failed to read %s" % fname
            else:
                width = self.imageLabels[0][0].width()
                height = self.imageLabels[0][0].height()
                image = self.image.scaled(width, height, Qt.KeepAspectRatio)
                qpx = QPixmap(QPixmap.fromImage(image))
                message = "Loaded %s" % fname

        self.status.showMessage(message, 10000)
        return qpx

    def loadFile(self, fname):
        if fname:
            self.image = QImage(fname)
            if self.image.isNull():
                message = "Failed to read %s" % fname
            else:
                width = self.image.width()
                height = self.image.height()
                image = self.image.scaled(width, height, Qt.KeepAspectRatio)
                for row in range(0,len(self.imageLabels)):
                    for col in range(0,len(self.imageLabels[row])):
                        self.imageLabels[row][col].setPixmap(QPixmap.fromImage(image))
                        
                message = "Loaded %s" % fname

            self.status.showMessage(message, 10000)


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
                    copyFileIncludingDirectories(path, dest)
                    # TODO Handle copy failure exceptions!
                    
                    if not os.path.exists(dest):
                        QMessageBox.warming(self, "Import Failed", "The file <%s> was not imported properly, aborting import" % (path))
                        return
                    exif = self.loadExif(unicode(path))
                    self.buildSideCarFile(path, dest, comments, keywords, exif)
                    # add file info to DB
                
                QMessageBox.information(self, "Import", "Import completed")

                self.loadLibrary()

    def buildSideCarFile(self, path, dest, comments, keywords, exif=None):
        sidecarFilePath = dest + os.extsep + "sidecar"
        f = open(sidecarFilePath, "w")
        f.write("originalpath=" + path + "\n")
        f.write("keywords=%s\n" % (keywords))
        f.write("comment=%s\n" % (comments))
        f.write("exif:\n")
        if exif:
            for tag in exif.keys():
                f.write(tag)
                f.write("=")
                f.write(exif[tag])
                f.write("\n")
        f.close()
            
    def buildLibPath(self, importFrom, path, albumpath):
        relPath = path[len(importFrom):]
        libPath = self.getSetting("Paths/Library") + os.sep + albumpath + relPath
        
        return libPath


    def getSetting(self, setting, default=None):
        settings = QSettings()
        return unicode(settings.value(setting, default).toString())

        
    def isImageFile(self, filepath):
        extensionList = unicode(self.getSetting("FileExtensions")).split(",")
        for extension in extensionList:
            if unicode(filepath).upper().endswith(unicode(extension).upper()):
                return True
        return False

    def isVideoFile(self, filepath):
        #TODO Implement list of accepted video extensions, and then work out what to do with them on import!
        pass
        
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

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue("MainWindow/Size", QVariant(self.size()))
        settings.setValue("MainWindow/Position", QVariant(self.pos()))
        settings.setValue("MainWindow/State", QVariant(self.saveState()))
        settings.setValue("MainWindow/Splitter", QVariant(self.mainSplitter.saveState()))

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
