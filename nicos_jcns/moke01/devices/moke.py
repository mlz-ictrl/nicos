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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

"""Device classes for MOKE setup."""

import os
import time
from contextlib import suppress
from datetime import datetime

import numpy
from uncertainties import ufloat  # pylint: disable=import-error

from nicos import session
from nicos.core import Attach, Param, device, errors, status, CanDisable
from nicos.core.sessions.utils import MASTER
from nicos.devices.entangle import AnalogInput, PowerSupply, Sensor
from nicos.devices.generic.magnet import MagnetWithCalibrationCurves
from nicos.utils import createThread
from nicos.utils.functioncurves import Curve2D

from nicos_jcns.moke01.utils import fix_filename, generate_output


class MokeMagnet(CanDisable, MagnetWithCalibrationCurves):

    attached_devices = {
        'intensity': Attach('Voltmeter reads intensity of a laser beam',
                            device.Readable),
    }

    parameters = {
        'baseline': Param(
            'Stores baseline curves of intensity vs magnetic field for '
            'different experiment modes in form of array of (X, Y(X)) tuples',
            dict, settable=True, default={'stepwise': {'polar': {},
                                                       'longitudinal': {}},
                                          'continuous': {'polar': {},
                                                         'longitudinal': {}}}
        ),
        'measurement': Param('Last measurement data', dict, settable=True),
    }

    def doInit(self, mode):
        MagnetWithCalibrationCurves.doInit(self, mode)
        self._measuring = False
        self._currentsource = self._attached_currentsource
        self._intensity = self._attached_intensity
        self._magsensor = self._attached_magsensor
        if mode == MASTER:
            self._Bvt, self._Intvt, self._BvI, self._IntvB = Curve2D(), \
                Curve2D(), Curve2D(), Curve2D()

    def doEnable(self, on):
        if on:
            self._attached_currentsource.enable()
        else:
            self._attached_currentsource.disable()
        self.prevtarget = 0

    def measure_intensity(self, mrmnt):
        self._measuring = True
        self.progress = self.maxprogress = self.cycle = 0
        self.mode = mrmnt['mode']
        self.ramp = mrmnt['ramp']
        mrmnt['time'] = datetime.now().strftime('%Y%m%d%H%M%S')
        mrmnt['name'] = f'{mrmnt["time"]}-{mrmnt["id"]}-' \
                        f'{mrmnt["field_orientation"][:3]}-' \
                        f'{mrmnt["exp_type"][:3]}'
        mrmnt['BvI'] = Curve2D()
        mrmnt['IntvB'] = Curve2D()
        mrmnt['baseline'] = \
            self.baseline[mrmnt['mode']][mrmnt['field_orientation']][str(mrmnt['ramp'])] \
            if str(mrmnt['ramp']) in self.baseline[mrmnt['mode']][mrmnt['field_orientation']].keys() \
                else []
        self.measurement = mrmnt

        try:
            if mrmnt['mode'] == 'stepwise':
                n = int(abs(mrmnt['Bmax'] - mrmnt['Bmin']) / mrmnt['step'])
                ranges = [[mrmnt['Bmin'], mrmnt['Bmax'], n, False],
                          [mrmnt['Bmax'], mrmnt['Bmin'], n, False]] * mrmnt['cycles']
                ranges[-1][2] += 1
                ranges[-1][3] = True
                self._BvI, self._IntvB = Curve2D(), Curve2D()
                self.maxprogress = sum(len(numpy.linspace(*r)) for r in ranges)
                for i, r in enumerate(ranges):
                    if not i % 2:
                        session.breakpoint(2)
                    self.cycle = i // 2
                    for _B in numpy.linspace(*r):
                        session.breakpoint(3)
                        self.start(_B)
                        self._hw_wait()
                        session.delay(mrmnt['steptime'])
                        B = None
                        while B is None:
                            with suppress(Exception):
                                B = self.read(0)
                        Int = None
                        while Int is None:
                            with suppress(Exception):
                                Int = self._intensity.read(0)
                        self._BvI.append((self._field2current(_B).n, _B))
                        self._IntvB.append((ufloat(B, self._magsensor.readStd(B)),
                                            ufloat(Int, self._intensity.readStd(Int))))
                        self.progress += 1
            elif mrmnt['mode'] == 'continuous':
                IBmax = self._field2current(mrmnt['Bmax']).n
                IBmin = self._field2current(mrmnt['Bmin']).n
                self.start(mrmnt['Bmin'])
                self._hw_wait()
                # runs the power supply in parallel thread
                if not self._cycling_thread:
                    self._cycling = True
                    self._cycling_thread = \
                        createThread('', self.cycle_currentsource,
                                     (IBmin, IBmax, mrmnt['ramp'], mrmnt['cycles']))
                else:
                    raise errors.NicosError(self, 'Power supply is busy.')
                # measures magnetic field and intensity vallues
                self._Bvt, self._Intvt, self._IntvB = Curve2D(), Curve2D(), Curve2D()
                _cycle = self.cycle
                while self._cycling:
                    if self.cycle != _cycle:
                        session.breakpoint(2)
                    _cycle = self.cycle
                    session.breakpoint(3)
                    try:
                        B = self.read(0)
                    except Exception:
                        B = None
                    if B:
                        self._Bvt.append((time.time(),
                                          ufloat(B, self._magsensor.readStd(B))))
                    try:
                        Int = self._intensity.read(0)
                    except Exception:
                        Int = None
                    if Int:
                        self._Intvt.append((time.time(),
                                            ufloat(Int, self._intensity.readStd(Int))))
                    if self._Ivt and self._Bvt:
                        self._BvI = Curve2D.from_two_temporal(self._Ivt, self._Bvt,
                                                              pick_yvt_points=True)
                    if self._Intvt and self._Bvt:
                        self._IntvB = Curve2D.from_two_temporal(self._Bvt, self._Intvt)
        finally:
            self._stop_requested = True
            if self._cycling_thread is not None:
                self._cycling_thread.join()
                self._cycling_thread = None
            self._measuring = False
            # stores the measurement in the cache
            mrmnt['BvI'] = self._BvI
            mrmnt['IntvB'] = self._IntvB
            self.measurement = mrmnt
            session.log.info('Measurement saving: %s', self.save_measurement(mrmnt))
            self.disable()

    def save_measurement(self, measurement):
        if not measurement or 'name' not in measurement.keys():
            return None
        try:
            folder = os.path.join(session.getDevice('Exp').dataroot, 'Measurements')
            os.makedirs(folder, exist_ok=True)
            filename = f'{measurement["name"]}.raw.txt'
            with open(os.path.join(folder, fix_filename(filename)), 'w',
                      encoding='utf-8') as f:
                f.write(generate_output(measurement))
            return os.path.join(folder, filename)
        except Exception as e:
            return f'error: {str(e)}'


