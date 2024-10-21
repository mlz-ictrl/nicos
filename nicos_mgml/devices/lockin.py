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

"""Allows to measure with RS830 Lock-In amplifier"""

import time

from nicos.core import SIMULATION, Attach, Measurable, Override, Param, status
from nicos.core.params import Value, floatrange, listof, oneof
from nicos.devices.entangle import StringIO


class Lockinmeter(Measurable):

    parameters = {
        'channels': Param('Channels to measure',
                          type=listof(oneof('X', 'Y', 'R', 'theta', 'Aux IN 1',
                                            'Aux IN 2', 'Aux IN 3', 'Aux IN 4', )),
                          settable=True, default=['R', 'theta'],),
        'amplitude': Param('Sine Output Amplitude in Vrms. 0.004 ≤ x ≤5.000.',
                           type=floatrange(0.004, 5.0), settable=True,
                           unit='V', default=5.0,),
        'frequency': Param('Reference Frequency in Hz.',
                           type=float, settable=True,
                           unit='Hz', default=50.5,),
        'unit': Param('Unit for voltage values',
                      type=oneof('V', 'mV', 'uV', 'nV'), settable=True,
                      default='V',),
        'suffix': Param('Optional suffix of the channel name',
                        type=str, settable=True, default='',),
    }

    attached_devices = {
        'sr830': Attach('Stanford Lock-In Amplifier', StringIO),
    }

    _values = []
    _currentChannel = 0
    _lastStatus = (status.OK, 'idle')

    parameter_overrides = {
        'unit':         Override(mandatory=False, default='V'),
        'pollinterval': Override(default=60),
        'maxage':       Override(default=70),
    }

    def comm(self, cmd, response=False):
        self.log.debug('comm: %r', cmd)
        if response:
            resp = self._attached_sr830.communicate(cmd)
            self.log.debug('  ->: %r', resp)
            return resp
        self._attached_sr830.writeLine(cmd)
        time.sleep(0.01)
        return None     # no ACK means nothing good!

    def doInit(self, mode):
        if mode != SIMULATION:
            devstr = self.comm('*IDN?', response=True)
            if 'SR830' not in devstr:
                raise ValueError('Wrong instrument: %s' % devstr)
            self._writeParams()
            self.log.debug('init complete')

    def doStart(self):
        self.log.debug('asked doStart')
        self._writeParams()
        self._values = [0] * len(self.channels)
        self._currentChannel = 0
        self._laststatus = (status.BUSY, 'measuring')
        self._measureNext()

    def _writeParams(self):
        self.comm('FREQ %f' % self.frequency)
        self.comm('SLVL %f' % self.amplitude)

    def _measureNext(self):
        # measure next channel
        chan = self.channels[self._currentChannel]
        value = 0
        if 'Aux IN' in chan:
            # measure Aux input
            value = self.comm('OAUX? %d' % int(chan[7]), response=True)
        else:
            value = self.comm('OUTP? %d' % (['X', 'Y', 'R', 'theta'].index(chan) + 1),
                              response=True)
        multiplier = 1
        if chan != 'theta':
            if self.unit == 'mV':
                multiplier = 1000
            elif self.unit == 'uV':
                multiplier = 1e6
            elif self.unit == 'nV':
                multiplier = 1e9
        self._values[self._currentChannel] = float(value) * multiplier

        self._currentChannel += 1
        if self._currentChannel == len(self.channels):
            self._lastStatus = (status.OK, 'done')
        else:
            self.doRead()
            self._measureNext()

    def doSetPreset(self, **preset):
        self.log.debug('asked doSetPreset')

    def doRead(self, maxage=0):
        self.log.debug('asked doRead')
        return self._values

    def doStatus(self, maxage=0):
        self.log.debug('asked doStatus')
        return self._lastStatus

    def valueInfo(self):
        """Return list of active channels"""
        ret = ()
        for chan in self.channels:
            ret = ret + (Value(chan + self.suffix, unit='deg' if chan == 'theta' else self.unit, fmtstr=self.fmtstr),
                         )
        return ret

    def doReset(self):
        self.log.debug('asked doReset')
        # TODO

    def doFinish(self):
        pass

    def doStop(self):
        pass
