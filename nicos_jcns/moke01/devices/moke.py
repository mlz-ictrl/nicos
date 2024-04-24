#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
from datetime import datetime
import os
import time

from nicos import session
from nicos.core import Attach, device, errors, Param, status
from nicos.core.sessions.utils import MASTER
from nicos.devices.entangle import AnalogInput, PowerSupply, Sensor
from nicos.devices.generic.magnet import MagnetWithCalibrationCurves
from nicos.utils import createThread
from nicos.utils.curves import curve_from_two_temporal
from nicos_jcns.moke01.utils import fix_filename, generate_output

import numpy
# pylint: disable=import-error
from uncertainties import ufloat


class MokeMagnet(MagnetWithCalibrationCurves):

    attached_devices = {
        'intensity': Attach('Voltmeter reads intensity of a laser beam',
                            device.Readable),
    }

    parameters = {
        'measurement': Param('Last measurement data', dict, settable=True),
    }

    def doInit(self, mode):
        MagnetWithCalibrationCurves.doInit(self, mode)
        self._currentsource = self._attached_currentsource
        self._intensity = self._attached_intensity
        self._magsensor = self._attached_magsensor
        if mode == MASTER:
            self._Bvt, self._Intvt, self._BvI, self._IntvB = [], [], [], []

    def measure_intensity(self, mode, Bmin, Bmax, ramp, cycles, step, steptime,
                          name, exp_type):
        self._cycling = True
        self._progress, self._maxprogress = 0, 0
        measurement = {}
        measurement['name'] = name
        measurement['time'] = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        measurement['exp_type'] = exp_type
        measurement['mode'] = mode
        self.mode = mode
        measurement['ramp'] = ramp
        self.ramp = ramp
        measurement['Bmin'] = Bmin
        measurement['Bmax'] = Bmax
        measurement['step'] = step
        measurement['steptime'] = steptime
        measurement['cycles'] = cycles
        measurement['BvI'] = []
        measurement['IntvB'] = []
        self.measurement = measurement

        if mode == 'stepwise':
            self.fielddirection = 'increasing' if self.read(10) < Bmin else 'decreasing'
            self.doStart(Bmin)
            self._hw_wait()
            session.delay(steptime)
            n = int(abs(Bmax - Bmin) / step)
            dB = abs(Bmax - Bmin) / (Bmax - Bmin) * abs(Bmax - Bmin) / n
            ranges = [(Bmin, Bmax, dB), (Bmax, Bmin, -dB)]
            self._BvI, self._IntvB = [], []
            self._maxprogress = sum(len(numpy.arange(*r)) for r in ranges) * cycles
            for i, r in enumerate(ranges * cycles):
                self.fielddirection = 'increasing' if i % 2 == 0 else 'decreasing'
                for _B in numpy.arange(*r):
                    self._progress += 1
                    self.doStart(_B)
                    session.delay(steptime)
                    B = None
                    while B is None:
                        B = self.doRead()
                    Int = None
                    while Int is None:
                        Int = self._intensity.doRead()
                    self._BvI.append((self._field2current(_B).n, _B))
                    self._IntvB.append((ufloat(B, self._magsensor.readStd(B)),
                                        ufloat(Int, self._intensity.readStd(Int))))
                    if self._stop_requested:
                        break
                if self._stop_requested:
                    break
            self._cycling = False
        elif mode ==  'continuous':
            self.fielddirection = 'decreasing'
            IBmin = self._field2current(Bmin).n
            self.fielddirection = 'increasing'
            IBmax = self._field2current(Bmax).n
            self.doStart(Bmin)
            self._hw_wait()
            session.delay(10) # saturates sample with Bmin field value
            # runs the power supply in parallel thread
            if not self._cycling_thread:
                self._cycling_thread = createThread('', self.cycle_currentsource,
                                                    (IBmin, IBmax, ramp, cycles,))
            else:
                raise errors.NicosError(self, 'Power supply is busy.')
            # measures magnetic field and intensity vallues
            self._Bvt, self._Intvt, self._IntvB = [], [], []
            while self._cycling and not self._stop_requested:
                if self._measuring:
                    try:
                        B = self.doRead()
                    except Exception:
                        B = None
                    if B:
                        self._Bvt.append((time.time(),
                                          ufloat(B, self._magsensor.readStd(B))))
                    try:
                        Int = self._intensity.doRead()
                    except Exception:
                        Int = None
                    if Int:
                        self._Intvt.append((time.time(),
                                            ufloat(Int, self._intensity.readStd(Int))))
                    self._BvI = curve_from_two_temporal(self._Ivt, self._Bvt,
                                                        interp_by='y')
                    self._IntvB = curve_from_two_temporal(self._Bvt, self._Intvt)
                else:
                    session.delay(0.1)
            self._cycling_thread.join()
            self._cycling_thread = None
        self.doStop()
        # stores the measurement in the cache
        measurement['BvI'] = self._BvI
        measurement['IntvB'] = self._IntvB
        self.measurement = measurement
        session.log.info('Measurement is saved to %s',
                         self.save_measurement(measurement))
        self._stop_requested = False

    def save_measurement(self, measurement):
        keys = ['name', 'time']
        if not measurement or not all(key in measurement.keys() for key in keys):
            return None
        folder = os.path.join(session.devices['Exp'].dataroot, 'Measurements')
        os.makedirs(folder, exist_ok=True)
        filename = f'{measurement["time"]} {measurement["name"]}.raw.txt'
        with open(os.path.join(folder, fix_filename(filename)), 'w',
                  encoding='utf-8') as f:
            f.write(generate_output(measurement))
        return os.path.join(folder, filename)


class MokePowerSupply(PowerSupply):

    def doEnable(self, on):
        if not on:
            current = self.read()
            if current < -7 or current > 7:
                self.ramp = 400
                PowerSupply.doStart(self, 0)
                self._hw_wait()
        PowerSupply.doEnable(self, on)
        self._hw_wait()

    def doStart(self, target):
        if self.doStatus()[0] == status.DISABLED:
            self.doEnable(True)
        PowerSupply.doStart(self, target)

    def doStop(self):
        PowerSupply.doStop(self)
        self._hw_wait()
        self.doEnable(False)


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
        'calibration_year': Param('Year of the last calibration', int),
        'probe_wire_length': Param('Length of probe cable in meters', float),
    }

    def doInit(self, mode):
        self._T = self._attached_temperature

    def readStd(self, value):
        value = abs(value)
        i = self._dev.GetProperties().index('range')
        _range = float(self._dev.GetProperties()[i + 1].split(' T')[0])
        temp = self._T.doRead()
        return (1e-4 * value + 6e-5 * _range +
                (1e-5 * value + (1e-6 + 3e-6 * _range)) * abs(temp - 25) +
                3e-6 * self.probe_wire_length * abs(temp - 25) +
                (datetime.now().year - self.calibration_year) * 1e-3 * value)


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
        'calibration_date': Param('Date last calibration in iso format', str),
    }

    def doInit(self, mode):
        self._T = self._attached_temperature

    def readStd(self, value):
        value = abs(value)
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
        return (value * err[0] + meas_range * err[1]) * 1e-6
