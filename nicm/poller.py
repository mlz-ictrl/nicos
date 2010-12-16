#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS device polling application
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""
Contains a process that polls devices automatically.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time
import threading

from nicm import nicos
from nicm.utils import dictof, listof
from nicm.device import Device, Readable, Param


class Poller(Device):

    parameters = {
        'processes': Param('Poller processes', type=dictof(str, listof(str)),
                           mandatory=True),
    }

    def doInit(self):
        self._stoprequest = False
        self._workers = []

    def start(self, process):
        self.printinfo('poller starting')
        devices = self.processes[process]
        for devname in devices:
            dev = nicos.getDevice(devname)
            self.printinfo('starting thread for %s' % dev)
            worker = threading.Thread(target=self._worker_thread, args=(dev,))
            worker.setDaemon(True)
            worker.start()
            self._workers.append(worker)

    def _worker_thread(self, dev):
        errcount = 0
        interval = dev.pollinterval
        while not self._stoprequest:
            time.sleep(interval)
            self.printdebug('polling %s' % dev)
            try:
                dev.read()
                dev.status()
            except Exception, err:
                if errcount < 5:
                    # only print the warning the first five times
                    self.printwarning('error reading %s: %s' % (dev, err))
                errcount += 1
            else:
                errcount = 0

    def wait(self):
        while not self._stoprequest:
            time.sleep(1)
        for worker in self._workers:
            worker.join()

    def quit(self):
        self.printinfo('poller quitting...')
        self._stoprequest = True
        for worker in self._workers:
            worker.join()
        self.printinfo('poller finished')
