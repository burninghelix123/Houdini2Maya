#!/usr/bin/python
# -*- coding: utf-8 -*-

# PointImporter.py
# 2013 April 8

'''PointConverter.py and PointImporter.py are programs I created for
the purpose of bringing point cloud data and particle simulations from
SideFx Houdini into Autodesk Maya.

===========================================
Copyright © 2013 Craig Barnett
===========================================

This program is to be distributed only by the owner. It was created
in the hope that it will be useful to artists, but WITHOUT ANY WARRANTY.

===========================================
Craig Barnett,
302 W 40th St Apt A, Savannah, Ga 31401
mailto: craigbme@hotmail.com
http://www.bhvfx.com
===========================================

This script was developed to conveniently and quickly bring point cloud
data or simulations from Houdini into Maya. The reasons I did this were
to allow for better integration with your scene without a lot of post
work and without the problem of matching lighting. You gain the benefits
of being able to use the vast collection of Maya compatible renderers
with your simulation along with easily having multiple simulations in one
compact and fast scene.

Read First:
------------
*These tools can be used to bring point cloud data from SideFx 
 Houdini into Autodesk Maya.
*Currently this only works with Houdini's .bgeo or .pc filetype    
 but will hopefully work with more soon.
*If you are using Houdini 12 or newer you will need to 
 add .classic to the extension (.pc.classic or .bgeo.classic). 
 Houdini now uses binary files instead of ascii, .classic forces
 it back into ascii mode.
*As of now it only transfers point location and id attributes, if 
 no id exists it will create ids in order of location.
*For the second tool to work you must have Autodesk Maya installed, 
  either versions 2012 or 2013. Other versions are untested.

Three Easy Steps:
-----------------
1. Export your point cloud from Houdini into a file/files.
2. Run the Point Converter tool and select your point cloud files   
   from step 1. Give it a name, project directory, and range.
3. Run the Point Importer tool, select project directory, name 
   from previous step, and range.

Important Notes:
----------------
*This tool will create empty cache files for frames not in your  
 sequence.
*For example, if you import frames 30-50 into Maya, 1-29 will    
 automatically be empty cache files.
*A series of folders will be created in the directory you choose 
 if they don't already exist.
*Those folders are called scenes, particles, data and backup.
*Cached simulations must go in the particles folder of your project 
 directory.
*The scenes folder is for your save files. The data folder and backup
 folder are for backups of the cache and scene.
*If you modify the cache in the particles folder, you can replace the
 cache with the original in the data folder.
*It will set the current scenes project folder to whichever 
 folder you choose as the directory.
*Changing the name of the scene will normally break the cache, so 
 in order to keep backups, rename the old files instead of the new 
 ones.
*In order to change the Maya version or Autodesk directory 
 location set during installation, navigate to the install 
 folder, typically "C:\Program Files (x86)\PointImporter" and 
 open the file config.ini with any text editor, like notepad or 
 wordpad. Then change the version and save it. Depending on your 
 setup you may need administrator rights to change this file 
 after installing.
*If the simulation doesn't appear when you open the file try 
 going to File in the title menu and click on "Set Project...". In 
 the following dialog navigate to your Project Directory created
 earlier. Afterwards make sure you reset the timeline before hitting
 play again.

Using Multiple Caches:
----------------------
*When running the Point Converter Tool simply make sure you 
 change the name to something different. If you do not change
 the name it will overwrite the previous cache.
*Do NOT name your cache the same as a particle simulation you 
 already have in your scene. Doing so will erase said particle
 simulation and overwrite it with the cache.

'''


try:
    import maya.standalone
    maya.standalone.initialize()
except:
    pass
