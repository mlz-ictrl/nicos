#  -*- coding: utf-8 -*-
# *****************************************************************************
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
# Module authors:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI utilities."""

__version__ = "$Revision$"

import os
import re
import time
import random
import socket
from os import path
from itertools import islice, chain

from PyQt4 import uic
from PyQt4.QtCore import Qt, QSettings, QVariant, QDateTime, QSize, SIGNAL
from PyQt4.QtGui import QApplication, QDialog, QProgressDialog, QMessageBox, \
     QPushButton, QTreeWidgetItem, QPalette, QFont, QClipboard, QDialogButtonBox, \
     QToolButton, QFileDialog, QLabel, QTextEdit, QWidget, QVBoxLayout

from nicos.gui.client import DEFAULT_PORT


def parseConnectionData(s):
    res = re.match(r"(?:(\w+)@)?([\w.]+)(?::(\d+))?", s)
    if res is None:
        return None
    return res.group(1) or 'guest', res.group(2), \
           int(res.group(3) or DEFAULT_PORT)

def getXDisplay():
    try:
        lhost = socket.getfqdn(socket.gethostbyaddr(socket.gethostname())[0])
    except socket.gaierror:
        return ''
    else:
        return lhost + os.environ.get('DISPLAY', ':0')

def chunks(iterable, size):
    sourceiter = iter(iterable)
    while True:
        chunkiter = islice(sourceiter, size)
        yield chain([chunkiter.next()], chunkiter)

def importString(import_name, silent=False):
    """Imports an object based on a string."""
    if ':' in import_name:
        module, obj = import_name.split(':', 1)
    elif '.' in import_name:
        module, obj = import_name.rsplit('.', 1)
    else:
        return __import__(import_name)
    return getattr(__import__(module, None, None, [obj]), obj)

def _s(n):
    return int(n), (n != 1 and 's' or '')

def formatAlternateDuration(secs):
    if secs == 0:
        return 'less than 42 seconds'
    elif secs < 360:
        return '%s millimonth%s' % _s(secs / 2.592)
    elif secs < 3600:
        return '%s microyear%s' % _s(secs / 31.536)
    elif secs < 86400:
        return '%s centiweek%s, %s microyear%s' % (_s(secs / 6048) +
                                                   _s((secs % 6048) / 31.536))
    else:
        #return '%.2f nanolightyears per kiloknot' % (secs / 18391.8)
        return '%.2f calories per megawatt' % (secs / 4186800.0)

