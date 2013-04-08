#!/usr/bin/python
# -*- coding: utf-8 -*-

# PointConverter.py
# PointImporter.py
# 2013 April 8

'''PointConverter.py and PointImporter.py are programs I created for the purpose of bringing
point cloud data and particle simulations from SideFx Houdini into
Autodesk Maya.

===========================================
Copyright © 2013 Craig Barnett
===========================================

This program is to be distributed only by the owner, it was created
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
 This is because Houdini now uses binary files instead of 
 ascii, .classic forces it back into ascii mode.
*As of now it only transfers point location and id attributes, if 
 no id exists it will create ids in order of location.
*For the second tool to work you must have Autdesk Maya installed 
 versions 2012 or 2013, other versions are untested.

Three Easy Steps:
-----------------
1. Export your point cloud from Houdini into a file/files
2. Run the Point Converter tool and select your point cloud files   
   from step 1, giving it a name, project directory, and range.
3. Run the Point Importer tool, select project directory, name 
   from previous step, and range.

Important Notes:
----------------
*This tool will create empty cache files for frames not in your  
 sequence.
*For example if you import frames 30-50 into Maya, 1-29 will    
 automatically be empty cache files.
*A series of folders will be created in the directory you choose, 
 if they don't already exist.
*Those folders are called scenes, particles, data and backup.
*Cached Sims must go in the particles folder of your project 
 directory.
*The scenes folder is your saves, data folder and backup folder 
 are for backups of the cache and scene.
*This way if you modify the cache in the particles folder, you 
 can replace it with the original in the data folder.
*It will set the current scenes project folder to whichever 
 folder you choose as the directory.
*Changing the name of the scene will normally break the cache, so 
 in order to keep backups rename the old files instead of the new 
 ones.
*In order to change the Maya version or Autodesk directory 
 location set during installation, navigate to the install 
 folder, typically "C:\Program Files (x86)\PointImporter" and 
 open the file config.ini with any text editor, like notepad or 
 wordpad and change the version then save it, depending on your 
 setup you may need adminisitrator right to change this file 
 after installing.
*If the simulation doesn't appear when you open the file try 
 going to File in the title menu then click on Set Project... and 
 navigate to your Project Directory, afterwards make sure you 
 reset the timeline before hitting play again.

Using Multiple Caches:
----------------------
*When running the Point Converter Tool simply make sure you 
 change the name to something different.
*If you do not change the name it will overwrite the previous 
 cache.
*Do NOT name your cache the same as a particle simulation you 
 already have in your scene.
*Doing so will erase said particle simulation and overwrite it 
 with the cache.

'''


from re import search
from re import split as resplit
from sys import argv as sysargv
from sys import exit as sysexit
from os import path
from os import makedirs
from struct import pack
from struct import Struct
from PyQt4 import QtCore
from PyQt4 import QtGui
from multiprocessing import Process
from multiprocessing import Lock
from multiprocessing import freeze_support
from time import time
from warnings import warn

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

