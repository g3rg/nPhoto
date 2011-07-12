'''
Created on 12/07/2011
@author g3rg
'''

from PyQt4.QtCore import QSettings, QVariant

def getSettingQVar(setting, default=None):
    settings = QSettings()
    return settings.value(setting, QVariant(default))

def getSettingStr(setting, default=None):
    return unicode(getSettingQVar(setting, default).toString())

def saveSetting(setting, value):
    QSettings().setValue(setting, QVariant(value))