class MokePowerSupply(PowerSupply):

    def doEnable(self, on):
        if not on:
            self.ramp = 400
            PowerSupply.start(self, 0)
            self._hw_wait()
        PowerSupply.doEnable(self, on)

    def doStart(self, target):
        if self.status(0)[0] == status.DISABLED:
            self.enable()
            self._hw_wait()
        PowerSupply.doStart(self, target)

    def doStop(self):
        PowerSupply.doStop(self)


class MokePSVoltage(AnalogInput):

    def doRead(self, maxage=0):
        return self._dev.voltage

    def doReadUnit(self):
        return 'V'


class MokeTeslameter(Sensor):

    attached_devices = {
        'temperature': Attach('Temperature, °C', device.Readable)
    }

    parameters = {
        'calibration_date': Param('Last calibration date in iso format', str),
        'probe_wire_length': Param('Length of probe cable in meters', float),
    }

    def doInit(self, mode):
        self._T = self._attached_temperature

    def readStd(self, value):
        # value is ÷/* 1000 because the NICOS device displays values in mT
        value = abs(value) / 1000
        i = self._dev.GetProperties().index('range')
        _range = float(self._dev.GetProperties()[i + 1].split(' T')[0])
        Tdeg = self._T.read(0)
        years = int((datetime.now() -
                     datetime.strptime(self.calibration_date, '%Y-%m-%d')).days
                    / 365)
        return (1e-4 * value + 6e-5 * _range +
                (1e-5 * value + (1e-6 + 3e-6 * _range)) * abs(Tdeg - 25) +
                3e-6 * self.probe_wire_length * abs(Tdeg - 25) +
                years * 1e-3 * value) * 1000


class MokeVoltmeter(Sensor):

    accuracies = {
        0.1: {
            1: numpy.array([30, 30]),
            90: numpy.array([40, 35]),
            365: numpy.array([50, 35]),
        },
        1: {
            1: numpy.array([15, 6]),
            90: numpy.array([25, 7]),
            365: numpy.array([30, 7]),
        },
        10: {
            1: numpy.array([15, 4]),
            90: numpy.array([20, 5]),
            365: numpy.array([30, 5]),
        },
        100: {
            1: numpy.array([15, 6]),
            90: numpy.array([30, 6]),
            365: numpy.array([45, 6]),
        },
        1000: {
            1: numpy.array([20, 6]),
            90: numpy.array([35, 6]),
            365: numpy.array([45, 6]),
        },
    }

    temp_coefs = {
        0.1: numpy.array([2, 6]),
        1: numpy.array([2, 1]),
        10: numpy.array([2, 1]),
        100: numpy.array([5, 1]),
        1000: numpy.array([5, 1]),
    }

    attached_devices = {
        'temperature': Attach('Temperature, °C', device.Readable)
    }

    parameters = {
        'calibration_date': Param('Last calibration date in iso format', str),
    }

    def doInit(self, mode):
        self._T = self._attached_temperature

    def readStd(self, value):
        # value is ÷/* 1000 because the NICOS device displays values in mV
        value = abs(value) / 1000
        days = (datetime.now() -
                datetime.strptime(self.calibration_date, '%Y-%m-%d')).days
        meas_range = None
        for r in MokeVoltmeter.accuracies.keys():
            if value % r == value:
                meas_range = r
                break
        err = MokeVoltmeter.accuracies[meas_range][365]
        for limit in MokeVoltmeter.accuracies[meas_range]:
            if days < limit:
                err = MokeVoltmeter.accuracies[meas_range][limit]
                break
        temp = self._T.read(60)
        if not 18 < temp < 28:
            err += MokeVoltmeter.temp_coefs[meas_range]
        return (value * err[0] + meas_range * err[1]) * 1e-6 * 1000
