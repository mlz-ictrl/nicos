#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <Matthias.Pomm@hereon.de>
#
# ****************************************************************************
"""
Some helper classes to handle CPU usage
"""

import psutil

from nicos.core import Readable, status
from nicos.core.params import Param, none_or, floatrange

from nicos_demo.demo.devices.cpuload import CPULoad


class CPUPercentage(CPULoad):

    parameters = {
        'index': Param('CPU number',
                       type=none_or(int), settable=True, default=None),
    }

    def doStatus(self, maxage=0):
        return status.OK, '%s' % self.index

    def _run(self):
        while True:
            if self.index is None:
                self._setROParam(
                    'lastvalue', psutil.cpu_percent(self.interval))
            else:
                self._setROParam(
                    'lastvalue', psutil.cpu_percent(percpu=True)[self.index])


class ProcessIdentifier(Readable):
    """Read CPU percentage for a given process.

    High use of a CPU indicates a process running out of control.
    """
    _PIDint = None
    _PIDobject = None

    parameters = {
        'processname': Param('Name of the process to be checked',
                             type=str, settable=True, default='cache'),
        'interval': Param('Interval for load detection',
                          type=floatrange(0.1, 60),
                          default=0.1, settable=False,),
    }

    def loadint(self):
        self.log.debug('Get PID for >%s<', self.processname)
        self._PIDint = 'nothing found'
        # Search for processes containing the processname in command line
        # This is typical for NICOS processes where the main process is the
        # Python interpreter itself.
        for p in psutil.process_iter():
            if any(self.processname in c for c in p.cmdline()):
                self._PIDint = p.pid
                self._PIDobject = psutil.Process(self._PIDint)

    def doRead(self, maxage=0):
        if not isinstance(self._PIDint, int):
            self.loadint()
            if not isinstance(self._PIDint, int):
                return 101
        return self._PIDobject.cpu_percent(interval=self.interval)

    def doStatus(self, maxage=0):
        if self._PIDint is None:
            self.loadint()
        if isinstance(self._PIDint, int):
            return status.OK, '%d' % self._PIDint
        return status.WARN, self._PIDint
