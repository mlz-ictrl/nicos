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
from nicm.device import Device, Readable
from nicm.utils import listof


class Poller(Device):

    parameters = {
        'devices': (listof(str), [], True, 'List of devices to poll.'),
        'interval': (int, 0, True, 'Interval for polling.'),
    }

    def doInit(self):
        self.__devices = [nicos.getDevice(devname, Readable)
                          for devname in self.devices]
        self._stoprequest = False

    def start(self):
        self._worker = threading.Thread(target=self._worker_thread)
        self._worker.start()

    def _worker_thread(self):
        self.printinfo('poller starting')
        while not self._stoprequest:
            time.sleep(self.interval)
            self.printdebug('starting polling run')
            for dev in self.__devices:
                self.printinfo('polling %s' % dev)
                try:
                    dev.read()
                except Exception, err:
                    self.printwarning('error reading %s: %s' % (dev, err))

    def wait(self):
        while not self._stoprequest:
            time.sleep(1)
        self._worker.join()

    def quit(self):
        self.printinfo('poller quitting...')
        self._stoprequest = True
        self._worker.join()
        self.printinfo('poller finished')
