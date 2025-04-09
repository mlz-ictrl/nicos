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

"""Allows to measure in delta mode of K6221 with switcher K7001."""

import time

import numpy as np

from nicos.core import SIMULATION, Attach, Measurable, Override, status
from nicos.core.params import Value
from nicos.devices.entangle import StringIO


def basicInit(commfunction, current):
    commfunction('*CLS;:TRAC:CLE')
    commfunction(':STAT:QUE:CLE')
    time.sleep(0.1)
    commfunction(':SOUR:DELTA:DELAY 0.062')
    commfunction(':SOUR:DELTA:COUNT 10;:TRAC:POIN 10')
    commfunction(':UNIT OHMS')
    commfunction(':SOUR:DELTA:HIGH %.4e' % current)
    commfunction(':SOUR:DELTA:LOW %.4e' % -current)
    commfunction(':FORM:SREG bin')


# will arm if not armed
def doArm(commfunction, current, points):
    armed = int(commfunction(':SOUR:DELTA:ARM?', response=True))
    # check max current
    remotecurrent = float(commfunction(':SOUR:DELTA:HIGH?', response=True))
    if current != remotecurrent:
        if armed:
            commfunction(':SOUR:SWE:ABOR')
            time.sleep(2)
            armed = 0
        commfunction(':SOUR:DELTA:HIGH %.4e' % current)
        commfunction(':SOUR:DELTA:LOW %.4e' % -current)
        time.sleep(0.5)
    # check points
    d = commfunction(':SOUR:DELTA:COUNT?', response=True)
    if int(d) != points:  # abort arm
        if armed:
            commfunction(':SOUR:SWE:ABOR')
            time.sleep(2)
            armed = 0
        commfunction(':SOUR:DELTA:COUNT %i' % points)
        commfunction(':TRAC:POIN %i' % points)
    # ARM
    if armed == 0:
        commfunction(':SOUR:DELTA:ARM')
        time.sleep(2)