import maya.cmds as cmds
import maya.mel as mel
from time import time as tTime
from glob import iglob
from shutil import copy
from os.path import join
from PyQt4 import QtCore
from PyQt4 import QtGui
from sys import argv as sysargv
from sys import exit as sysexit

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_PointImporter(object):
    '''Main window for program'''
    cacheName = ''
    endFrame = []
    sourceFile = []
    sceneName = ''
    projectDirectory = []
    def setupUi(self, PointImporter):
        PointImporter.setObjectName(_fromUtf8("PointImporter"))
        PointImporter.resize(376, 419)
        self.centralwidget = QtGui.QWidget(PointImporter)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(110, 0, 141, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 50, 161, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.radioButton = QtGui.QRadioButton(self.centralwidget)
        self.radioButton.setGeometry(QtCore.QRect(200, 50, 82, 17))
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.radioButton_2 = QtGui.QRadioButton(self.centralwidget)
        self.radioButton_2.setGeometry(QtCore.QRect(270, 50, 82, 17))
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(20, 90, 131, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit.setEnabled(False)
        self.lineEdit.setGeometry(QtCore.QRect(130, 90, 171, 20))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(300, 90, 61, 23))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton.clicked.connect(self.browseDialog)
        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(10, 140, 121, 21))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.lineEdit_2 = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit_2.setEnabled(True)
        self.lineEdit_2.setGeometry(QtCore.QRect(130, 140, 171, 20))
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(300, 140, 61, 23))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.pushButton_2.clicked.connect(self.browseDialog2)
        self.label_5 = QtGui.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(30, 190, 91, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.lineEdit_3 = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit_3.setEnabled(True)
        self.lineEdit_3.setGeometry(QtCore.QRect(130, 190, 171, 20))
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.lineEdit_3.textChanged.connect(self.getName)
        self.lineEdit_3.cursorPositionChanged.connect(self.getName)
        self.label_6 = QtGui.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(40, 240, 81, 20))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.lineEdit_4 = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit_4.setEnabled(True)
        self.lineEdit_4.setGeometry(QtCore.QRect(130, 240, 171, 20))
        self.lineEdit_4.setObjectName(_fromUtf8("lineEdit_4"))
        self.lineEdit_4.textChanged.connect(self.getName)
        self.lineEdit_4.cursorPositionChanged.connect(self.getName2)
        self.label_7 = QtGui.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(60, 300, 61, 16))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.spinBox = QtGui.QSpinBox(self.centralwidget)
        self.spinBox.setGeometry(QtCore.QRect(130, 300, 171, 22))
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.spinBox.valueChanged.connect(self.endFrame)
        self.spinBox.setRange(0,10000)
        self.pushButton_3 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(210, 350, 75, 23))
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.pushButton_3.clicked.connect(self.create)
        self.pushButton_4 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(290, 350, 75, 23))
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.pushButton_4.clicked.connect(self.close)
        self.label_8 = QtGui.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(70, 260, 231, 20))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.label_9 = QtGui.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(90, 70, 221, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.label_10 = QtGui.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(130, 320, 201, 21))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.label_11 = QtGui.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(120, 210, 211, 20))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(7, 120, 361, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.label_12 = QtGui.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(120, 160, 181, 21))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        PointImporter.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(PointImporter)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        PointImporter.setStatusBar(self.statusbar)
        self.retranslateUi(PointImporter)
        QtCore.QMetaObject.connectSlotsByName(PointImporter)

    def retranslateUi(self, PointImporter):
        '''Name labels and ui objects'''
        PointImporter.setWindowTitle(QtGui.QApplication.translate("PointImporter", "Point Importer Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PointImporter", "Point Importer", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("PointImporter", "Do you have a previous scene?", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton.setText(QtGui.QApplication.translate("PointImporter", "Yes", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_2.setText(QtGui.QApplication.translate("PointImporter", "No", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("PointImporter", "Select Existing Scene:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("PointImporter", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("PointImporter", "Select Project Directory:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("PointImporter", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("PointImporter", "New Scene Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("PointImporter", "Cache Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("PointImporter", "End Frame:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("PointImporter", "Create", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_4.setText(QtGui.QApplication.translate("PointImporter", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("PointImporter", "(Same name as before - Do not include \"Shape\")", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("PointImporter", "(Bringing cache into an existing scene?)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("PointImporter", "(Last frame of cache)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("PointImporter", "(Name of new save file)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("PointImporter", "(Same directory as before)", None, QtGui.QApplication.UnicodeUTF8))

    def create(self):
        '''Create Maya scene file'''
        if (self.radioButton.isChecked()):
            cmds.file(self.sourceFile, o=True)
        endFrameCurrent = cmds.playbackOptions(query=True,maxTime=True)
        endFrameFloat = float(self.endFrame)
        if (endFrameCurrent < endFrameFloat):
            cmds.playbackOptions(minTime='1', maxTime=self.endFrame)
        time = tTime()
        cmds.file(rename = str(self.projectDirectory + "\\scenes\\" + self.sceneName + ".mb"))
        cmds.file(save=1)
        stringDirectory = str(self.projectDirectory)
        outputDirectoryTemp = stringDirectory.replace("\\","/");
        cacheDirectory = outputDirectoryTemp + '/particles/'
        startFrame = 1
        mel.eval('setProject "' + outputDirectoryTemp + '";')
        mel.eval('particle -name "' + str(self.cacheName) + '";')
        mel.eval('dynExport -f "cache" -mnf 1 -mxf ' + str(self.endFrame) +' -oup 0 ' + str(self.cacheName) + ';')
        newCacheName = str(self.cacheName) + 'Shape'
        cacheFile1 = outputDirectoryTemp + '/data/' + newCacheName + '.*'        
        for fname in iglob(cacheFile1):
            copy(fname, join(cacheDirectory))
        cmds.currentTime(1)
        cmds.file(rename = str(self.projectDirectory + "\\scenes\\" + self.sceneName + ".mb"))
        cmds.file(save=1)
        
    def close(self):
        sysexit(app.exec_())
        
    def endFrame(self, spinBox):
        self.endFrame = self.spinBox.value()

    def browseDialog(self, *args):
        '''Browse dialog to choose scene file'''
        dialog = QtGui.QFileDialog.getOpenFileName(caption = 'Select your existing scene',
                                                    filter = 'Maya Scene Files (*.ma *.mb)')
        self.lineEdit.setText(str(dialog))
        self.sourceFile = str(dialog)

    def browseDialog2(self, *args):
        '''Browse dialog to choose directory'''
        dialog2 = QtGui.QFileDialog.getExistingDirectory(caption = 'Select your project directory')
        self.lineEdit_2.setText(dialog2)
        self.projectDirectory = dialog2

    def getName(self, lineEdit_3):
        self.sceneName = self.lineEdit_3.text()

    def getName2(self, lineEdit_4):
        self.cacheName = self.lineEdit_4.text()


if __name__ == "__main__":
    app = QtGui.QApplication(sysargv)
    PointImporter = QtGui.QMainWindow()
    ui = Ui_PointImporter()
    ui.setupUi(PointImporter)
    PointImporter.show()
    sysexit(app.exec_())
