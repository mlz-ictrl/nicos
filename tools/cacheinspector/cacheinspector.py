#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
from PyQt4.QtGui import QApplication, QIcon

from .mainwindow import MainWindow  # pylint: disable=F0401
from .cacheclient import CICacheClient  # pylint: disable=F0401


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

    def start(self):
        self._window.show()
        if self.cache:
            self.connect(*self._address)
        try:
            self._qtapp.exec_()
        except KeyboardInterrupt:
            pass
        self._stoprequest = True