def convertPcToPdc(deffile, particlesName, startframe, endframe, pdcIncrements,
                   outputDirectory, questionasked):
    '''Converts Houdini's Point Cache file to Maya's Point Disc Cach file'''
    print "time(): %f " %  time()
    print 'ReadFile:'
    dataType = {'Integer': 0, 'Integer Array': 1, 'Double': 2,
                    'Double Array': 3, 'Vector': 4, 'Vector Array': 5}
    readFile = open(str(deffile), 'r', buffering=1024*10)
    fileContent = readFile.read()
    content = resplit('\[|\]| |', fileContent)
    readFile.close()
    count = 0
    del fileContent
    vartest = 0
    vartest1 = 0
    vartesta = 0
    vartestb = 0
    vartestc = 0
    vartestd = 0
    noIds = 0
    noCoords = 0
    for count, item in enumerate(content):
        if search('\"P\"', item):
           index1 = count
           vartest = 1
        if search('\"id\"', item):
           index2 = count
           vartest1 = 1
        if vartest == 1:
            if vartesta == 0:
                if search('$^', item):
                   if count > index1:
                       index3 = count
                       vartesta = 1
            if vartesta == 1:           
                if vartestb == 0: 
                    if search('\"', item):
                       if count > index3:
                           index4 = count
                           vartestb = 1
            if vartest1 == 1:           
                if vartestc == 0:
                    if search('$^', item):
                       if count > index2:
                           index5 = count
                           vartestc = 1   
                if vartestc == 1:
                    if vartestd == 0:
                        if search('\"', item):
                           if count > index5:
                               index6 = count
                               vartestd = 1
    if vartest == 1:
       coords = content[(index3 + 1):index4]
    if vartest == 0:
       raise RuntimeError('No Coords found in file, is this a .pc.classic or .bgeo.classic file?')
    print "time(): %f " %  time()
    print 'Grouping:'
    tempString = ','.join(str(n) for n in coords)
    del coords
    running = True
    while running:    
        if tempString[-1].isdigit() == False:
            tempString = tempString[:-1]
        else:
            running = False
    tempString += ',,,'
    print "time(): %f " %  time()
    print 'Coords: '
    s = ''.join(tempString.split())
    del tempString
    split = s.split(",")
    outputs = [' '.join(split[6*i:6*i+3]) for i in range(len(split)//6)]
    outputs = ' '.join(outputs)
    outputs = outputs.split(' ')
    coords = tuple(float(f) for f in outputs)
    del outputs
    if vartest1 == 0:
        noIds = 1
        numberofids = len(coords)/3 
        ids = range(numberofids)
        ids = [float(x) for x in ids]
        ids = tuple(ids)
    if vartest1 == 1:
        ids = content[index5:index6]
        print "time(): %f " %  time()
        print 'Ids: '
        tempString2 = ','.join(str(n) for n in ids)
        running = True
        while running:    
            if tempString2[-1].isdigit() == False:
                tempString2 = tempString2[:-1]
            else:
                running = False
        tempString2 = tempString2[1:]
        ids = tempString2.split(',')
        del tempString2
        ids = [float(x.strip()) for x in ids]
        ids = tuple(ids)
    print "time(): %f " %  time()
    print 'Set Attributes:'
    scaleFactor = 1    
    particlecount = (len(coords))
    count = 0
    num = range(len(coords))
    attributes = ['position','particleId']
    fileType = 'PDC ' 
    formatVersion = 1 
    byteOrder = 1 
    offset = -1
    extra1 = 0 
    extra2 = 0 
    particlesTotal = len(coords)/3
    print "time(): %f " %  time()
    print 'Set Header Values and records2:'
    attributesTotal = 2
    headerValues = (fileType, formatVersion, byteOrder, extra1,
                    extra2, particlesTotal, attributesTotal)
    recordsValues2 = (len(attributes[1 + offset]), attributes[1 + offset],
                      dataType['Vector Array'])
    recordsValues2 += coords
    scaleFactor = 1
    print "time(): %f " %  time()
    print 'Set Records 3:'
    recordsValues3 = (len(attributes[2 + offset]), attributes[2 + offset],
                      dataType['Double Array'])
    recordsValues3 += ids
    recordsForm = ' i{0}si{1}d i{2}si{3}d'.format(str(len(attributes[1 + offset])),
                                                      str(3* particlesTotal),
                                                      str(len(attributes[2 + offset])),
                                                      str(len(ids)))
    headerForm = '>4sii2iii'
    form = Struct(headerForm + recordsForm)
    allValues = headerValues + recordsValues2 + recordsValues3
    del headerValues
    del recordsValues2
    del recordsValues3
    del headerForm
    del recordsForm
    packedData = form.pack(*allValues)
    del allValues
    del form
    print "time(): %f " %  time()
    print 'Writing File: \n'
    fileName = particlesName + '.' + str(pdcIncrements) + ".pdc"    
    outputPDCfile = open(outputDirectory + '\\Data\\' + fileName, 'wb')
    outputPDCfile.write(packedData)
    outputPDCfile.close()
    del packedData
    print 'done'
    print "time(): %f " %  time()
    if noIds == 1:
        warn(('No Id Values were included\n'
                       'Id values were assigned based on order of particles\n'
                      'This may cause unexpected results, to fix add a id attribute in houdini'),
                      DeprecationWarning)
    
def threadedFuntion(sourceFiles,startframe,endframe,particlesName,outputDirectory,questionasked):
    """Calls the function to start multithreading"""
    threadme(sourceFiles,startframe,endframe,particlesName,
             outputDirectory,questionasked,threadlimit=6)

    
class Worker(Process):
    """Class that runs multiprocessing"""
    def __init__(self, srcfile, printlock, countfile, startframe,
                 endframe, particlesName, outputDirectory, questionasked, **kwargs):
        super(Worker,self).__init__(**kwargs)
        self.srcfile = srcfile
        self.startframe = startframe
        self.endframe = endframe
        self.particlesName = particlesName
        self.outputDirectory = outputDirectory
        self.lock = printlock
        self.countfile = countfile
        self.questionasked = questionasked

    def run(self):
        """Runs main function based on number of threads"""
        with self.lock:
            print("starting %s on %s" % (self.ident,self.srcfile))
        pdcIncrements = 250 * (self.startframe + self.countfile)
        convertPcToPdc(self.srcfile, self.particlesName, self.startframe,
                        self.endframe, pdcIncrements, self.outputDirectory,
                        self.questionasked)
        with self.lock:
            print("%s done" % self.ident)
	
def threadme(infiles,startframe,endframe,particlesName,
             outputDirectory,questionasked,threadlimit=None,timeout=0.01):
    """Creates number of threads and prepares them """
    assert threadlimit > 0, "need at least one thread";
    printlock = Lock()
    srcfiles = list(infiles)
    countfiles = range(len(infiles))
    threadpool = []
    while srcfiles or threadpool:
        while srcfiles and \
           (threadlimit is None \
            or len(threadpool) < threadlimit):
            countfile = countfiles.pop()
            file = srcfiles.pop()
            wrkr = Worker(file,printlock,countfile,startframe,
                          endframe,particlesName,outputDirectory,questionasked)
            wrkr.start()
            threadpool.append(wrkr)
        for thr in threadpool:
            thr.join(timeout=timeout)
            if not thr.is_alive():
                threadpool.remove(thr)
    print("all threads are done")                


class Ui_Dialog(object):
    """Class containing the Gui for the program"""
    particlesName = ''
    startframe = []
    endframe = []
    pdcIncrements = 250
    sourceFiles = []
    files = []
    inputString3 = ''
    outputDirectory = []
    questionasked = 0

    def setupUi(self, Dialog):
        """Sets up ui window and objects"""
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(376, 296)
        self.lineEdit = QtGui.QLineEdit(Dialog)
        self.lineEdit.setEnabled(False)
        self.lineEdit.setGeometry(QtCore.QRect(100, 160, 181, 20))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.spinBox = QtGui.QSpinBox(Dialog)
        self.spinBox.setGeometry(QtCore.QRect(170, 40, 151, 21))
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.spinBox.valueChanged.connect(self.startFrame)
        self.spinBox.setRange(0,10000)
        self.spinBox_2 = QtGui.QSpinBox(Dialog)
        self.spinBox_2.setGeometry(QtCore.QRect(170, 80, 151, 21))
        self.spinBox_2.setObjectName(_fromUtf8("spinBox_2"))
        self.spinBox_2.valueChanged.connect(self.endFrame)
        self.spinBox_2.setRange(0,10000)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(130, 0, 131, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(70, 70, 61, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(10, 160, 81, 20))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.lineEdit_3 = QtGui.QLineEdit(Dialog)
        self.lineEdit_3.setEnabled(True)
        self.lineEdit_3.setGeometry(QtCore.QRect(190, 120, 171, 21))
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.lineEdit_3.textChanged.connect(self.getName)
        self.lineEdit_3.cursorPositionChanged.connect(self.getName)        
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(290, 160, 75, 23))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton.clicked.connect(self.browseDialog)
        self.pushButton_2 = QtGui.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(290, 210, 75, 23))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.pushButton_2.clicked.connect(self.browseDialog2)
        self.lineEdit_2 = QtGui.QLineEdit(Dialog)
        self.lineEdit_2.setEnabled(False)
        self.lineEdit_2.setGeometry(QtCore.QRect(100, 210, 181, 20))
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(5, 210, 91, 20))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.pushButton_3 = QtGui.QPushButton(Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(200, 260, 75, 23))
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.pushButton_3.clicked.connect(self.create)
        self.pushButton_4 = QtGui.QPushButton(Dialog)
        self.pushButton_4.setGeometry(QtCore.QRect(290, 260, 75, 23))
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.pushButton_4.clicked.connect(self.close)
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(70, 30, 61, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(20, 110, 151, 21))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(10, 120, 171, 31))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtGui.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(20, 40, 151, 20))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.label_9 = QtGui.QLabel(Dialog)
        self.label_9.setGeometry(QtCore.QRect(20, 80, 151, 20))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.label_10 = QtGui.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(50, 180, 281, 20))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.label_11 = QtGui.QLabel(Dialog)
        self.label_11.setGeometry(QtCore.QRect(70, 230, 281, 20))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
    
    def getName(self, lineEdit_3):
        self.particlesName = self.lineEdit_3.text() + "Shape"

    def startFrame(self, spinBox):
        self.startframe = self.spinBox.value()
        
    def endFrame(self, spinBox_2):
        self.endframe = self.spinBox_2.value()

    def create(self):
        '''Creates pdc files'''
        writtenPDCCount = 0
        pdcIncrements = 250
        if not path.exists(str(self.outputDirectory) + '\\data'):
            makedirs(str(self.outputDirectory) + '\\data')
        if not path.exists(str(self.outputDirectory) + '\\particles'):
            makedirs(str(self.outputDirectory) + '\\particles')
        if not path.exists(str(self.outputDirectory) + '\\scenes'):
            makedirs(str(self.outputDirectory) + '\\scenes')
        if not path.exists(str(self.outputDirectory) + '\\backup'):
            makedirs(str(self.outputDirectory) + '\\backup')
        threadedFuntion(self.sourceFiles, self.startframe, self.endframe,
                        self.particlesName, self.outputDirectory, self.questionasked)

    def close(self):
        sysexit(app.exec_())
    
    def browseDialog(self):
        """Browse dialog to choose pc files"""
        dialog = QtGui.QFileDialog.getOpenFileNames(caption = 'Select your .pc sequence',
                                                    filter = 'Point Cloud Files (*.pc *.pc.classic)')
        self.files = list(dialog)
        self.inputString3 = ' '.join(str(n) for n in self.files)
        self.sourceFiles = self.inputString3.split(' ')
        self.lineEdit.setText(self.inputString3)
    
    def browseDialog2(self):
        """Browse dialog to choose directory"""
        dialog2 = QtGui.QFileDialog.getExistingDirectory(caption = 'Select your output directory')
        self.outputDirectory = list(dialog2)
        inputString2 = ''.join(str(n) for n in self.outputDirectory)
        self.lineEdit_2.setText(inputString2)
        self.outputDirectory = inputString2
        
    def retranslateUi(self, Dialog):
        """Names ui objects and labels"""
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Pc to Pdc Creator",
                                                            None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Pc to Pdc Creator",
                                                        None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "End Frame:",
                                                          None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Select .pc Files:",
                                                          None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "Browse. . .",
                                                             None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Dialog", "Browse. . .",
                                                               None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Select Project Folder:",
                                                          None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Dialog", "Create PDC",
                                                               None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_4.setText(QtGui.QApplication.translate("Dialog", "Close",
                                                               None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "Start Frame:",
                                                          None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "Name of Point Cloud:",
                                                          None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Dialog",
                                                          "(You will use this again later)",
                                                          None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Dialog",
                                                          "(Frame the cache will start on)",
                                                          None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Dialog",
                                                          "(Frame the cache will end on)",
                                                          None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Dialog",
                                                           "(Navigate and select .pc or .pc.classic file sequence)",
                                                           None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("Dialog",
                                                           "(Navigate to directory to export Pdc files)",
                                                           None, QtGui.QApplication.UnicodeUTF8))
        
if __name__ == "__main__":
    freeze_support()
    app = QtGui.QApplication(sysargv)
    window = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(window)
    window.show()
    sysexit(app.exec_())
