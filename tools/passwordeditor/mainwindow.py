#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
import hashlib
from os import path
from collections import OrderedDict

from PyQt4 import uic
from PyQt4.QtGui import QMainWindow, QFileDialog, QMessageBox

from nicos.core.sessions.setups import readSetup

from passwordeditor.userdialog import UserDialog
from passwordeditor.user import User


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'mainwindow.ui'), self)

        self.info = {}          # dictionary read from script
        self.className = ''     # name of the devices class in auth tuple
        self.group = ''         # name of the group defined in the setup file
        self.description = ''   # name of the description in the setup file
        self.authDict = {}      # dictionary containing info in auth tuple
        self.users = {}         # dict to store users while working
        self.loadedScript = ''  # path to the currently loaded file without *.py

        self.actionNew.triggered.connect(self.newFile)
        self.actionLoad.triggered.connect(self.loadFile)
        self.actionSave.triggered.connect(self.save)
        self.actionPrintInfo.triggered.connect(self.debugInfo)
        self.actionPrintClassname.triggered.connect(self.debugClassname)
        self.actionPrintAuthDict.triggered.connect(self.debugAuthDict)
        self.actionPrintUsers.triggered.connect(self.debugUsers)
        self.actionEditable.triggered.connect(self.toggleEditable)
        self.actionShowDebug.triggered.connect(self.toggleDebug)

        self.menuBar.clear()
        self.menuBar.addMenu(self.menuFile)
        self.menuBar.addMenu(self.menuEdit)

        self.userList.currentItemChanged.connect(self.changeUser)
        self.pushButtonAddUser.clicked.connect(self.addUser)
        self.pushButtonDeleteUser.clicked.connect(self.deleteUser)
        self.pushButtonSaveConfig.clicked.connect(self.setConfig)
        self.pushButtonSaveUser.clicked.connect(self.setUserData)

        self.lineEditClassName.textEdited.connect(self.changedConfig)
        self.lineEditGroup.textEdited.connect(self.changedConfig)
        self.lineEditDescription.textEdited.connect(self.changedConfig)
        self.comboBoxHashing.activated.connect(self.changedConfig)
        self.lineEditUserName.textEdited.connect(self.changedUser)
        self.lineEditPassword.textEdited.connect(self.changedUser)
        self.comboBoxUserLevel.activated.connect(self.changedUser)

        # Initialize a logger required by setups.readSetup()
        self.log = logging.getLogger()

    def loadFile(self):
        # allows a user to specify the setup file to be parsed
        setupFile = QFileDialog.getOpenFileName(
            self,
            'Open Python script',
            path.expanduser('~'),
            'Python Files (*.py)')

        if setupFile:
            self.readSetupFile(setupFile)

    def readSetupFile(self, pathToFile):
        # uses nicos.core.sessions.setups.readSetup() to read a setup file and
        # put the information in the self.info dictionary.
        self.info.clear()
        self.users.clear()
        while self.userList.count() > 1:
            self.userList.takeItem(1)

        readSetup(self.info, str(pathToFile), self.log)
        self.loadedScript = str(pathToFile[:-3])

        # if device Auth doesnt exist, create it
        if 'Auth' not in self.info[str(pathToFile[:-3])]['devices']:
            self.info[str(pathToFile[:-3])]['devices']['Auth'] = (
                'services.daemon.auth.ListAuthenticator',
                {'passwd': [], 'hashing': 'sha1'})

        self.className = self.info[str(pathToFile[:-3])]['devices']['Auth'][0]
        self.group = self.info[str(pathToFile[:-3])]['group']
        self.description = self.info[str(pathToFile[:-3])]['description']
        self.authDict = self.info[str(pathToFile[:-3])]['devices']['Auth'][1]

        for userTuple in self.authDict['passwd']:  # passwd = list of users
            newUser = User(userTuple[0], userTuple[1], userTuple[2])
            self.users[userTuple[0]] = newUser  # convert to editable users

        for key in self.users:
            self.userList.addItem(key)  # put users in gui (list widget)

        self.userList.setEnabled(True)
        self.lineEditClassName.setEnabled(True)
        self.lineEditGroup.setEnabled(True)
        self.lineEditDescription.setEnabled(True)
        self.comboBoxHashing.setEnabled(True)
        self.lineEditUserName.setEnabled(True)
        self.lineEditPassword.setEnabled(True)
        self.comboBoxUserLevel.setEnabled(True)
        self.pushButtonAddUser.setEnabled(True)
        self.pushButtonDeleteUser.setEnabled(True)

        self.userList.setCurrentRow(0)
        self.reloadConfig()

    def changeUser(self, user, previuousUser):
        # signal provides last item and current item
        self.pushButtonSaveUser.setEnabled(False)
        self.pushButtonSaveConfig.setEnabled(False)

        if self.userList.currentRow() == 0:  # if "Device Configuration...":
            self.userWidget.setVisible(False)
            self.infoWidget.setVisible(True)
            self.pushButtonDeleteUser.setEnabled(False)
            self.lineEditClassName.setText(self.className)
            self.lineEditGroup.setText(self.group)
            self.lineEditDescription.setText(self.description)
            self.comboBoxHashing.setCurrentIndex(self.comboBoxHashing.findText(
                self.authDict['hashing']))
            return

        if not self.userWidget.isVisible():  # if previous selection was no user
            self.userWidget.setVisible(True)
            self.infoWidget.setVisible(False)
            self.pushButtonDeleteUser.setEnabled(True)

        currentUser = self.users[str(user.text())]
        self.lineEditUserName.setText(currentUser.userName)
        if currentUser.password:
            # to show 'there is a password, it's not empty'
            self.lineEditPassword.setText('abcdefg')
        else:
            self.lineEditPassword.clear()
        self.comboBoxUserLevel.setCurrentIndex(self.comboBoxUserLevel.findText(
            currentUser.userLevel))

    def reloadConfig(self):
        self.pushButtonDeleteUser.setEnabled(False)
        self.lineEditClassName.setText(self.className)
        self.lineEditGroup.setText(self.group)
        self.lineEditDescription.setText(self.description)
        self.comboBoxHashing.setCurrentIndex(self.comboBoxHashing.findText(
            self.authDict['hashing']))

    def deleteUser(self):
        user = str(self.userList.currentItem().text())
        del self.users[user]  # remove from model
        self.userList.takeItem(self.userList.currentRow())  # remove from gui

    def addUser(self):
        dlg = UserDialog()
        if dlg.exec_():
            username = str(dlg.lineEditUserName.text())
            if dlg.lineEditPassword.text().isEmpty():
                password = ''
            else:
                noHashPassword = str(dlg.lineEditPassword.text())
                if self.authDict['hashing'] == 'sha1':
                    password = str(hashlib.sha1(noHashPassword).hexdigest())
                else:  # elif self.authDict['hashing'] == 'md5':
                    password = str(hashlib.md5(noHashPassword).hexdigest())
            userlevel = str(dlg.comboBoxUserLevel.currentText())
            newUser = User(username, password, userlevel)
            self.users[username] = newUser
            self.userList.addItem(username)

    def hashingMsgbox(self):
        msgBox = QMessageBox()
        msgBox.setText('Changing the hashing requires you to enter all' +
                       'passwords again.')
        msgBox.setInformativeText('Do you still want to change the hashing?\n' +
                                  'WARNING: THIS WILL CLEAR ALL PASSWORDS.')
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        return msgBox.exec_() == QMessageBox.Ok

    def setConfig(self):
        # method called when clicking save button in config widget.
        self.pushButtonSaveConfig.setEnabled(False)

        self.className = str(self.lineEditClassName.text())
        self.group = str(self.lineEditGroup.text())
        self.description = str(self.lineEditDescription.text())

        newHashing = str(self.comboBoxHashing.currentText())
        if newHashing != self.authDict['hashing']:
            if self.hashingMsgbox():
                self.authDict['hashing'] = newHashing
                self.removeAllPasswords()
            else:
                self.comboBoxHashing.setCurrentIndex(
                    self.comboBoxHashing.findText(self.authDict['hashing']))

    def setUserData(self):
        # method called when clicking save button in user widget.
        self.pushButtonSaveUser.setEnabled(False)

        # get the string of the currently selected user in GUI
        oldUserName = str(self.userList.currentItem().text())

        # get the new entered username
        newUserName = str(self.lineEditUserName.text())

        # update model
        # because users are identified by their name, the key in the dictionary
        # must be updated to the new name.
        self.users[newUserName] = self.users.pop(oldUserName)
        self.users[newUserName].userName = newUserName
        if self.lineEditPassword.text().isEmpty():
            password = ''
        else:
            noHashPassword = str(self.lineEditPassword.text())
            if self.authDict['hashing'] == 'sha1':
                password = str(hashlib.sha1(noHashPassword).hexdigest())
            else:  # elif self.authDict['hashing'] == 'md5':
                password = str(hashlib.md5(noHashPassword).hexdigest())
        self.users[newUserName].password = password
        self.users[newUserName].userLevel = str(self.comboBoxUserLevel.
                                                currentText())

        # update GUI
        self.userList.currentItem().setText(newUserName)

    def changedConfig(self):
        # called when changing lineEdits for className, group, description
        # or selection in comboBoxHashing changed
        if not self.pushButtonSaveConfig.isEnabled():
            self.pushButtonSaveConfig.setEnabled(True)

    def changedUser(self):
        # called when lineEditUserName, lineEditPassword, comoBoxUserLevel change
        if not self.pushButtonSaveUser.isEnabled():
            self.pushButtonSaveUser.setEnabled(True)

    def removeAllPasswords(self):
        # called when hashing changes: It's neccessary to enter all passwords
        # again, so they can be hashed in the new way.
        for _, value in self.users.items():
            value.password = ''

    def toggleEditable(self):
        if self.actionEditable.isChecked():
            self.lineEditClassName.setReadOnly(False)
            self.lineEditGroup.setReadOnly(False)
            self.lineEditDescription.setReadOnly(False)
        else:
            self.lineEditClassName.setReadOnly(True)
            self.lineEditGroup.setReadOnly(True)
            self.lineEditDescription.setReadOnly(True)

    def toggleDebug(self):
        if self.actionShowDebug.isChecked():
            self.menuBar.clear()
            self.menuBar.addMenu(self.menuFile)
            self.menuBar.addMenu(self.menuEdit)
            self.menuBar.addMenu(self.menuDebug)
        else:
            self.menuBar.clear()
            self.menuBar.addMenu(self.menuFile)
            self.menuBar.addMenu(self.menuEdit)

    def debugInfo(self):
        print(self.info)
        print('')

    def debugClassname(self):
        print(self.className)
        print('')

    def debugAuthDict(self):
        print(self.authDict)
        print('')

    def debugUsers(self):
        for _, value in self.users.items():
            print(value.userName)
            print(value.password)
            print(value.userLevel)
            print('')
        print('')

    def newFile(self):
        filepath = QFileDialog.getSaveFileName(
            self,
            "New setup...",
            path.expanduser('~'),
            "Python script (*.py)")

        if filepath:
            if not str(filepath).endswith('.py'):
                filepath += '.py'
            open(filepath, 'w').close()
            self.readSetupFile(filepath)

    def save(self):
        # put information in self.users, e.g. the User() classes, into tuples
        # and put them back into self.info['file']['devices']['Auth'][1][passwd]
        del self.authDict['passwd'][:]
        for _, value in self.users.items():
            self.authDict['passwd'].append((value.userName,
                                            value.password,
                                            value.userLevel))

        # open a file to save into, create empty output string
        filepath = QFileDialog.getSaveFileName(
            self,
            "Save as...",
            path.expanduser('~'),
            "Python script (*.py)")

        if not str(filepath):
            return
        if not str(filepath).endswith('.py'):
            filepath += '.py'

        output = []
        add = output.append

        add('description = ')
        add(repr(self.description) + '\n\n')

        add('group = ')
        add(repr(self.group) + '\n\n')

        add('includes = ')
        add(repr(self.info[self.loadedScript]['includes']) + '\n\n')

        add('excludes = ')
        add(repr(self.info[self.loadedScript]['excludes']) + '\n\n')

        add('modules = ')
        add(repr(self.info[self.loadedScript]['modules']) + '\n\n')

        add('sysconfig = dict(\n')
        for key, value in self.info[self.loadedScript]['sysconfig'].items():
            add('    ' + str(key) + ' = ' + repr(value) + ',\n')
        add(')\n\n')

        add('devices = dict(\n')

        # sort the devices by their name
        self.info[self.loadedScript]['devices'] = OrderedDict(
            sorted(self.info[self.loadedScript]['devices'].items()))
        for deviceName, deviceInfo in self.info[
                self.loadedScript]['devices'].items():
            add('    ' + str(deviceName) + ' = device(')
            indent = '              ' + (' ' * len(deviceName))  # fancy indent

            if str(deviceName) == 'Auth':
                add(repr(self.className) + ',\n')

            else:
                add(repr(deviceInfo[0]) + ',\n')

            for deviceParam, paramValue in deviceInfo[1].items():
                add(indent + str(deviceParam) + ' = ')
                if deviceParam == 'passwd':
                    add('[\n')
                    for userTuple in paramValue:
                        add(indent + '          ' + repr(userTuple) + ',\n')
                    add(indent + '         ],\n')
                else:
                    add(repr(paramValue) + ',\n')
            add((' ' * (len(indent) - 1)) + '),\n')
        add(')\n\n')

        add("startupcode = '''")
        add(self.info[self.loadedScript]['startupcode'] + "'''\n\n")

        with open(str(filepath), 'w') as outputFile:
            outputFile.write(''.join(output))