class HCmeter(Measurable):

    attached_devices = {
        'k6221temp': Attach('Keithley to measure using delta method', StringIO),
        'k6221heater': Attach('Keithley for heater', StringIO),
    }

    _values = []
    _currentChannel = 0
    _lastStatus = (status.OK, 'idle')
    _statusCounter = 0

    _current = 0.00000005   # initial current
    _points = 5

    parameter_overrides = {
        'unit':         Override(mandatory=False, default='mOhm'),
        'pollinterval': Override(default=60),
        'maxage':       Override(default=70),
    }

    def commTemp(self, cmd, response=False):
        self.log.debug('commT: %r', cmd)
        if response:
            resp = self._attached_k6221temp.communicate(cmd)
            self.log.debug('  ->: %r', resp)
            return resp
        self._attached_k6221temp.writeLine(cmd)
        time.sleep(0.01)

    def commHeat(self, cmd, response=False):
        self.log.debug('commH: %r', cmd)
        if response:
            resp = self._attached_k6221heater.communicate(cmd)
            self.log.debug('  ->: %r', resp)
            return resp
        self._attached_k6221heater.writeLine(cmd)
        return None     # no ACK means nothing good!

    def doInit(self, mode):
        self._statusCounter = 0
        if mode != SIMULATION:
            basicInit(self.commTemp, self._current)
            self.log.debug('init Thermometer keithley complete')
            basicInit(self.commHeat, self._current)
            self.log.debug('init Heater keithley complete')

    def parseData(self, data):
        if ',' in data:
            data = data.split(',')[0::2]
            data = np.array(data).astype(float)
            value = data.mean()[0]  # TODO: Check use of index
            if len(data) > 1:
                dvalue = data.std(ddof=1)[0]  # TODO: Check use of index
            else:
                dvalue = 0
            self.log.debug('result %d: %f +- %f', len(data), value, dvalue)
        else:
            value = 0
            dvalue = 0
        return value, dvalue

    def checkPuck(self):
        self.log.debug('check puck started')

        # measure heater
        doArm(self.commHeat, self._current, self._points)
        self.commHeat(':TRAC:CLE')
        self.commHeat(':INIT:IMM')
        time.sleep(2)  # TODO FIX!
        d = self.commHeat(':TRAC:DATA?', response=True)
        self.log.debug('data->: %r', d)
        self.log.info('Heater Resistivity: %f +- %f', *self.parseData(d))

        # measure thermometer
        doArm(self.commTemp, self._current, self._points)
        self.commTemp(':TRAC:CLE')
        self.commTemp(':INIT:IMM')
        time.sleep(2)  # TODO FIX!
        d = self.commTemp(':TRAC:DATA?', response=True)
        self.log.debug('data->: %r', d)
        self.log.info('Thermometer resistivity: %f +- %f', *self.parseData(d))

    def doStart(self):
        self.log.debug('asked doStart')
        doArm(self.commTemp, self._current, [])  # TODO: Check last param
        self._measure()

    def _measureNext(self):
        self.commCurrent(':TRAC:CLE')
        self.commCurrent(':INIT:IMM')
        time.sleep(1.5)

    def doSetPreset(self, **preset):
        self.log.debug('asked doSetPreset')
        t = preset.get('t')
        if t is None:
            t = max(self.points, 2)
        else:
            t = max(t, 2)
            self.points = t
        # check settings
        d = self.commCurrent(':SOUR:DELTA:COUNT?', response=True)
        if int(d) != t:  # abort arm
            self.commCurrent(':SOUR:SWE:ABOR')
            time.sleep(2)
            self.commCurrent(':SOUR:DELTA:COUNT %i' % t)
            self.commCurrent(':TRAC:POIN %i' % t)
            self.commCurrent(':SOUR:DELTA:HIGH %f' % self.current)
            self.commCurrent(':SOUR:DELTA:LOW %f' % -self.current)
            self.commCurrent(':SOUR:DELTA:ARM')  # arm again
            time.sleep(2)
        self.log.debug('preset set to %i measurements', t)

    def doRead(self, maxage=0):
        self.log.debug('asked doRead')
        # time.sleep(0.1)
        d = self.commCurrent(':TRAC:DATA?', response=True)
        self.log.debug('data->: %r', d)
        value, dvalue = self.parseData(d)
        self._values[self._currentChannel * 2 - 2] = value
        self._values[self._currentChannel * 2 - 1] = dvalue
        self.log.debug('vals->: %r', self._values)
        return self._values

    def doStatus(self, maxage=0):
        self.log.debug('asked doStatus')
        stb = int(self.commCurrent('*STB?', response=True)[2:], 2)
        oper = int(self.commCurrent('STAT:OPER?', response=True)[2:], 2)
        self.log.debug('test 1')
        if (stb & (1 << 2)) != 0:
            self._lastStatus = (status.ERROR, 'Error in Status byte')
            # try reset
            self.commCurrent(':STAT:QUE:CLE')  # clear error que
            return self._lastStatus
        self.log.debug('test 2')
        if oper == 0:  # no change in status
            if self._lastStatus[0] == status.ERROR:
                self._lastStatus = (status.OK, 'idle')
            self._statusCounter += 1
            if self._statusCounter > 5:
                self._lastStatus = (status.OK, 'idle')
                self._statusCounter = 0
            return self._lastStatus
        self._statusCounter = 0
        self.log.debug('test 3')
        if (oper & (1 << 1)) != 0:  # done
            if self._currentChannel == len(self.channels):
                self._lastStatus = (status.OK, 'done')
                return self._lastStatus
            else:
                self.doRead()
                self._measureNext()
                self._lastStatus = (status.BUSY, 'measuring')
                return self._lastStatus
        self.log.debug('test 4')
        if (oper & (1 << 10)) != 0:  # idle
            self._lastStatus = (status.OK, 'idle')
            return self._lastStatus
        self.log.debug('test 4a')
        if (oper & (1 << 2)) != 0:
            self._lastStatus = (status.OK, 'aborted')
            return self._lastStatus
        self.log.debug('test 5')
        if (oper & (1 << 3)) != 0:  # sweeping
            self.log.debug('weird')
            self._lastStatus = (status.BUSY, 'measuring ch%d' % self._currentChannel)
            return self._lastStatus
        self.log.debug('test 6')
        if (oper & (1 << 11)) != 0:
            self.log.debug('error happened')
            self._lastStatus = (status.ERROR, 'Error in operation status')
            self.log.debug('error happened 2: %r', self._lastStatus)
            return self._lastStatus
        self.log.debug('test 7')

    def valueInfo(self):
        """Return list of active channels."""
        ret = ()
        for i in range(1, len(self.channels) + 1):
            ret = ret + (Value('Ch%d' % i, unit=self.unit, fmtstr=self.fmtstr, errors='next'),
                         Value('dCh%d' % i, unit=self.unit, fmtstr=self.fmtstr, type='error'),
                         )
        return ret

    def doReset(self):
        self.log.debug('asked doReset')
        self.commCurrent(':STAT:QUE:CLE')  # clear error que
        # self.commCurrent(':SOUR:SWE:ABOR')  # clear error que
        # time.sleep(3)

    def doFinish(self):
        pass

    def doStop(self):
        pass
