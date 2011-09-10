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

"""Cache logfile viewer tool."""

__version__ = "$Revision$"

# ----- user changeable parameters ---------------------------------------------

# XXX get from nicos system
STDLOGPATH = '/data/cache'

# ------------------------------------------------------------------------------

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

colors = [('#ccccff', '#0000cc'),
          ('#ffcccc', '#cc0000'),
          ('#ccffcc', '#00cc00'),
          ('#ffffaa', '#aaaa00'),
          ('#ffaaff', '#aa00aa'),
          ('#aaffff', '#00aaaa'),
          ('#ffaa00', '#cc6600'),
          ('#00ffaa', '#00cc66'),
          ('#aa00ff', '#6600cc')]

class LogViewer(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        loadUi(path.join(path.dirname(__file__), 'logviewer.ui'), self)
        self.connect(self.viewBtn, SIGNAL('clicked()'), self.view)
        self.connect(self.updateBtn, SIGNAL('clicked()'), self.update)
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

    def update(self, *args):
        self.view(0)

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

        devs = str(self.device.text()).lower().split(',')
        keys = ['nicos/%s' % (d if '/' in d else d+'/value') for d in devs]
        fnames = ['/tmp/logfile_%s.tmp' % dev.replace('/', '_') for dev in devs]
        fs = [open(fname, 'w') for fname in fnames]
        try:
            for i in days:
                day = datefrom.addDays(i).toString('yyyy-MM-dd')
                cachefile = path.join(str(self.logfileDir.text()), str(day))
                try:
                    cache = bsddb.hashopen(cachefile, 'r')
                except bsddb.db.DBNoSuchFileError:
                    continue

                for f, key in zip(fs, keys):
                    if key not in cache:
                        print 'Not found!'
                        continue

                    entries = load_entries(cache[key])
                    ltime = 0
                    for entry in entries:
                        if entry.time > ltime + interval:
                            if tstart <= entry.time <= tend:
                                f.write('%s %s\n' % (time.localtime(entry.time)[:6], entry.value))
                                ltime = entry.time
        finally:
            #if f.tell() == 0:
            #    # XXX message box that no data were found
            #    return
            pass
        [f.close() for f in fs]

        if args and args[0] in [0, 1]:
            if self.gp:
                self.gp.stdin.write('replot\n')
            return

        fname = '/tmp/logfile.tmp'
        self.gp = Popen(['/usr/bin/gnuplot', '-persist'], stdin=PIPE)
        comm = '''
set term x11 title "%(wt)s"
set term wx title "%(wt)s"
set xdata time
set timefmt "(%%Y, %%m, %%d, %%H, %%M, %%S)"
#set timefmt "%%s"
set format x "%%d-%%m\\n%%H:%%M"
set grid back lw 0.4
#plot "fns" u 3:2 every ::3 w l lc rgb "#ccccff" t "fns", \
#           "" u 3:2 every ::3 w p ps 0.5 lc rgb "#0000cc" pt 6 t ""
plot ''' % {'wt': 'Log: %s, %s' % (self.device.text(), ''),
            'fn': fname}
        for dev, fname, (c1, c2) in zip(devs, fnames, colors):
            comm += ''' "%(fn)s" u 1:7 w l lc rgb "%(c1)s" t "", \
            "" u 1:7 w p ps 0.5 lc rgb "%(c2)s" pt 6 t "%(dev)s",''' % \
            {'dev': dev, 'fn': fname, 'c1': c1, 'c2': c2}
        comm = comm[:-1] + '\n'
        self.gp.stdin.write(comm)


if __name__ == "__main__":
    runDlgStandalone(LogViewer)
