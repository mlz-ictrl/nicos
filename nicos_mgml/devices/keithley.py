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

from nicos.core import SIMULATION, Attach, Measurable, Override, Param, status
from nicos.core.params import Value, floatrange, listof
from nicos.devices.entangle import StringIO


class Deltameter(Measurable):

    parameters = {
        'channels': Param('Channels to measure in Keithley format',
                          type=listof(str), settable=True,
                          default=['1!3,2!3'],),
        'current': Param('Maximum current in Amps for the pulse of Delta method',
                         type=floatrange(0, 0.01), settable=True,
                         default=0.0002,),
        'points': Param('Number of independent measurements averaged in one '
                        'measurement',
                        type=int, settable=True, default=5,),
        'keeparmed': Param('If to keep keep k6221 armed after measurement',
                           type=bool, settable=True, default=True,),
    }

    attached_devices = {
        'k6221': Attach('Keithley to measure using delta method', StringIO),
        'k7001': Attach('Keithley to switch channels', StringIO,
                        optional=True),
    }

    _values = []
    _currentChannel = 0
    _lastStatus = (status.OK, 'idle')
    _statusCounter = 0

    parameter_overrides = {
        'unit':         Override(mandatory=False, default='mOhm'),
        'pollinterval': Override(default=60),
        'maxage':       Override(default=70),
    }

    def commCurrent(self, cmd, response=False):
        self.log.debug('commC: %r', cmd)
        if response:
            resp = self._attached_k6221.communicate(cmd)
            self.log.debug('  ->: %r', resp)
            return resp
        self._attached_k6221.writeLine(cmd)
        time.sleep(0.01)
        return None     # no ACK means nothing good!

    def commSwitcher(self, cmd, response=False):
        if self._attached_k7001:
            self.log.debug('commS: %r', cmd)
            if response:
                resp = self._attached_k7001.communicate(cmd)
                self.log.debug('  ->: %r', resp)
                return resp
            self._attached_k7001.writeLine(cmd)
        return None     # no ACK means nothing good!

    def commVoltage(self, cmd, response=False):
        self.log.debug('commV: %r', cmd)
        self._attached_k6221.writeLine(f':SYST:COMM:SER:SEND "{cmd}"')
        if response:
            time.sleep(0.5)
            resp = self._attached_k6221.communicate(':SYST:COMM:SER:ENT?')
            self.log.debug('  ->: %r', resp)
            return resp
        return None     # no ACK means nothing good!

    def doInit(self, mode):
        self._statusCounter = 0
        if mode != SIMULATION:
            self.commCurrent('*CLS;:TRAC:CLE')
            time.sleep(0.1)
            self.commCurrent(':SOUR:DELTA:DELAY 0.062')
            self.commCurrent(':SOUR:DELTA:COUNT 10;:TRAC:POIN 10')
            self.commCurrent(':UNIT V')
            self.commCurrent(f':SOUR:DELTA:HIGH {self.current:e}')
            self.commCurrent(f':SOUR:DELTA:LOW {-self.current:e}')
            self.commCurrent(':FORM:SREG bin')
            # time.sleep(0.1)
            # self.commCurrent(':SOUR:DELTA:ARM')
            # time.sleep(2)
            self.log.debug('init complete')
            self.doReset()  # maybe only in the master (mode == MASTER)?

    def _disarm(self, check=False):
        if check:
            armed = int(self.commCurrent(':SOUR:DELTA:ARM?', response=True))
        if not check or armed:
            self.commCurrent(':SOUR:SWE:ABOR')  # disarm
            time.sleep(2)

    def _arm(self, check=False):
        if check:
            armed = int(self.commCurrent(':SOUR:DELTA:ARM?', response=True))
        if not check or armed == 0:
            self.commCurrent(':SOUR:DELTA:ARM')  # arm
            time.sleep(2)

    def doStart(self):
        self.log.debug('asked doStart')
        remotecurrent = float(self.commCurrent(':SOUR:DELTA:HIGH?', response=True))
        if self.current != remotecurrent:
            self._disarm(check=True)
            self.commCurrent(f':SOUR:DELTA:HIGH {self.current:e}')
            self.commCurrent(f':SOUR:DELTA:LOW {-self.current:e}')
            time.sleep(0.5)
            self._arm(check=False)
        else:
            self._arm(check=True)
        self._values = [0] * len(self.channels) * 2
        self._currentChannel = 0
        self._measureNext()

    def _measureNext(self):
        # set Next channel
        self._currentChannel += 1
        self._setChannel(self._currentChannel)
        # self.commCurrent(':TRAC:CLE')
        self.commCurrent(':INIT:IMM')
        time.sleep(1.5)

    def _setChannel(self, n):
        if n > len(self.channels):
            raise ValueError('Channel %d does not exist!' % n)
        self.commSwitcher(':OPEN ALL')
        self.commSwitcher(':CLOS (@%s)' % self.channels[n - 1])
        time.sleep(0.1)
        # self.commSwitcher('*OPC?', response=True)
        # self.commSwitcher(':CLOS:STATE?', response=True)

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
            armed = int(self.commCurrent(':SOUR:DELTA:ARM?', response=True))
            if armed == 1:  # need to disarm
                self.commCurrent(':SOUR:SWE:ABOR')
                time.sleep(2)
                self.commCurrent(':SOUR:DELTA:COUNT %i' % t)
                self.commCurrent(':TRAC:POIN %i' % t)
                self.commCurrent(':SOUR:DELTA:HIGH %f' % self.current)
                self.commCurrent(':SOUR:DELTA:LOW %f' % -self.current)
                self.commCurrent(':SOUR:DELTA:ARM')  # arm again
                time.sleep(2)
            else:
                self.commCurrent(':SOUR:DELTA:COUNT %i' % t)
                self.commCurrent(':TRAC:POIN %i' % t)
        self.log.debug('preset set to %i measurements', t)

    def doRead(self, maxage=0):
        self.log.debug('asked doRead')
        if len(self._values) > 0:
            # time.sleep(0.1)
            d = self.commCurrent(':TRAC:DATA?', response=True)
            self.log.debug('data->: %r', d)
            if ',' in d:
                d = d.split(',')[0::2]
                d = np.array(d).astype(float)
                value = d.mean() / self.current * 1000.0
                if len(d) > 1:
                    dvalue = d.std(ddof=1) / self.current * 1000.0
                else:
                    dvalue = 0
                self.log.debug('result %d: %f +- %f', len(d), value, dvalue)
            else:
                value = 0
                dvalue = 0
            self._values[self._currentChannel * 2 - 2] = value
            self._values[self._currentChannel * 2 - 1] = dvalue
            self.log.debug('vals->: %r', self._values)
            return self._values
        return []

    def doStatus(self, maxage=0):
        self.log.debug('asked doStatus')
        stb = int(self.commCurrent('*STB?', response=True)[2:], 2)
        oper = int(self.commCurrent('STAT:OPER?', response=True)[2:], 2)
        self.log.debug('test 1')
        if (stb & (1 << 2)) != 0:
            # which error?
            errors = []
            while True:
                er = self.commCurrent('STAT:QUE?', response=True)
                if er[:4] == '-213':
                    # cant init, rearm
                    self.log.info('Delta blocked, rearming...')
                    time.sleep(1)
                    self.commCurrent(':SOUR:SWE:ABOR')
                    time.sleep(2)
                    self.commCurrent(':SOUR:DELTA:ARM')  # arm again
                    time.sleep(3)
                    # return ok and try again
                    self._lastStatus = (status.OK, 'idle')
                    return self._lastStatus
                elif er[0] == '0':
                    break
                errors.append(f'({er})')
            self._lastStatus = (status.ERROR, f'Error in Status byte: {",".join(errors)}')
            # try reset
            self.commCurrent(':STAT:QUE:CLE')  # clear error que
            return self._lastStatus
        self.log.debug('test 2: %s', self._lastStatus)
        if oper == 0:  # no change in status
            if self._lastStatus[0] == status.ERROR:
                self.log.debug('going to idle after %s recovered error',
                               self._lastStatus[1])
                self._lastStatus = (status.OK, 'idle')
            self._statusCounter += 1
            if self._statusCounter > 5:
                self._lastStatus = (status.OK, 'idle')
                self.log.debug(
                    'going to idle after %d attemps', self._statusCounter)
                self._statusCounter = 0
            self.log.debug('No change in status, returning lastStatus %s',
                           self._lastStatus)
            return self._lastStatus
        self._statusCounter = 0
        self.log.debug('test 3')
        if (oper & (1 << 1)) != 0:  # done
            if self._currentChannel == len(self.channels):
                # finished
                if not self.keeparmed:
                    self._disarm(False)
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
            ret += (Value('Ch%d' % i, unit=self.unit, fmtstr=self.fmtstr, errors='next'),
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
