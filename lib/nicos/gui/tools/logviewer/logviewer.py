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

"""Cache logfile viewer tool."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

# ----- user changeable parameters ---------------------------------------------

# XXX get from nicos system
STDLOGPATH = '/data/cache'

# ------------------------------------------------------------------------------

import os
import time
import bsddb
from os import path
from subprocess import Popen, PIPE

#import matplotlib

from PyQt4.QtCore import SIGNAL, QDateTime
from PyQt4.QtGui import QDialog
from PyQt4.uic import loadUi

from nicos.cache.utils import load_entries
from nicos.gui.tools.uitools import DlgPresets, runDlgStandalone, selectDirectory


class LogViewer(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        loadUi(path.join(path.dirname(__file__), 'logviewer.ui'), self)
        self.connect(self.viewBtn, SIGNAL('clicked()'), self.view)
        self.connect(self.closeBtn, SIGNAL('clicked()'), self.close)
        self.connect(self.selectDir, SIGNAL('clicked()'), self.selectLogDir)
        self.presets = DlgPresets('logviewer', [
            (self.logfileDir, STDLOGPATH), (self.device, ''),
            (self.interval, ''), (self.fromdate, QDateTime.currentDateTime()),
            (self.todate, QDateTime.currentDateTime())])
        self.presets.load()

        self.todate.setDateTime(QDateTime.currentDateTime())

    def selectLogDir(self):
        selectDirectory(self.logfileDir, self)

    def close(self, *args):
        """
        Close the window and save the settings.
        """
        self.presets.save()
        self.accept()
        return True

    def view(self, *args):
        datefrom = self.fromdate.dateTime()
        dateto = self.todate.dateTime()
        # XXX might not be correct for localtime
        tstart = time.mktime(time.localtime(datefrom.toTime_t()))
        tend = time.mktime(time.localtime(dateto.toTime_t()))
        days = range(datefrom.daysTo(dateto)+1)
        try:
            interval = int(self.interval.text())
        except ValueError:
            interval = 30

        key = 'nicos/%s/value' % str(self.device.text()).lower()

        f = open('/tmp/logfile.tmp', 'w')
        try:
            for i in days:
                day = datefrom.addDays(i).toString('yyyy-MM-dd')
                cachefile = path.join(str(self.logfileDir.text()), str(day))
                try:
                    cache = bsddb.hashopen(cachefile, 'r')
                except bsddb.db.DBNoSuchFileError:
                    continue

                if key not in cache:
                    print 'Not found!'
                    continue

                entries = load_entries(cache[key])
                ltime = 0
                for entry in entries:
                    if entry.time > ltime + interval:
                        if tstart <= entry.time <= tend:
                            f.write('%s %s\n' % (entry.time, entry.value))
                            ltime = entry.time
        finally:
            if f.tell() == 0:
                # XXX message box that no data were found
                return
        f.close()

        fname = '/tmp/logfile.tmp'
        gp = Popen(['/usr/bin/gnuplot', '-persist'], stdin=PIPE)
        gp.communicate('''
set term x11 title "%(wt)s"
set term wx title "%(wt)s"
set xdata time
#set timefmt "%%Y%%m%%d%%H%%M%%S"
set timefmt "%%s"
set format x "%%d-%%m\\n%%H:%%M"
set grid back lw 0.4
#plot "%(fn)s" u 3:2 every ::3 w l lc rgb "#ccccff" t "%(fn)s", \
#           "" u 3:2 every ::3 w p ps 0.5 lc rgb "#0000cc" pt 6 t ""
plot "%(fn)s" u 1:2 w l lc rgb "#ccccff" t "log", \
           "" u 1:2 w p ps 0.5 lc rgb "#0000cc" pt 6 t ""
''' % {'wt': 'Log: %s, %s' % (self.device.text(), ''),
       'fn': fname})


if __name__ == "__main__":
    runDlgStandalone(LogViewer)
