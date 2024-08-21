# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI utilities."""

import logging
from os import path

from nicos.core import MAINTENANCE, MASTER, SIMULATION, SLAVE
from nicos.guisupport.qt import QApplication, QByteArray, QColor, QDateTime, \
    QDialog, QFileDialog, QFont, QLabel, QMessageBox, QProgressDialog, \
    QPushButton, QSettings, QSize, QStyle, Qt, QTextEdit, QToolButton, \
    QVBoxLayout, QWidget, uic


def splitTunnelString(tunnel):
    tmp = tunnel.split('@')
    host = tmp[-1]
    username, password = '', ''
    if len(tmp) > 1:
        tmp = tmp[0].split(':')
        username = tmp[0]
        if len(tmp) > 1:
            password = tmp[1]
    return host, username, password


uipath = path.dirname(__file__)


def loadUi(widget, uiname):
    return uic.loadUi(path.join(uipath, uiname), widget)


def dialogFromUi(parent, uiname):
    dlg = QDialog(parent)
    loadUi(dlg, uiname)
    return dlg


def loadBasicWindowSettings(window, settings):
    window.restoreGeometry(settings.value('geometry', '', QByteArray))
    window.restoreState(settings.value('windowstate', '', QByteArray))
    try:
        window.splitstate = settings.value('splitstate', '', QByteArray)
    except TypeError:
        window.splitstate = ''


def loadUserStyle(window, settings):
    window.user_font = settings.value('font', QFont('Monospace'), QFont)
    window.user_color = settings.value('color', QApplication.palette().base().color(), QColor)


def enumerateWithProgress(seq, text, every=1, parent=None, total=None,
                          force_display=False):
    total = total or len(seq)
    pd = QProgressDialog(parent, labelText=text)
    pd.setRange(0, total)
    pd.setCancelButton(None)
    if total > every or force_display:
        pd.show()
    processEvents = QApplication.processEvents
    processEvents()
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
        widget.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)


def modePrompt(mode):
    return {SLAVE:       'slave >>',
            SIMULATION:  'SIM >>',
            MAINTENANCE: 'maint >>',
            MASTER:      '>>'}[mode]


class DlgUtils:
    def __init__(self, title):
        self._dlgutils_title = title

    def showError(self, text):
        QMessageBox.warning(self, self._dlgutils_title, text)

    def showInfo(self, text):
        QMessageBox.information(self, self._dlgutils_title, text)

    def askQuestion(self, text, select_no=False):
        defbutton = select_no and QMessageBox.StandardButton.No or \
                    QMessageBox.StandardButton.Yes
        buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        return QMessageBox.question(self, self._dlgutils_title, text, buttons,
                                    defbutton) == QMessageBox.StandardButton.Yes

    def selectInputFile(self, ctl, text='Choose an input file'):
        previous = ctl.text()
        if previous:
            startdir = path.dirname(previous)
        else:
            startdir = '.'
        fn = QFileDialog.getOpenFileName(self, text, startdir, 'All files (*)')[0]
        if fn:
            ctl.setText(fn)

    def selectOutputFile(self, ctl, text='Choose an output filename'):
        previous = ctl.text()
        if previous:
            startdir = path.dirname(previous)
        else:
            startdir = '.'
        fn = QFileDialog.getSaveFileName(self, text, startdir, 'All files (*)')[0]
        if fn:
            ctl.setText(fn)

    def selectDirectory(self, ctl, text='Choose a directory'):
        previous = ctl.text()
        startdir = previous or '.'
        fname = QFileDialog.getExistingDirectory(self, text, startdir)
        if fname:
            ctl.setText(fname)

    def viewTextFile(self, fname):
        with open(fname, encoding='utf-8', erorrs='replace') as f:
            contents = f.read()
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
        btn.clicked.connect(qd.accept)
        lay.addWidget(btn, 0, QWidget.AlignRight)
        qd.show()


class SettingGroup:
    global_group = ''

    def __init__(self, name):
        self.name = name
        self.settings = QSettings()

    def __enter__(self):
        if self.global_group:
            self.settings.beginGroup(self.global_group)
        self.settings.beginGroup(self.name)
        return self.settings

    def __exit__(self, *args):
        if self.global_group:
            self.settings.endGroup()
        self.settings.endGroup()
        self.settings.sync()


class ScriptExecQuestion(QMessageBox):
    """Special QMessageBox for asking what to do when a script is running."""

    def __init__(self):
        QMessageBox.__init__(
            self, QMessageBox.Icon.Information, 'Error',
            'A script is currently running.  What do you want to do?',
            QMessageBox.StandardButton.NoButton)

        # Using NoRole to avoid buttons getting rearranged depending on OS
        self.queueBtn = self.addButton('Queue script',
                                       QMessageBox.ButtonRole.NoRole)
        self.queueBtn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogOkButton))
        self.execBtn = self.addButton('Execute now!',
                                      QMessageBox.ButtonRole.NoRole)
        self.execBtn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_MessageBoxWarning))
        self.cancelBtn = self.addButton('Cancel',
                                        QMessageBox.ButtonRole.NoRole)
        self.cancelBtn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogCancelButton))

    def exec(self):
        QMessageBox.exec(self)
        # Since our buttons have no role, determine the correct return value
        btn = self.clickedButton()
        if btn == self.execBtn:
            return QMessageBox.StandardButton.Apply
        elif btn == self.queueBtn:
            return QMessageBox.StandardButton.Yes
        return QMessageBox.StandardButton.Cancel


class DlgPresets:
    """Save dialog presets for Qt dialogs."""

    def __init__(self, group, ctls):
        self.group = group
        self.ctls = ctls
        self.settings = QSettings()

    def load(self):
        self.settings.beginGroup(self.group)
        for (ctl, default) in self.ctls:
            entry = 'presets/' + ctl.objectName()
            val = self.settings.value(entry, default, type(default))
            try:
                getattr(self, 'set_' + ctl.__class__.__name__)(ctl, val)
            except Exception as err:
                print(ctl, err)
        self.settings.endGroup()

    def save(self):
        self.settings.beginGroup(self.group)
        for (ctl, _) in self.ctls:
            entry = 'presets/' + ctl.objectName()
            try:
                val = getattr(self, 'get_' + ctl.__class__.__name__)(ctl)
                self.settings.setValue(entry, val)
            except Exception as err:
                print(err)
        self.settings.endGroup()
        self.settings.sync()

    def set_QLineEdit(self, ctl, val):
        ctl.setText(val)

    def set_QListBox(self, ctl, val):
        ctl.setSelected(ctl.findItem(val), 1)

    def set_QListWidget(self, ctl, val):
        ctl.setCurrentItem(ctl.findItems(val, Qt.MatchFlag.MatchExactly)[0])

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
        return ctl.toPlainText()

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


class DebugHandler(logging.Handler):
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        logging.Handler.__init__(self)

    def emit(self, record):
        if self.mainwindow.debugConsole:
            msg = self.format(record)
            self.mainwindow.debugConsole.addLogMsg('#' * 80)
            self.mainwindow.debugConsole.addLogMsg(msg)


def split_query(fromtime, totime, interval, func):
    # if requested period is longer than 1 day it will be sequenced
    maxquery = 3600 * 24
    history = []
    if totime - fromtime > maxquery:
        for sequence in range(int((totime - fromtime) // maxquery)):
            if sequence:
                fromtime += maxquery
            history.extend(func(fromtime, fromtime+maxquery, interval))
    history.extend(func(fromtime, totime, interval))
    return history
