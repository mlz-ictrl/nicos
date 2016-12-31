#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Pascal Neubert <pascal.neubert@frm2.tum.de>
#
# *****************************************************************************

import sys
from logging import Handler, INFO, WARNING, ERROR

from PyQt4.QtGui import QApplication, QIcon, QPalette
from PyQt4.QtCore import Qt

from nicos import session
from nicos.utils.loggers import NicosLogger, ColoredConsoleHandler
from nicos.core.sessions.simple import SingleDeviceSession

from .mainwindow import MainWindow  # pylint: disable=F0401
from .cacheclient import CICacheClient  # pylint: disable=E0611


class StatusBarHandler(Handler):

    def __init__(self):
        Handler.__init__(self)
        self._statusbar = None

    def setStatusbar(self, statusbar):
        self._statusbar = statusbar

    def emit(self, record):
        if self._statusbar:
            msg = record.message
            palette = self._statusbar.palette()
            color = Qt.black
            if record.levelno == WARNING:
                color = Qt.darkMagenta
                msg = 'Warning: ' + msg
            elif record.levelno == ERROR:
                color = Qt.red
                msg = 'Error: ' + msg
            palette.setColor(QPalette.WindowText, color)
            self._statusbar.setPalette(palette)
            self._statusbar.showMessage(msg)


class CISession(SingleDeviceSession):
    """Session for the cache inspector: makes log messages appear in the
    status bar of the main window.
    """

    _qthandler = None

    def createRootLogger(self, prefix='nicos', console=True):
        self.log = NicosLogger('nicos')
        self.log.setLevel(INFO)
        self.log.parent = None
        self.log.addHandler(ColoredConsoleHandler())
        self._qthandler = StatusBarHandler()
        self.log.addHandler(self._qthandler)


class CacheInspector(CICacheClient):

    # Import the compiled resource file to register resources
    import nicos.guisupport.gui_rc  # pylint: disable=W0612

    def doInit(self, mode):
        CICacheClient.doInit(self, self._mode)
        self._qtapp = QApplication(sys.argv)
        self._qtapp.setOrganizationName('nicos')
        self._qtapp.setApplicationName('cacheinspector')
        self._window = MainWindow(self)
        self._window.setWindowIcon(QIcon(':/inspector'))
        session._qthandler.setStatusbar(self._window.statusBar())

    def start(self):
        self._window.show()
        if self.cache:
            self.connect(self.cache)
        try:
            self._qtapp.exec_()
        except KeyboardInterrupt:
            pass
        self._stoprequest = True
