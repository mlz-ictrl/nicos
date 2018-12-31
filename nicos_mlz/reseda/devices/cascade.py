#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Class for CASCADE detector measurement and readout."""

from __future__ import absolute_import, division, print_function

from time import sleep

import numpy as np

from nicos.core import ArrayDesc, Override, Param, Value, intrange, listof, \
    oneof, tupleof
from nicos.core.data import GzipFile
from nicos.devices.datasinks.raw import SingleRawImageSink
from nicos.devices.tango import ImageChannel
from nicos.utils.fitting import curve_fit


def fit_a_sin(x, y):
    perr = 4*[float('inf')]
    if len(x) != len(y):
        return 4*[0], 4*[0], 'need equal number of x and y values!'
    if len(y) == 1:
        startpar = [y[0], 0, 1, 0]
    else:
        startpar = [sum(y)/len(y), len(y)*0.5*(max(y)-min(y))/(sum(y)+1e-6),
                    0.38, 0]
    if len(y) < 4:
        return startpar, perr, 'not enough data points for a fit, guessing'

    def model_sin(x, avg, contrast, freq, phase):
        return avg + avg * contrast * np.sin(freq * x + phase)
    try:
        popt = startpar
        popt, pcov = curve_fit(model_sin, x, y, startpar, np.sqrt(np.abs(y)))
        perr = np.sqrt(abs(np.diagonal(pcov)))
        return popt, perr, ''
    except Exception as e:
        return popt, perr, 'Error during fit: %s' % e


def fit_a_sin_fixed_freq(x, y):
    perr = 4*[float('inf')]
    if len(x) != len(y):
        return 4*[0], 4*[0], 'need equal number of x and y values!'

    freq = 2*np.pi/len(y)
    if len(y) == 1:
        startpar = [y[0], 0, 0]
    else:
        startpar = [sum(y)/len(y), len(y)*0.5*(max(y)-min(y))/(sum(y)+1e-6), 0]
    popt = [startpar[0], startpar[1], freq, startpar[2]]

    if len(y) < 4:
        return popt, perr, 'not enough data points for a fit, guessing'

    def model_sin(x, avg, contrast, phase):
        return avg + avg * contrast * np.sin(freq * x + phase)
    try:
        popt, pcov = curve_fit(model_sin, x, y, startpar, np.sqrt(np.abs(y)))
        perr = np.sqrt(abs(np.diagonal(pcov)))
        return [popt[0], popt[1], freq, popt[2]], [perr[0], perr[1], 0, perr[2]], ''
    except Exception as e:
        return popt, perr, 'Error during fit: %s' % e


