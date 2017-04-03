#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Special devices for recording and fitting 3He cell polarization."""

import time

import numpy as np

from nicos.core import Attach, Param, Override, Readable, Moveable, tupleof, \
    usermethod
from nicos.core.constants import SCAN, SUBSCAN
from nicos.core.data import DataSink, DataSinkHandler, PointDataset
from nicos.devices.generic.manual import ManualMove
from nicos.utils.fitting import Fit


class HePolSinkHandler(DataSinkHandler):

    def prepare(self):
        self.monitors = self.sink.monitors
        self.values = (0, 0)

    def addSubset(self, subset):
        if not isinstance(subset, PointDataset):
            return
        ix1 = -1
        ix2 = -1
        for (i, vi) in enumerate(subset.detvalueinfo):
            if vi.name == self.monitors[0]:
                ix1 = i
            elif vi.name == self.monitors[1]:
                ix2 = i
        if ix1 == -1 or ix2 == -1:
            self.log.debug('did not find both monitor columns in subset')
            return
        m1 = subset.detvaluelist[ix1]
        m2 = subset.detvaluelist[ix2]
        if m1 == 0 or m2 == 0:
            self.log.debug('one or two monitor values are zero')
            return
        self.values = (self.values[0] + m1,
                       self.values[1] + m2)
        if self.values[1] >= 20000:
            ratio = float(self.values[1]) / self.values[0]
            self.sink._attached_transmission.start(ratio)
            self.values = (0, 0)

    def end(self):
        if self.values[1] >= 5000:
            ratio = float(self.values[1]) / self.values[0]
            self.sink._attached_transmission.start(ratio)


class HePolSink(DataSink):
    """For every scan, records the mon2/mon1 ratio in the transmission device.
    """

    attached_devices = {
        'transmission': Attach('Transmission device', Moveable),
    }

    parameters = {
        'monitors':     Param('Names of the two monitor devices to calculate '
                              'the transmission ratio', type=tupleof(str, str),
                              mandatory=True),
    }

    parameter_overrides = {
        'settypes':     Override(default=set((SCAN, SUBSCAN)))
    }

    handlerclass = HePolSinkHandler


class Transmission(ManualMove):
    pass


class BeamPolarization(Readable):

    attached_devices = {
        'transmission': Attach('Transmission device', Readable),
        'wavelength':   Attach('Wavelength device', Readable),
    }

    parameters = {
        'starttime':      Param('The time when the current cell was installed',
                                type=float, settable=True),
        'transmission':   Param('Monitor transmission ratio without cell',
                                type=float, settable=True),
        'hepressure':     Param('The He gas pressure in the current cell',
                                type=float, settable=True, unit='bar'),
        'celllength':     Param('The length of the current cell',
                                type=float, settable=True, unit='cm'),
        'celltrans':      Param('The transmission of the empty cell',
                                type=float, settable=True),
        'relaxationtime': Param('The calculated relaxation time of the cell',
                                type=float, settable=False, unit='h'),
    }

    parameter_overrides = {
        'pollinterval': Override(default=600),
        'maxage':       Override(default=700),
        'unit':         Override(mandatory=False, default='%'),
    }

    @usermethod
    def newCell(self, m1, m2, pressure, length=13.0, T0=0.88):
        """Re-set data associated with the current cell."""
        self.starttime = time.time()
        self.transmission = float(m2) / float(m1)
        self.hepressure = pressure
        self.celllength = length
        self.celltrans = T0

    def doRead(self, maxage=None):
        O = 0.0732 * self._attached_wavelength.read() * \
            self.celllength * self.hepressure

        def model(t, T1, PHe0):
            # see Hutanu et al., J. Phys. Conf. Ser. 294, 012012
            # O:    opacity (0.0732 * lambda/A * length/cm * pressure/bar)
            # T1:   relaxation time in hours
            # PHe0: helium polarization at cell installation time
            PHe = PHe0 * np.exp(-(t - self.starttime)/(T1 * 3600.))
            return self.transmission * self.celltrans * np.exp(-O) * np.cosh(O * PHe)

        fit = Fit('polarization', model, ['T1', 'PHe0'], [100.0, 0.7])
        xs, ys = [], []
        # fit max. one day of data
        fromtime = max(self.starttime, time.time() - 86400)
        for t, v in self._attached_transmission.history(fromtime=fromtime):
            xs.append(t)
            ys.append(v)
        res = fit.run(xs, ys, None)
        self.log.debug(str(res))
        if res._failed:
            return 0.0
        totaltime = time.time() - self.starttime
        self._setROParam('relaxationtime', res.T1)
        # calculate He polarization at the current time
        PHe = res.PHe0 * np.exp(-totaltime/(res.T1 * 3600.))
        # calculate beam polarization (in percent)
        return abs(100 * np.tanh(O * PHe))
