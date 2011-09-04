#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""Utilities for Qt dialog applications."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import sys
from os import path

from PyQt4.QtCore import SIGNAL, SLOT, QObject, QSize, QVariant, QSettings, \
     QDateTime, Qt
from PyQt4.QtGui import QDialog, QFileDialog, QLabel, QPushButton, QTextEdit, \
     QFont, QVBoxLayout, QWidget, QApplication


__all__ = ['selectInputFile', 'selectOutputFile', 'selectDirectory',
           'viewTextFile', 'runDlgStandalone',
           'DlgPresets']

def selectInputFile(ctl, parent=None,
                    text='Choose an input file'):
    previous = str(ctl.text())
    if previous:
        startdir = path.dirname(previous)
    else:
        startdir = '.'
    fname = QFileDialog.getOpenFileName(parent, text,
                                        startdir, 'All files (*)')
    if fname:
        ctl.setText(fname)

def selectOutputFile(ctl, parent=None,
                     text='Choose an output filename'):
    previous = str(ctl.text())
    if previous:
        startdir = path.dirname(previous)
    else:
        startdir = '.'
    fname = QFileDialog.getSaveFileName(parent, text,
                                        startdir, 'All files (*)')
    if fname:
        ctl.setText(fname)

def selectDirectory(ctl, parent=None, text='Choose a directory'):
    previous = str(ctl.text())
    startdir = previous or '.'
    fname = QFileDialog.getExistingDirectory(parent, text, startdir)
    if fname:
        ctl.setText(fname)


def viewTextFile(fname, parent=None):
    f = open(fname)
    contents = f.read()
    f.close()
    qd = QDialog(parent, 'PreviewDlg', True)
    qd.setCaption('File preview')
    qd.resize(QSize(500, 500))
    lay = QVBoxLayout(qd, 11, 6, 'playout')
    lb = QLabel(qd, 'label')
    lb.setText('Viewing %s:' % fname)
    lay.addWidget(lb)
    tx = QTextEdit(qd, 'preview')
    tx.setReadOnly(1)
    tx.setText(contents)
    font = QFont(tx.font())
    font.setFamily('monospace')
    tx.setFont(font)
    lay.addWidget(tx)
    btn = QPushButton(qd, 'ok')
    btn.setAutoDefault(1)
    btn.setDefault(1)
    btn.setText('Close')
    qd.connect(btn, SIGNAL('clicked()'), qd.accept)
    lay.addWidget(btn, 0, QWidget.AlignRight)
    qd.show()


def runDlgStandalone(dlgclass):
    a = QApplication(sys.argv)
    QObject.connect(a, SIGNAL('lastWindowClosed()'), a, SLOT('quit()'))
    dlg = dlgclass()
    #a.setMainWidget(dlg)
    dlg.show()
    a.exec_()


class DlgPresets(object):
    """Save dialog presets for Qt dialogs."""
    def __init__(self, group, ctls):
        self.group = group
        self.ctls = ctls
        self.settings = QSettings('nicostools')

    def load(self):
        self.settings.beginGroup(self.group)
        for (ctl, default) in self.ctls:
            entry = 'presets/' + ctl.objectName()
            val = self.settings.value(entry, QVariant(default))
            try:
                if type(default) is int:
                    val = val.toInt()[0]
                else:
                    val = val.toString()
                getattr(self, 'set_' + ctl.__class__.__name__)(ctl, val)
            except Exception, err:
                print ctl, err
        self.settings.endGroup()

    def save(self):
        self.settings.beginGroup(self.group)
        for (ctl, _) in self.ctls:
            entry = 'presets/' + ctl.objectName()
            try:
                val = getattr(self, 'get_' + ctl.__class__.__name__)(ctl)
                self.settings.setValue(entry, QVariant(val))
            except Exception, err:
                print err
        self.settings.endGroup()
        self.settings.sync()

    def set_QLineEdit(self, ctl, val):
        ctl.setText(val)
    def set_QListBox(self, ctl, val):
        ctl.setSelected(ctl.findItem(val), 1)
    def set_QListWidget(self, ctl, val):
        ctl.setCurrentItem(ctl.findItems(val, Qt.MatchExactly)[0])
    def set_QComboBox(self, ctl, val):
        if ctl.isEditable():
            ctl.setEditText(val)
        else:
            ctl.setCurrentIndex(val)
    def set_QTextEdit(self, ctl, val):
        ctl.setText(val)
    def set_QTabWidget(self, ctl, val):
        ctl.setCurrentIndex(val)
    def set_QSpinBox(self, ctl, val):
        ctl.setValue(val)
    def set_QRadioButton(self, ctl, val):
        ctl.setChecked(bool(val))
    def set_QCheckBox(self, ctl, val):
        ctl.setChecked(bool(val))
    def set_QDateTimeEdit(self, ctl, val):
        ctl.setDateTime(QDateTime.fromString(val))

    def get_QLineEdit(self, ctl):
        return ctl.text()
    def get_QListBox(self, ctl):
        return ctl.selectedItem().text()
    def get_QListWidget(self, ctl):
        return ctl.currentItem().text()
    def get_QComboBox(self, ctl):
        if ctl.isEditable():
            return ctl.currentText()
        else:
            return ctl.currentIndex()
    def get_QTextEdit(self, ctl):
        return ctl.text()
    def get_QTabWidget(self, ctl):
        return ctl.currentIndex()
    def get_QSpinBox(self, ctl):
        return ctl.value()
    def get_QRadioButton(self, ctl):
        return int(ctl.isChecked())
    def get_QCheckBox(self, ctl):
        return int(ctl.isChecked())
    def get_QDateTimeEdit(self, ctl):
        return ctl.dateTime().toString()
