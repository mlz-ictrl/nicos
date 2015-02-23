#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************

import logging
import os
from os import path

from PyQt4 import uic
from PyQt4.QtGui import QMainWindow, QFileDialog, QMenu
from PyQt4.QtCore import QString

from nicos.core.sessions.setups import readSetup

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'mainwindow.ui'), self)

        # initialize empty dictionary
        # supposed to be a dictionary of Tuples of parsed files
        self.info = {}
        self.scriptMenu = QMenu()
        self.scriptMenuSpecial = QMenu()
        self.scriptMenuSpecial.setTitle('special/')
        self.pushButtonSelectScript.setMenu(self.scriptMenu)

        self.pushButtonLoadSetupDir.clicked.connect(
            self.loadFile)
        self.pushButtonLoadInstruments.clicked.connect(
            self.loadInstrumentsList)
        self.comboBoxSelectInstrument.currentIndexChanged[QString].connect(
            self.loadScriptList)

        # Initialize a logger required by setups.readSetup()
        self.log = logging.getLogger()

    def loadFile(self):
        # allows a user specify the setup file to be parsed
        setupFile = QFileDialog.getOpenFileName(
            self,
            'Open Python script',
            path.expanduser('~'),
            'Python Files (*.py)')

        if setupFile:
            self.comboBoxSelectInstrument.clear()
            self.comboBoxSelectInstrument.setEnabled(False)
            self.scriptMenu.clear()
            self.scriptMenuSpecial.clear()
            self.pushButtonSelectScript.setEnabled(False)
            self.pushButtonSelectScript.setText('Select script...')
            self.pushButtonLoadInstruments.setText('Load instruments')
            self.readSetupFile(setupFile)


    def readSetupFile(self, pathToFile):
        # uses nicos.core.sessions.setups.readSetup() to read a setup file and
        # put the information in the self.info dictionary.
        self.info.clear()
        readSetup(self.info,
                  path.dirname(str(pathToFile)),
                  str(pathToFile),
                  self.log)

        # sets the textEdit's text to the dictionary for debug purposes
        self.textEdit.clear()
        self.printDict(self.info, 0)


    def printDict(self, myDict, depth):
        for value in myDict.iteritems():
            if isinstance(value, dict):
                self.printDict(value, depth + 1)
            elif isinstance(value, tuple):
                self.printTuple(value, depth + 1)
            else:
                self.textEdit.append(depth * ' ' + str(value))


    def printTuple(self, myTuple, depth):
        for value in myTuple:
            if isinstance(value, dict):
                self.printDict(value, depth + 1)
            elif isinstance(value, tuple):
                self.printTuple(value, depth + 1)
            else:
                self.textEdit.append(depth * ' ' + str(value))


    def loadInstrumentsList(self):
        # (re-)loads the list of instruments by going to the nicos dir,
        # switching to directory "custom" and loading all the entries there
        self.comboBoxSelectInstrument.clear()

        # creating an empty list to store the instruments because apparently
        # listDir does NOT return the files & directories alphabetically sorted
        instrumentList = []
        instrumentDir =  path.join(self.getNicosDir(), 'custom')
        for instrument in os.listdir(instrumentDir):
            if os.path.isdir(os.path.join(instrumentDir, instrument)):
                instrumentList.append(instrument)

        for instrument in sorted(instrumentList):
            self.comboBoxSelectInstrument.addItem(instrument)

        if not self.comboBoxSelectInstrument.isEnabled():
            self.comboBoxSelectInstrument.setEnabled(True)
            self.pushButtonLoadInstruments.setText('Reload Instruments')


    def loadScriptList(self, instrument):
        # loads all the setup files of the selected instrument into
        # self.scriptMenu and all the special setup files in the subdirectory
        # setups/special into scriptMenuSpecial
        self.scriptMenu.clear()
        self.scriptMenuSpecial.clear()

        if instrument.isEmpty():
            return

        scriptDir = os.path.join(self.getNicosDir(),
                                 'custom',
                                 str(instrument),
                                 'setups')

        # add all scripts in the scriptDir to the scriptList as strings
        # also add a string for the special subdirectory
        scriptList = []
        for script in os.listdir(scriptDir):
            if script.endswith('.py'):
                scriptList.append(script)
        scriptList.append('special/')

        # add all scripts in the special directory to the scriptListSpecial
        scriptListSpecial = []
        for script in os.listdir(os.path.join(scriptDir, 'special')):
            if script.endswith('.py'):
                scriptListSpecial.append(script)

        # fill the submenu for the special directory with the scripts in the
        # scriptListSpecial
        for script in sorted(scriptListSpecial):
            self.scriptMenuSpecial.addAction(script)

        # fill the menu for the setups directory with the scripts in the
        # scriptList, also add the submenu special/
        for script in sorted(scriptList):
            if script.endswith('special/'):
                self.scriptMenu.addMenu(self.scriptMenuSpecial)
            else:
                self.scriptMenu.addAction(script)

        # requiring two different functions because scripts in special/
        # subdirectory have a different path than scripts in setups/
        for action in self.scriptMenu.actions():
            action.triggered.connect(self.loadSetupScript)

        for specialAction in self.scriptMenuSpecial.actions():
            specialAction.triggered.connect(self.loadSpecialScript)

        if not self.pushButtonSelectScript.isEnabled():
            self.pushButtonSelectScript.setEnabled(True)


    def loadSetupScript(self):
        if not str(self.sender().text()):
            return
        self.loadScript(str(self.sender().text()))


    def loadSpecialScript(self):
        if not str(self.sender().text()):
            return
        self.loadScript(os.path.join('special', str(self.sender().text())))


    def loadScript(self, script):
        # loads the given script using self.readSetupFile()
        self.pushButtonSelectScript.setText(script)

        pathToScript = os.path.join(
            self.getNicosDir(),
            'custom',
            str(self.comboBoxSelectInstrument.currentText()),
            'setups',
            script)

        self.readSetupFile(pathToScript)


    def getNicosDir(self):
        # this file should be in */nicos-core/tools/setupfiletool
        return(path.abspath(path.join(path.dirname( __file__ ), '..', '..')))
