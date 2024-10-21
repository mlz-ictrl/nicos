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

"""Allows to measure in delta mode of K6221 with switcher K7001"""

import time

from nicos.core import SIMULATION, Attach, Measurable, Override, Param, status
from nicos.core.params import Value, floatrange, listof
from nicos.devices.entangle import StringIO


class Current(Measurable):

    parameters = {
        'channels': Param('Channels to measure in Keysight format',
                          type=listof(str), settable=True,
                          default=['111,122'],),
        'voltage': Param('Output voltage of the source',
                         default=0.01, unit='V',
                         type=floatrange(-50, 50), settable=True,),
        'current_compliance': Param('Maximum allowed current applied to the '
                                    'sample',
                                    type=floatrange(0, 100), settable=True,
                                    unit='mA', default=0.1,),
    }

    attached_devices = {
        'b2910bl': Attach('Keysight to measure', StringIO),
        'daq970': Attach('Keysight to switch channels', StringIO,
                         optional=True),
    }

    _values = []
    _currentChannel = 0
    _measuring = False
    _lastStatus = (status.OK, 'idle')
    _lastclosed = None

    parameter_overrides = {
        'unit':         Override(mandatory=False, default='A'),
    }

    def commCurrent(self, cmd, response=False):
        self.log.debug('commC: %r', cmd)
        if response:
            resp = self._attached_b2910bl.communicate(cmd)
            self.log.debug('  ->: %r', resp)
            return resp
        self._attached_b2910bl.writeLine(cmd)
        time.sleep(0.01)
        return None     # no ACK means nothing good!

    def commSwitcher(self, cmd, response=False):
        if self._attached_daq970:
            self.log.debug('commS: %r', cmd)
            if response:
                resp = self._attached_daq970.communicate(cmd)
                self.log.debug('  ->: %r', resp)
                return resp
            self._attached_daq970.writeLine(cmd)
        return None     # no ACK means nothing good!

    def doInit(self, mode):
        if mode != SIMULATION:
            # self.commCurrent('*CLS;:TRAC:CLE')
            # time.sleep(0.1)
            self.log.debug('init complete')
            # self.doReset()

    def doStart(self):
        self.log.debug('asked doStart')
        voltage = float(self.commCurrent(':SOUR:VOLT?', response=True))
        if self.voltage != voltage:
            self.commCurrent(f':SOUR:VOLT  {self.voltage:e}')
            self.log.debug(f'voltage changed to {voltage}')
        protection = float(self.commCurrent(':SENS:CURR:PROT?', response=True)) * 1000
        if self.current_compliance != protection:
            self.commCurrent(f':SENS:CURR:PROT  {self.current_compliance/1000:e}')
            self.log.debug(f'current compliance changed to {protection}')
        self._values = [0] * len(self.channels)
        self._currentChannel = 0
        self._measuring = True
        self._measureNext()

    def _measureNext(self):
        # set Next channel
        self._currentChannel += 1
        self._setChannel(self._currentChannel)
        # self.commCurrent(':TRAC:CLE')
        # self.commCurrent(':MEAS:CURR?')

        d = self.commCurrent(':MEAS:CURR?', response=True)
        self.log.debug('data->: %r', d)
        self._values[self._currentChannel - 1] = float(d) * 1000

        time.sleep(0.1)

        if self._currentChannel < len(self.channels):
            self.log.debug(f'Measuring of channel {self._currentChannel} finished.')
            self._measureNext()
        else:
            self.log.debug(f'Measuring of all channels finished, last was {self._currentChannel}')
            self._measuring = False

    def _setChannel(self, n):
        if n > len(self.channels):
            raise ValueError('Channel %d does not exist!' % n)
        ch = self.channels[n - 1]

        self.commSwitcher(':ROUT:CLOS:EXCL (@%s)' % ch)
        self.commSwitcher(':ROUT:CLOS (@%s)' % ch)
        # self._lastclosed = self.channels[n-1]
        time.sleep(0.4)
        # self.commSwitcher('*OPC?', response=True)
        # self.commSwitcher(':CLOS:STATE?', response=True)

    def doSetPreset(self, **preset):
        self.log.debug('asked doSetPreset')

    def doRead(self, maxage=0):
        self.log.debug('asked doRead')
        if self._mode != SIMULATION and len(self._values) > 0:
            # time.sleep(0.1)
            return self._values
        return []

    def doStatus(self, maxage=0):
        self.log.debug('asked doStatus')
        if self._measuring:
            return (status.BUSY, 'measuring')
        # self._lastStatus = (status.OK, 'idle')
        return (status.OK, 'idle')

    def valueInfo(self):
        """Return list of active channels"""
        ret = ()
        for i in range(1, len(self.channels) + 1):
            ret = ret + (Value('Ch%d' % i, unit=self.unit, fmtstr=self.fmtstr),
                         )
        return ret

    def doReset(self):
        self.log.debug('asked doReset')
        # self.commCurrent(':STAT:QUE:CLE')  #clear error que
        # self.commCurrent(':SOUR:SWE:ABOR')  #clear error que
        # time.sleep(3)

    def doFinish(self):
        pass

    def doStop(self):
        pass
