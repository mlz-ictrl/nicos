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

"""Logfile viewer tool."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

# ----- user changeable parameters ---------------------------------------------

STDLOGPATH = '/data'

# ------------------------------------------------------------------------------

import os
import time
from os import path
from subprocess import Popen, PIPE

#import matplotlib

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QDialog
from PyQt4.uic import loadUi

from nicm.gui.tools.uitools import DlgPresets, runDlgStandalone, selectDirectory


class LogViewer(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        loadUi(path.join(path.dirname(__file__), 'logviewer.ui'), self)
        self.connect(self.viewBtn, SIGNAL('clicked()'), self.view)
        self.connect(self.logfileList,
                     SIGNAL('doubleClicked(const QModelIndex &)'), self.view)
        self.connect(self.closeBtn, SIGNAL('clicked()'), self.close)
        self.connect(self.devnameList,
                     SIGNAL('currentRowChanged(int)'), self.updateFiles)
        self.connect(self.selectDir, SIGNAL('clicked()'), self.selectLogDir)
        self.connect(self.logfileDir,
                     SIGNAL('textChanged(const QString &)'), self.updateList)
        self.presets = DlgPresets('logviewer', [
                (self.logfileDir, STDLOGPATH),
                (self.devnameList, '')])
        self.presets.load()

    def selectLogDir(self):
        selectDirectory(self.logfileDir, self)

    def updateList(self, newlogpath):
        newlogpath = str(newlogpath)
        if not path.isdir(newlogpath):
            return
        self.devnameList.clear()
        self.logfileList.clear()
        self.logpath = newlogpath
        self.logfiles = {}
        for fn in os.listdir(newlogpath):
            if fn.startswith('cmd') or fn.startswith('error') \
                    or not fn.endswith('.log'):
                continue
            devname, date = fn[:-18], fn[-18:-4]
            date = time.strptime(date, '%Y%m%d%H%M%S')
            self.logfiles.setdefault(devname, []).append(
                (date, path.join(newlogpath, fn)))
        for lst in self.logfiles.itervalues():
            lst.sort()

        for devname in sorted(self.logfiles):
            self.devnameList.addItem(devname)

        self.devname = ''
        self.updateFiles()

    def updateFiles(self, *args):
        try:
            self.devname = str(self.devnameList.currentItem().text())
        except AttributeError:
            return
        self.logfileList.clear()
        for date, fname in self.logfiles[self.devname]:
            date = time.strftime('%d-%m-%Y, %H:%M:%S', date)
            self.logfileList.addItem('%s, started %s' % (self.devname, date))

    def close(self, *args):
        """
        Close the window and save the settings.
        """
        self.presets.save()
        self.accept()
        return True

    def view(self, *args):
        fname = self.logfiles[self.devname][self.logfileList.currentRow()][1]
        gp = Popen(['/usr/bin/gnuplot', '-persist'], stdin=PIPE)
        gp.communicate('''
set term x11 title "%(wt)s"
set term wx title "%(wt)s"
set xdata time
set timefmt "%%Y%%m%%d%%H%%M%%S"
set format x "%%d-%%m\\n%%H:%%M"
set grid back lw 0.4
plot "%(fn)s" u 3:2 every ::3 w l lc rgb "#ccccff" t "%(fn)s", \
           "" u 3:2 every ::3 w p ps 0.5 lc rgb "#0000cc" pt 6 t ""
''' % {'wt': 'Log: %s, %s' % (self.devname,
                              self.logfileList.currentItem().text()),
       'fn': fname})


if __name__ == "__main__":
    runDlgStandalone(LogViewer)
