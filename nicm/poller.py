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
from nicm.errors import NicmError


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
            try:
                dev = nicos.getDevice(devname)
            except NicmError, err:
                self.printwarning('error creating %s' % devname, exc=err)
                continue
            self.printinfo('starting thread for %s' % dev)
            interval = dev.pollinterval
            if interval > 5:
                sleeper = self._long_sleep
            else:
                sleeper = time.sleep
            worker = threading.Thread(target=self._worker_thread,
                                      args=(dev, interval, sleeper))
            worker.setDaemon(True)
            worker.start()
            self._workers.append(worker)

    def _long_sleep(self, interval):
        te = time.time() + interval
        while time.time() < te:
            if self._stoprequest:
                return
            time.sleep(5)

    def _worker_thread(self, dev, interval, sleep):
        errcount = 0
        orig_interval = interval
        while not self._stoprequest:
            self.printdebug('polling %s' % dev)
            try:
                dev.status()
                dev.read()
            except Exception, err:
                if errcount < 5:
                    # only print the warning the first five times
                    self.printwarning('error reading %s' % dev, exc=err)
                elif errcount == 5:
                    # make the interval a bit larger
                    interval *= 5
                errcount += 1
            else:
                if errcount > 0:
                    interval = orig_interval
                errcount = 0
            sleep(interval)

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
