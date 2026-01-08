# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Alexander Söderqvist <alexander.soederqvist@psi.ch>
#
# *****************************************************************************

"""NICOS demo class displaying the CPU load"""

import psutil

from nicos import session
from nicos.core import POLLER, SIMULATION, Param, Readable, status
from nicos.core.device import listof
from nicos.core.params import floatrange
from nicos.utils import createThread


class CPULoad(Readable):

    parameters = {
        'interval':  Param('Interval for load detection',
                           type=floatrange(0.1, 60),
                           default=0.1, settable=False,),
        'lastvalue': Param('Last obtained value', type=float,
                           internal=True, mandatory=False, default=0.0),
    }

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        # create only run ONE thread: in the poller
        # it may look stupid, as the poller already has a thread polling read()
        # now imagine several such devices in a setup.... not so stupid anymore
        if session.sessiontype == POLLER:
            self._thread = createThread('measure cpuload', self._run)

    def doWriteInterval(self, value):
        self.pollinterval = max(1, 2 * value)
        self.maxage = max(3, 5 * value)

    def doRead(self, maxage=0):
        return self.lastvalue

    def doStatus(self, maxage=0):
        return status.OK, ''

    def _run(self):
        while True:
            self._setROParam('lastvalue', psutil.cpu_percent(self.interval))


class ProcessCPULoad(Readable):
    """Read CPU percentage for a given process.
    This device tries to find a process whose command line invocation includes
    all the strings given in the parameter `process_strings`, this is only
    settable through the setup file. It picks the first matching process it
    finds. The CPU Load is returned as a percentage and represented as
    the `Value` of this device.

    If for any reason the processes is respawned, the device tries to refind
    a new process matching the same process strings in order to possibly
    recover. If the process becomes a zombie, it does nothing other
    than reporting it's a zombie.
    """
    parameters = {
        'process_strings': Param('List of strings that are checked against '
                                 'the process cmdline',
                                 type=listof(str), settable=False),
    }

    def init(self):
        Readable.init(self)
        self._findprocess()

    def _findprocess(self):
        self.log.debug('Get PID for >%s<', self.process_strings)
        self._PIDint = 'nothing found'
        self._PIDobject = None
        # Search for processes containing the process strings in command line
        for p in psutil.process_iter():
            try:
                # Take the first process matching all strings
                if set(self.process_strings).issubset(set(p.cmdline())):
                    self._PIDint = p.pid
                    self._PIDobject = psutil.Process(self._PIDint)
                    return
            except psutil.ZombieProcess:
                # This covers the case when the system has any zombie processes
                continue
            except (psutil.AccessDenied):
                # This covers the case when on macOS a system process is checked
                continue
        self.log.warning('Process with string %s not found', self.process_strings)

    def doRead(self, maxage=0):
        if self._PIDobject is not None:
            # Check the process utilization since last call.
            # Ergo interval is determined by polling period, and this is non-blocking
            return self._PIDobject.cpu_percent()

    def doStatus(self, maxage=0):
        if self._PIDobject is None:
            self._findprocess()
            return status.WARN, "No process, trying to reinitialize"
        try:
            if self._PIDobject.status() == psutil.STATUS_ZOMBIE:
                return status.ERROR, f'{self._PIDint} is a zombie'
            if self._PIDobject.is_running():
                return status.OK, '%d' % self._PIDint
            self._PIDobject = None
            return status.ERROR, f"{self._PIDint} isn't running."
        except psutil.NoSuchProcess:
            self._PIDobject = None
            return status.ERROR, 'Process stopped for unknown reason.'
