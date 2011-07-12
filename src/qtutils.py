'''
Created on 12/07/2011
@author g3rg
'''

from PyQt4.QtCore import QSettings, QVariant, SIGNAL, SLOT
from PyQt4.QtGui import QAction, QIcon


def getSettingQVar(setting, default=None):
    settings = QSettings()
    return settings.value(setting, QVariant(default))

def getSettingStr(setting, default=None):
    return unicode(getSettingQVar(setting, default).toString())

def saveSetting(setting, value):
    QSettings().setValue(setting, QVariant(value))

def addActions(target, actions):
    for action in actions:
        if action is None:
            target.addSeparator()
        else:
            target.addAction(action)

def createAction(parent, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
    action = QAction(text, parent)
    if icon is not None:
        action.setIcon(QIcon(":/%s.png" % icon))
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    if slot is not None:
        parent.connect(action, SIGNAL(signal), slot)
    if checkable:
        action.setCheckable(True)
    return action