def formatDuration(secs):
    if random.random() > 0.99:
        est = formatAlternateDuration(secs)
    elif 0 <= secs < 60:
        est = '%s second%s' % _s(secs)
    elif secs < 3600:
        est = '%s minute%s' % _s(secs // 60 + 1)
    elif secs < 86400:
        est = '%s hour%s, %s minute%s' % (_s(secs // 3600) +
                                          _s((secs % 3600) // 60))
    else:
        est = '%s day%s, %s hour%s' % (_s(secs // 86400) +
                                       _s((secs % 86400) // 3600))
    return est

def formatEndtime(secs):
    return time.strftime('%A, %H:%M', time.localtime(time.time() + secs))

def safeFilename(fn):
    return re.compile('[^a-zA-Z0-9_.-]').sub('', fn)


# -- UI tools ------------------------------------------------------------------

uipath = path.dirname(__file__)

def loadUi(widget, uiname):
    uic.loadUi(path.join(uipath, uiname), widget)

def dialogFromUi(parent, uiname):
    dlg = QDialog(parent)
    loadUi(dlg, uiname)
    return dlg

def enumerateWithProgress(seq, text, every=1, parent=None, total=None):
    total = total or len(seq)
    pd = QProgressDialog(parent)
    pd.setLabelText(text)
    pd.setRange(0, total)
    pd.setCancelButton(None)
    if total > every:
        pd.show()
    processEvents = QApplication.processEvents
    try:
        for i, item in enumerate(seq):
            if i % every == 0:
                pd.setValue(i)
                processEvents()
            yield i, item
    finally:
        pd.close()


def showToolText(toolbar, action):
    widget = toolbar.widgetForAction(action)
    if isinstance(widget, QToolButton):
        widget.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

def setBackgroundColor(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.Base, color)
    widget.setBackgroundRole(QPalette.Base)
    widget.setPalette(palette)

def setForegroundColor(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.WindowText, color)
    widget.setForegroundRole(QPalette.WindowText)
    widget.setPalette(palette)


class DlgUtils(object):
    def __init__(self, title):
        self._dlgutils_title = title

    def showError(self, text):
        QMessageBox.warning(self, self._dlgutils_title, text)

    def showInfo(self, text):
        QMessageBox.information(self, self._dlgutils_title, text)

    def askQuestion(self, text, select_no=False):
        defbutton = select_no and QMessageBox.No or QMessageBox.Yes
        buttons = QMessageBox.Yes | QMessageBox.No
        return QMessageBox.question(self, self._dlgutils_title, text,
                                    buttons, defbutton) == QMessageBox.Yes

    def selectInputFile(self, ctl, text='Choose an input file'):
        previous = str(ctl.text())
        if previous:
            startdir = path.dirname(previous)
        else:
            startdir = '.'
        fname = QFileDialog.getOpenFileName(self, text,
                                            startdir, 'All files (*)')
        if fname:
            ctl.setText(fname)

    def selectOutputFile(self, ctl, text='Choose an output filename'):
        previous = str(ctl.text())
        if previous:
            startdir = path.dirname(previous)
        else:
            startdir = '.'
        fname = QFileDialog.getSaveFileName(self, text,
                                            startdir, 'All files (*)')
        if fname:
            ctl.setText(fname)

    def selectDirectory(self, ctl, text='Choose a directory'):
        previous = str(ctl.text())
        startdir = previous or '.'
        fname = QFileDialog.getExistingDirectory(self, text, startdir)
        if fname:
            ctl.setText(fname)

    def viewTextFile(self, fname):
        f = open(fname)
        contents = f.read()
        f.close()
        qd = QDialog(self, 'PreviewDlg', True)
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


class SettingGroup(object):
    def __init__(self, name):
        self.name = name
        self.settings = QSettings()

    def __enter__(self):
        self.settings.beginGroup(self.name)
        return self.settings

    def __exit__(self, *args):
        self.settings.endGroup()
        self.settings.sync()


def showTraceback(tb, parent, fontwidget):
    assert tb.startswith('Traceback')
    # split into frames and message
    frames = []
    message = ''
    curframe = None
    for line in tb.splitlines():
        if line.startswith('        '):
            name, v = line.split('=', 1)
            curframe[2][name.strip()] = v.strip()
        elif line.startswith('    '):
            curframe[1] = line.strip()
        elif line.startswith('  '):
            curframe = [line.strip(), '', {}]
            frames.append(curframe)
        elif not line.startswith('Traceback'):
            message += line
    # show traceback window
    dlg = dialogFromUi(parent, 'traceback.ui')
    button = QPushButton('To clipboard', dlg)
    dlg.buttonBox.addButton(button, QDialogButtonBox.ActionRole)
    def copy():
        QApplication.clipboard().setText(tb+'\n', QClipboard.Selection)
        QApplication.clipboard().setText(tb+'\n', QClipboard.Clipboard)
    parent.connect(button, SIGNAL('clicked()'), copy)
    dlg.message.setText(message)
    dlg.tree.setFont(fontwidget.font())
    boldfont = QFont(fontwidget.font())
    boldfont.setBold(True)
    for file, line, bindings in frames:
        item = QTreeWidgetItem(dlg.tree, [file])
        item.setFirstColumnSpanned(True)
        item = QTreeWidgetItem(dlg.tree, [line])
        item.setFirstColumnSpanned(True)
        item.setFont(0, boldfont)
        for var, value in bindings.iteritems():
            QTreeWidgetItem(item, ['', var, value])
    dlg.show()


class DlgPresets(object):
    """Save dialog presets for Qt dialogs."""

    def __init__(self, group, ctls):
        self.group = group
        self.ctls = ctls
        self.settings = QSettings()

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
