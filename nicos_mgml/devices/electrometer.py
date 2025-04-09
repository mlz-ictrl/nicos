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
#   Petr Čermák <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""Allows to measure with RS830 Lock-In amplifier."""

import time

from nicos.core import SIMULATION, Attach, Measurable, Override, status
from nicos.devices.entangle import StringIO


class K6517(Measurable):

    attached_devices = {
        'k6517': Attach('Keithley K6517 electrometer bus', StringIO),
    }

    _lastValue = 0
    _lastStatus = (status.OK, 'idle')

    parameter_overrides = {
        'unit':         Override(mandatory=False, default='pA'),
        'pollinterval': Override(default=60),
        'maxage':       Override(default=70),
    }

    def comm(self, cmd, response=False):
        self.log.debug('comm: %r', cmd)
        if response:
            # self._attached_k6517.writeLine(cmd)
            # resp = self._attached_k6517.readLine()
            resp = self._attached_k6517.communicate(cmd)
            self.log.debug('  ->: %r', resp)
            return resp
        self._attached_k6517.writeLine(cmd)
        time.sleep(0.01)
        return None     # no ACK means nothing good!

    def doInit(self, mode):
        if mode != SIMULATION:
            devstr = self.comm('*IDN?', response=True)
            if 'MODEL 6517B' not in devstr:
                raise ValueError('Wrong instrument: %s' % devstr)
            self.log.debug('init complete')

    def doStart(self):
        self.log.debug('asked doStart')
        self._lastValue = 0
        self._laststatus = (status.BUSY, 'measuring')
        self._measure()

    def _measure(self):
        # measure next channel
        strval = self.comm('FETCH?', response=True)
        strval = (strval).split(',')[0]
        if strval[-4:] == 'NADC':
            strval = strval[:-4]
        self._lastValue = float(strval) * 1e12
        self._lastStatus = (status.OK, 'done')

    def doSetPreset(self, **preset):
        self.log.debug('asked doSetPreset')

    def doRead(self, maxage=0):
        self.log.debug('asked doRead')
        return self._lastValue

    def doStatus(self, maxage=0):
        self.log.debug('asked doStatus')
        return self._lastStatus

    def doReset(self):
        self.log.debug('asked doReset')
        # TODO

    def doFinish(self):
        pass

    def doStop(self):
        pass
