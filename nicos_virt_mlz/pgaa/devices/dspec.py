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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""Classes to simulate the DSPec detector."""

import numpy as np
from numpy.random import random
from scipy import interpolate

from nicos.core import ArrayDesc, Override, Param, Value, intrange, \
    nonemptylistof, oneof, tupleof
from nicos.devices.generic.detector import GatedDetector
from nicos.devices.generic.virtual import VirtualImage, VirtualTimer


class DSPecTimer(VirtualTimer):

    parameters = {
        'type': Param('Type of time, "livetime" or "truetime"',
                      type=oneof('livetime', 'truetime'),
                      ),
    }

    def valueInfo(self):
        return (Value(self.type[:-1], type='time', fmtstr='%.3f', unit='s'),)


class DSPecSpectrum(VirtualImage):

    parameters = {
        'prefix': Param('prefix for filesaving',
                        type=str, settable=False, mandatory=True,
                        category='general'),
        'ecalslope': Param('Energy Calibration Slope',
                           type=float, mandatory=False, settable=True,
                           default=0.178138, category='general'),
        'ecalintercept': Param('Energy Calibration Intercept',
                               type=float, mandatory=False, settable=True,
                               default=0.563822, category='general'),
    }

    parameter_overrides = {
        'size': Override(type=tupleof(intrange(1, 65535), intrange(1, 1)),
                         default=(16384, 1)),
    }

    def doInit(self, mode):
        self.arraydesc = ArrayDesc(self.name, self.size, '<u4')

    def doReadArray(self, _quality):
        if self._buf is not None:
            return self._buf.reshape(self.size[0])
        return self._buf

    def arrayInfo(self):
        return (self.arraydesc, )

    def valueInfo(self):
        return (Value('DSPec', type='counter', fmtstr='%d', errors='sqrt',
                      unit='cts'),)

    def doPrepare(self):
        self._x = np.linspace(10, 170, self.size[0])
        self._xmax = self._x.max()
        self._xmin = self._x.min()
        VirtualImage.doPrepare(self)

    def _generate(self, t):

        def f(x):
            """Ideal function that we sample from in this example.

            It's making an analytical function up for a virtual instrument.

            This function would just read a certain file that contains the
            expected measured curve for a certain sample.
            """
            y = np.zeros_like(x)
            # in this particular example, we use a diffraction pattern
            wl = 3.  # wavelength in AA to calculate scattering angles from Q
            # [Q in AA-1, relative intensity (normalized to the highest peak)]
            peaklist = [
                [1.229, 4.383],
                [1.389, 3.324],
                [1.762, 0.809],
                [2.148, 100.0],
                [2.225, 0.709],
                [2.458, 5.557],
                [2.492, 12.25],
                [2.778, 0.490],
                [2.853, 0.275],
                [2.853, 0.866],
                [3.024, 2.380],
                [3.315, 0.406],
                [3.340, 0.744],
                [3.340, 0.720],
                [3.500, 23.41],
                [3.524, 13.02],
            ]
            # does not need to be normalized
            for Q, I in peaklist:
                tth = 2 * np.arcsin(Q * wl / (4. * np.pi)) * 180. / np.pi
                y += I * np.exp(-(x - tth) ** 2)
            # add some background
            y += 10 * np.exp(-(x / 100)**2)
            return y

        def sample(g):
            """Sampling the ideal curve with counts."""
            x = np.linspace(10, 170, self.size[0])
            y = g(x)              # probability density function, pdf
            cdf_y = np.cumsum(y)  # cumulative distribution function, cdf
            cdf_y /= cdf_y.max()  # takes care of normalizing cdf to 1.0
            inverse_cdf = interpolate.interp1d(
                cdf_y, x, bounds_error=False, fill_value='extrapolate')
            return inverse_cdf

        def return_samples(N=1e6):
            """Return random events distributed according to the PDF.

            so that their histogram looks like the target data.

            If called with a low number of samples, one gets a noisy dataset
            If called with a high number of samples, the returned dataset gets
            smoother and smoother in order to give people the impression of an
            ongoing measurement, one would call this function many times with
            a small number of samples each and sum the results up in a
            histogram generate some samples according to the chosen pdf, f(x)
            """
            return sample(f)(random(int(N)))

        numbins = self.size[0]
        # each "measurement" contains 1000 neutrons
        if t == 0:
            return np.histogram(return_samples(1e3), bins=numbins,
                                range=(self._xmin, self._xmax)
                                )[0].reshape(self.size)
        counts, _bins = np.histogram(
            return_samples(1e3), bins=numbins, range=(self._xmin, self._xmax))
        return counts.reshape(self.size)

        # this is the sum of all the neutrons that have been counted so far
        # new_y = self._buf.tolist() + counts
        # self.log.info('new_y: %d', len(new_y))
        # y_repeated = np.concatenate(
        #     ([new_y[0]], np.repeat(new_y, 2), [new_y[-1]]))
        # return y_repeated.reshape(self.size)


class DSPec(GatedDetector):

    parameters = {
        'size': Param('Full detector size', type=nonemptylistof(int),
                      settable=False, mandatory=False, default=(16384, 1),
                      category='instrument'),
        'roioffset': Param('ROI offset', type=nonemptylistof(int),
                           mandatory=False, settable=True),
        'roisize': Param('ROI size', type=nonemptylistof(int),
                         mandatory=False, settable=True),
        'binning': Param('Binning', type=nonemptylistof(int),
                         mandatory=False, settable=True, default=(1,)),
        'zeropoint': Param('Zero point', type=nonemptylistof(int),
                           settable=False, mandatory=False, default=[0, 0]),
        'prefix': Param('prefix for filesaving',
                        type=str, settable=False, mandatory=True,
                        category='general'),
        'ecalslope': Param('Energy calibration slope',
                           type=float, mandatory=False, settable=True,
                           default=1, category='general'),
        'ecalintercept': Param('Energy calibration interception',
                               type=float, mandatory=False, settable=True,
                               default=0, category='general'),
        'poll': Param('Polling time of the TANGO device driver',
                      type=float, settable=False),
        'cacheinterval': Param('Interval to cache intermediate spectra',
                               type=float, unit='s', settable=True,
                               default=1800),
    }

    parameter_overrides = {
        'enablevalues': Override(settable=True, category='general'),
    }

    def _presetiter(self):
        for k in ('info', 'Filename'):
            yield k, None, 'other'
        for dev in self._attached_timers:
            if dev.name == 'truetim':
                yield 'TrueTime', dev, 'time'
            elif dev.name == 'livetim':
                yield 'LiveTime', dev, 'time'
            elif dev.name == 'clocktim':
                yield 'ClockTime', dev, 'time'
        for dev in self._attached_images:
            yield 'counts', dev, 'counts'

    def presetInfo(self):
        pinfo = {'info', 'Filename'}
        for dev in self._attached_timers:
            if dev.name == 'truetim':
                pinfo = pinfo.union({'TrueTime'})
            elif dev.name == 'livetim':
                pinfo = pinfo.union({'LiveTime'})
            elif dev.name == 'clocktim':
                pinfo = pinfo.union({'ClockTime'})
        if self._attached_images:
            pinfo = pinfo.union({'counts'})
        return pinfo
