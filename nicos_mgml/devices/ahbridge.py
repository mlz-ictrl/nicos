# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""Allows to measure with AH2500A Capacitance bridge."""

import time

from nicos.core import Attach, Measurable, Override, status
from nicos.core.params import Value
from nicos.devices.entangle import StringIO


class Capacitance(Measurable):

    attached_devices = {
        'ah2500': Attach('AH 2500A capacitance bridge', StringIO),
    }

    parameter_overrides = {
        'unit':         Override(mandatory=False, default='pF'),
        'pollinterval': Override(default=60),
        'maxage':       Override(default=70),
    }

    _values = []
    _measuring = False

    def comm(self, cmd, response=False):
        self.log.debug('comm: %r', cmd)
        if response:
            resp = self._attached_ah2500.communicate(cmd)
            self.log.debug('  ->: %r', resp)
            return resp
        self._attached_ah2500.writeLine(cmd)
        time.sleep(0.01)

    def doStart(self):
        self.log.debug('asked doStart')
        self.comm('SINGLE')
        self._values = None
        self._measuring = True

    def doSetPreset(self, **preset):
        self.log.debug('asked doSetPreset')

    def doRead(self, maxage=0):
        self.log.debug('asked doRead')
        return self._values

    def doStatus(self, maxage=0):
        self.log.debug('asked doStatus')
        if self._measuring:
            try:
                time.sleep(1)
                self.log.debug('do readline')
                response = self._attached_ah2500.readLine()
                self.log.debug('ReadLine: %s', response)
            except Exception as e:
                self.log.debug('Error during read from GPIB: %s', e)
                self._measuring = False
                return (status.OK, 'done')
            self._measuring = False
            response = response.replace('=', '= ')
            results = {}
            buff = None
            key = None
            for v in response.split():
                if '=' in v:
                    if key and buff:
                        results[key] = buff
                    key = v[:v.index('=')]
                    buff = []
                elif key:
                    if len(buff) == 0:  # value
                        buff.append(float(v))
                    elif len(buff) == 1:  # units
                        buff.append(v)
            if 'C' in results and 'L' in results:
                self._values = [results['C'][0], results['L'][0]]
            else:
                self.log.info("Did not find values in '%s'", response)
            return (status.OK, 'done')

        return (status.OK, 'idle')

    def valueInfo(self):
        """Return list measured values."""
        return (
            Value('C', unit='pF', fmtstr=self.fmtstr),
            Value('L', unit='nS', fmtstr=self.fmtstr),
        )

    def doReset(self):
        self._values = None
        self._measuring = False

    def doFinish(self):
        pass

    def doStop(self):
        self._measuring = False
