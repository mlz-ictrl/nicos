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

"""Allows to measure thermal conductivity."""

import time
from time import time as currenttime

import numpy as np

from nicos import session
from nicos.core import SIMULATION, Attach, ConfigurationError, Param, \
    Readable, SubscanMeasurable, Waitable, anytype
from nicos.core.params import Value, absolute_path, floatrange, intrange, \
    listof
from nicos.core.scan import ElapsedTime, SweepScan
from nicos.devices.entangle import StringIO


class Conductivity(SubscanMeasurable):
    """Measure thermal conductivity of the sample."""

    attached_devices = {
        'seebeck': Attach('Device for reading Seebeck voltage', Readable),
        'voltage': Attach('Keithley to read thermocouple voltage', Waitable),
        'k6221': Attach('Keithley current source', StringIO,
                        optional=True),
        'temp': Attach('Temp to read in K', Readable),
    }

    parameters = {
        'readresult': Param('Storage for processed results from detector, to'
                            'be returned from doRead()',
                            type=listof(anytype), settable=True,
                            internal=True,),
        'current': Param('current in Amps to heat',
                         type=floatrange(0, 0.1), settable=True,
                         default=0.001,),
        'heater': Param('status of the heater',
                        type=intrange(0, 1), settable=True, internal=True,
                        default=0,),
        'heatercalfile': Param('Heater calibration file',
                               type=absolute_path, settable=True),
        'heatercalpoly': Param('Heater calibration polynom coefficients '
                               'R=(... + c1*T^2 + c2*T + c3) ohm',
                               type=listof(float), settable=True, default=[0]),
        'sample_l': Param('Length of the sample',
                          type=float, settable=True, default=1, unit='mm'),
        'sample_a': Param('Area of the sample', type=float,
                          settable=True, default=1, unit='mm2'),
    }

    def commCurrent(self, cmd, response=False):
        if self._attached_voltage.CanCurrent:
            return self._attached_voltage.commCurrent(cmd, response)
        elif self._attached_k6221 is not None:
            self.log.debug('commC: %r', cmd)
            if response:
                resp = self._attached_k6221.communicate(cmd)
                self.log.debug('  ->: %r', resp)
                return resp
            self._attached_k6221.writeLine(cmd)
            time.sleep(0.01)
            return None
        raise ConfigurationError('No current source attached!')

    _R = None
    _S = None
    _T = None

    # tempheatercal = [100]  # ohm

    def f(self, x):
        return (((- 9.63637553312268E-009 * x) - 0.0003238565) * x +
                0.2341843218) * x - 0.2222214359

    def getHeaterRes(self, t):
        result = 0
        for i in self.heatercalpoly:
            result = result * t + i
        return result

    def doInit(self, mode):
        self._preset = None
        if self._attached_voltage.unit != 'uV':
            self.log.warning('Changing units of attached voltmeter to uV.')
            self._attached_voltage.unit = 'uV'
        if self._attached_seebeck.unit != 'uV':
            self.log.warning('Changing units of attached voltmeter for Seebeck to uV.')
            self._attached_seebeck.unit = 'uV'

    def doSetPreset(self, **preset):
        self._preset = preset

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _processDataset(self, dataset):
        # get xy values
        x = []
        y = []
        for subset in dataset.subsets:
            for i, val in enumerate(subset.envvalueinfo):
                if val.name == 'etime':
                    x.append(subset.envvaluelist[i])
                elif val.name == self._attached_voltage.name:
                    y.append(subset.envvaluelist[i])
        fitfrom = max(x) - self._attached_voltage.window / 2
        return np.mean([b for a, b in zip(x, y) if a > fitfrom])

    def doStart(self):
        # self.log.info("measure delta")
        # self._attached_delta.start()
        # while self._attached_delta.status()[0] != status.OK:
        #     time.sleep(1)
        # measuredDelta = self._attached_delta.read()
        # self.log.info(f"delta finished: {measuredDelta}")
        if session.mode != SIMULATION:
            self._attached_voltage.start(None)
            time.sleep(2)
            timer = ElapsedTime('t')
            timer.started = currenttime()
            ds = SweepScan(
                [self._attached_voltage], [], -1, detlist=[], envlist=[timer],
                preset={'delay': 0.01}, subscan=True).run()
            self._R = self._processDataset(ds)
            self.log.info('reference voltage: %s', self._R)
            # measure U1
            # self._attached_delta._disarm(True)
            # self._attached_delta.commVoltage('*CLS;SYST:PRES')
            # time.sleep(0.1)
            # self._attached_delta.commVoltage(':CONF:VOLT')
            # resp = ''
            # time.sleep(0.1)
            # while not self.isfloat(resp):
            #     resp = self._attached_delta.commVoltage('READ?', True)
            #     session.delay(0.05)
            U1 = self._attached_seebeck.read(0)
            self.log.debug('U1 recorded: %s', U1)

            self._attached_voltage.start(None)
            time.sleep(2)

            # Turn on current
            self.commCurrent(f'SOUR:CURR {self.current}')
            self.commCurrent('OUTP ON')
            self.heater = 1

            timer = ElapsedTime('t')
            timer.started = currenttime()
            ds = SweepScan(
                [self._attached_voltage], [], -1, detlist=[], envlist=[timer],
                preset={'delay': 0.01}, subscan=True).run()
            self._S = self._processDataset(ds)
            self.log.info('heated voltage: %s', self._S)
            # measure U2
            # self._attached_delta.commVoltage('*CLS;SYST:PRES')
            # time.sleep(0.1)
            # self._attached_delta.commVoltage(':CONF:VOLT')
            # resp = ''
            # time.sleep(0.1)
            # while not self.isfloat(resp):
            #     resp = self._attached_delta.commVoltage('READ?', True)
            #     time.sleep(0.05)
            # U2 = float(resp) * 1e6
            U2 = self._attached_seebeck.read(0)
            self.log.debug('U2 recorded: %s', U2)
            # turn off current:
            self.commCurrent('OUTP OFF')
            self.heater = 0

            self._T = self._attached_temp.read(0)
            self.log.info('used system T: %s', self._T)
            # get conductance
            dT = abs(self._S - self._R) / self.f(self._T)
            Q = self.getHeaterRes(self._T) * self.current * self.current
            cond = Q / dT * self.sample_l / self.sample_a * 1000

            # self.readresult = measuredDelta[0], measuredDelta[1], cond, self.current * 1000
            self.readresult = cond, dT, self.current * 1000, U1, U2, self._R, self._S, Q

            # self.log.info("scan ended")

    def valueInfo(self):
        if self.readresult:
            return (Value('kappa', unit='W/K.m', fmtstr=self.fmtstr),
                    Value('deltaT', unit='K', fmtstr=self.fmtstr),
                    Value('I', unit='mA', fmtstr=self.fmtstr),
                    Value('U1', unit='uV', fmtstr=self.fmtstr),
                    Value('U2', unit='uV', fmtstr=self.fmtstr),
                    Value('R', unit='uV', fmtstr=self.fmtstr),
                    Value('S', unit='uV', fmtstr=self.fmtstr),
                    Value('Q', unit='W', fmtstr=self.fmtstr),
                    )
        return ()

    def doRead(self, maxage=0):
        return self.readresult

    def doFinish(self):
        pass