class CascadeDetector(ImageChannel):
    """Detector channel for the CASCADE-MIEZE detector.

    Controls the detector via a connection to a Tango server.
    """

    parameters = {
        'mode':         Param('Data acquisition mode (tof or image)',
                              type=oneof('tof', 'image'), settable=True,
                              volatile=True),
        'roi':          Param('Region of interest, given as (x1, y1, x2, y2)',
                              type=tupleof(int, int, int, int),
                              default=(-1, -1, -1, -1), settable=True),
        'tofchannels':  Param('Number of TOF channels to use', type=int,
                              default=128, settable=True),
        'foils':        Param('Number of spaces for foils in the TOF data',
                              type=intrange(1, 32), default=8),
        'foilsorder':   Param('Usable foils, ordered by number',
                              type=listof(intrange(0, 31)), settable=False,
                              default=[7, 6, 5, 0, 1, 2]),  # XXX make it mandatory
        'fitfoil':      Param('Foil for contrast fitting', type=int, default=0,
                              settable=True),
    }

    parameter_overrides = {
        'fmtstr':   Override(default='roi %s, total %s, file %s'),
    }

    #
    # parameter handlers
    #

    def doReadMode(self):
        if self._dev.timeChannels == 1:
            return 'image'
        return 'tof'

    def doWriteMode(self, value):
        self._dev.timeChannels = self.tofchannels if value == 'tof' else 1

    def doWriteTofchannels(self, value):
        self._dev.timeChannels = value if self.mode == 'tof' else 1
        self.doUpdateMode(self.mode)

    def doUpdateMode(self, value):
        self._dataprefix = (value == 'image') and 'IMAG' or 'DATA'
        self._datashape = (value == 'image') and (128, 128) or (128, 128,
                                                                self.tofchannels)
        self._tres = (value == 'image') and 1 or self.tofchannels

    #
    # Device interface
    #

    def doPreinit(self, mode):
        ImageChannel.doPreinit(self, mode)
        #if mode != SIMULATION:
        #    self.doReset()

    def doInit(self, mode):
        # self._tres is set by doUpdateMode
        self._xres, self._yres = (128, 128)

    def doReset(self):
        oldmode = self.mode
        self._dev.Reset()
        # reset parameters in case the server forgot them
        self.log.info('re-setting to %s mode', oldmode.upper())
        self.doWriteMode(oldmode)
        self.doWritePreselection(self.preselection)

    #
    # Channel interface
    #

    def doStart(self):
        self.readresult = [0, 0]
        sleep(0.005)
        self._dev.Start()

    def doFinish(self):
        self._dev.Stop()

    def doStop(self):
        self.doFinish()

    def doPrepare(self):
        self._dev.Clear()

    def valueInfo(self):
        if self.mode == 'tof':
            return (Value(self.name + '.roi', unit='cts', type='counter',
                          errors='sqrt', fmtstr='%d'),
                    Value(self.name + '.total', unit='cts', type='counter',
                          errors='sqrt', fmtstr='%d'),
                    Value('fit.contrast', unit='', type='other',
                          errors='next', fmtstr='%.3f'),
                    Value('fit.contrastErr', unit='', type='error',
                          errors='none', fmtstr='%.3f'),
                    Value('fit.avg', unit='', type='other', errors='next',
                          fmtstr='%.1f'),
                    Value('fit.avgErr', unit='', type='error',
                          errors='none', fmtstr='%.1f'),
                    Value('roi.contrast', unit='', type='other',
                          errors='next', fmtstr='%.3f'),
                    Value('roi.contrastErr', unit='', type='error',
                          errors='none', fmtstr='%.3f'),
                    Value('roi.avg', unit='', type='other', errors='next',
                          fmtstr='%.1f'),
                    Value('roi.avgErr', unit='', type='error',
                          errors='none', fmtstr='%.1f'))
        return (Value(self.name + '.roi', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'),
                Value(self.name + '.total', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'))

    @property
    def arraydesc(self):
        if self.mode == 'image':
            return ArrayDesc('data', self._datashape, '<u4', ['X', 'Y'])
        return ArrayDesc('data', self._datashape, '<u4', ['X', 'Y', 'T'])

    def doReadArray(self, quality):
        # get current data array from detector, reshape properly
        data = self._dev.value.reshape(self._datashape)
        # determine total and roi counts
        total = data.sum()
        if self.roi != (-1, -1, -1, -1):
            x1, y1, x2, y2 = self.roi
            roi = data[..., y1:y2, x1:x2].sum()
        else:
            x1, y1, x2, y2 = 0, 0, data.shape[-1], data.shape[-2]
            roi = total

        if self.mode != 'tof':
            self.readresult = [roi, total]
            return data

        # demux timing into foil + timing
        nperfoil = self.tofchannels // self.foils
        shaped = data.reshape((self.foils, nperfoil) +  self._datashape[:2])

        x = np.arange(nperfoil)
        ty = shaped[self.fitfoil].sum((1, 2))
        ry = shaped[self.fitfoil, :, y1:y2, x1:x2].sum((1, 2))

        self.log.debug('fitting %r and %r' % (ty, ry))

        tpopt, tperr, msg = fit_a_sin_fixed_freq(x, ty)
        if msg:
            self.log.debug(msg)
        self.log.debug('total result is %r +/- %r for [avg, contrast, freq, phase]',
                       tpopt, tperr)

        rpopt, rperr, msg = fit_a_sin_fixed_freq(x, ry)
        if msg:
            self.log.debug(msg)
        self.log.debug('ROI result is %r +/- %r for [avg, contrast, freq, phase]',
                       rpopt, rperr)

        self.readresult = [
            roi, total,
            abs(tpopt[1]), tperr[1], tpopt[0], tperr[0],
            abs(rpopt[1]), rperr[1], rpopt[0], rperr[0],
        ]

        # also fit per foil data and pack everything together to be send
        # via cache for display
        payload = []
        for foil in self.foilsorder:
            foil_tot = shaped[foil].sum((1, 2))
            foil_roi = shaped[foil, :, y1:y2, x1:x2].sum((1, 2))
            tpopt, tperr, _ = fit_a_sin_fixed_freq(x, foil_tot)
            rpopt, rperr, _ = fit_a_sin_fixed_freq(x, foil_roi)
            payload.append([tpopt, tperr, foil_tot.tolist(),
                            rpopt, rperr, foil_roi.tolist()])
        self._cache.put(self.name, '_foildata', payload, flag='#')
        return data


class CascadePadSink(SingleRawImageSink):

    parameter_overrides = {
        'filenametemplate': Override(default=['%(pointcounter)08d.pad'],
                                     settable=False),
    }

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2


class CascadeTofSink(SingleRawImageSink):

    parameter_overrides = {
        'filenametemplate': Override(default=['%(pointcounter)08d.tof'],
                                     settable=False),
    }

    fileclass = GzipFile

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 3
