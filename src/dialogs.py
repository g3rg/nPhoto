'''
Created on 12/07/2011
@author g3rg
'''

from PyQt4.QtCore import Qt, SIGNAL, SLOT
from PyQt4.QtGui import QDialog, QDialogButtonBox, QLabel, QLineEdit, QGridLayout, QFrame, QVBoxLayout, QSizePolicy

from fileutils import loadQPixMap


class EditPhotoDialog(QDialog):
    def __init__(self, parent, path, comment, keywords):
        super(EditPhotoDialog, self).__init__(parent)
        controlframe = QFrame()
        self.image = None
        
        self.imgLabel = QLabel()
        self.imgLabel.setPixmap(loadQPixMap(self.image, path, self.imgLabel.width(), self.imgLabel.height()))
        self.imgLabel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        #self.imgLabel.setScaledContents = True
        self.imgLabel.setAlignment(Qt.AlignCenter)
        
        commentLabel = QLabel("Comment")
        self.commentEdit = QLineEdit(comment)
        keywordLabel = QLabel("Keyword")
        self.keywordEdit = QLineEdit(keywords)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.connect(buttonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.setWindowTitle("Edit Photo")

        grid = QGridLayout()
        grid.addWidget(commentLabel, 0, 0)
        grid.addWidget(self.commentEdit, 0, 1)
        grid.addWidget(keywordLabel, 1, 0)
        grid.addWidget(self.keywordEdit, 1, 1)

        grid.addWidget(buttonBox, 2, 0, 1, 2)
        controlframe.setLayout(grid)

        box = QVBoxLayout()
        
        box.addWidget(self.imgLabel)
        box.addWidget(controlframe)

        self.setLayout(box)

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
    def __init__(self, parent, libPath, backupPaths, extensions, extensionsOther):
        super(SettingsDialog, self).__init__(parent)

        libPathLabel = QLabel("Library Path")
        self.libPathEdit = QLineEdit(libPath)
        backupPathsLabel = QLabel("Backup Paths")
        self.backupPathsEdit = QLineEdit(backupPaths)
        fileExtensionLabel = QLabel("Image File Extensions")
        self.fileExtensionEdit = QLineEdit(extensions)
        fileExtensionOtherLabel = QLabel("Other Extensions")
        self.fileExtensionOtherEdit = QLineEdit(extensionsOther)

        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        self.connect(buttonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.setWindowTitle("Settings")

        grid = QGridLayout()
        
        grid.addWidget(libPathLabel, 0, 0)
        grid.addWidget(self.libPathEdit, 0, 1)
        grid.addWidget(backupPathsLabel, 1, 0)
        grid.addWidget(self.backupPathsEdit, 1, 1)
        grid.addWidget(fileExtensionLabel, 2, 0)
        grid.addWidget(self.fileExtensionEdit, 2, 1)
        grid.addWidget(fileExtensionOtherLabel, 3, 0)
        grid.addWidget(self.fileExtensionOtherEdit, 3, 1)
        
        grid.addWidget(buttonBox, 4, 0, 1, 2)
        self.setLayout(grid)
