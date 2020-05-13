#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""Integration of Dynamic Light Scattering setup."""

from __future__ import absolute_import, division, print_function

import time

import numpy as np

from nicos.core import ArrayDesc, Attach, Measurable, Moveable, Override, \
    Param, Readable, dictof, oneof, tupleof
from nicos.core.constants import FINAL, INTERMEDIATE, POINT
from nicos.core.data import DataSinkHandler
from nicos.core.status import BUSY, OK
from nicos.devices.datasinks import FileSink
from nicos.devices.tango import BaseImageChannel

MODES = ['cross_auto1', 'cross_auto2', 'auto1_auto2', 'cross_cross']


class DLSCard(BaseImageChannel):
    attached_devices = {
        'wheels': Attach('The filter wheel positions', Readable,
                         multiple=True, optional=True),
    }

    parameters = {
        'angles': Param('Scattering angles of the detector',
                        type=tupleof(float, float), mandatory=True,
                        settable=True),
        'mode':   Param('Measure mode', type=oneof(*MODES),
                        default='cross_cross', settable=True),
    }

    def _get_filters(self):
        return ' '.join('%d' % wh.read() for wh in self._attached_wheels)

    def setMode(self):
        self._dev.readoutMode = self.mode

    def readAbscissa(self):
        return self._dev.abscissa

    def readIntensity(self):
        data = self._dev.intensity
        return data.reshape((len(data) // 3, 3))

    abscissa_arraydesc = ArrayDesc('data', shape=(264,), dtype='<f8')
    intensity_arraydesc = ArrayDesc('data', shape=(100, 3), dtype='<f8')


class DLSDetector(Measurable):
    attached_devices = {
        'cards':    Attach('DLS cards', DLSCard, multiple=True),
        'shutter':  Attach('Shutter to open before measuring', Moveable),
        'limiters': Attach('The filter wheel adjusters', Moveable, multiple=True),
        'lasersel': Attach('The laser wavelength selector', Readable, optional=True),
    }

    parameters = {
        'duration':  Param('Duration of a single DLS measurement.', default=10,
                           unit='s', settable=True),
        'intensity': Param('Intensity to aim for when adjusting filter wheels.',
                           default=100, unit='kHz', settable=True),
        'wavelengthmap': Param('Laser wavelength depending on selector',
                               unit='nm', type=dictof(str, float)),
        # these should be sample properties instead...
        'viscosity': Param('Sample viscosity', unit='cp', settable=True),
        'refrindex': Param('Sample refractive index', settable=True),
    }

    def doInit(self, mode):
        self._adjusting = -1
        self._measuring = False
        self._nfinished = 1
        self._nstarted = 1
        self._ntotal = 1

    def _get_wavelength(self):
        if self._attached_lasersel:
            return self.wavelengthmap.get(
                self._attached_lasersel.read(), -1)
        else:
            return self.wavelengthmap.get('', -1)

    def doRead(self, maxage=0):
        return []

    def valueInfo(self):
        return ()

    def doReadArrays(self, quality):
        result = []
        for card in self._attached_cards:
            result.append(card.readArray(quality))
            result.append(card.readAbscissa())
            result.append(card.readIntensity())
        return result

    def arrayInfo(self):
        result = []
        for card in self._attached_cards:
            result.append(card.arraydesc)
            result.append(card.abscissa_arraydesc)
            result.append(card.intensity_arraydesc)
        return result

    def doStatus(self, maxage=0):
        return BUSY if self._measuring else OK, \
            '%d of %d done' % (self._nfinished, self._ntotal)

    def doSetPreset(self, **preset):
        if 't' in preset:
            self._ntotal = int(preset['t'] / self.duration) or 1

    def presetInfo(self):
        return ('t',)

    def doStart(self):
        self._attached_shutter.start(1)
        self._adjusting = 0
        self._nfinished = 0
        self._nstarted = 0
        self._measuring = True
        self._attached_limiters[0].start(self.intensity)

    def doFinish(self):
        self.doStop()

    def doStop(self):
        self._measuring = False
        for card in self._attached_cards:
            try:
                card.stop()
            except Exception:
                pass
        self._attached_shutter.start(0)
        for limiter in self._attached_limiters:
            limiter.maw(0)   # close wheels

    def duringMeasureHook(self, elapsed):
        retval = None
        if self._adjusting > -1:
            adj_lim = self._attached_limiters[self._adjusting]
            if adj_lim.status(0)[0] == BUSY:
                return
            self.log.info('reached %s adjustment: %.1f kHz', adj_lim,
                          adj_lim.read(0))
            if self._adjusting == len(self._attached_limiters) - 1:
                self._adjusting = -1
            else:
                self._adjusting += 1
                self._attached_limiters[self._adjusting].start(self.intensity)
                return
        # start new measurements when needed
        if all(c.status(0)[0] != BUSY for c in self._attached_cards):
            if self._nstarted > self._nfinished:
                # read out now, start new measurement next time
                retval = INTERMEDIATE
                self._nfinished += 1
            elif self._nfinished < self._ntotal:
                self.log.info('starting new DLS measurement')
                for card in self._attached_cards:
                    card.setMode()
                    card.preselection = self.duration
                    card.start()
                self._nstarted += 1
            else:
                self._measuring = False
        return retval


FILETEMPLATE = '''\
FPGA-CORRELATOR
Date :	"%(date)s"
Time :	"%(time)s"
Samplename : 	"%(sample)s"
SampMemo(0) : 	""
SampMemo(1) : 	""
SampMemo(2) : 	""
SampMemo(3) : 	""
SampMemo(4) : 	""
SampMemo(5) : 	""
SampMemo(6) : 	""
SampMemo(7) : 	""
SampMemo(8) : 	""
SampMemo(9) : 	""
Temperature [K] :	%(temperature)14.5f
Viscosity [cp]  :	%(viscosity)14.5f
Refractive Index:	%(refrindex)14.5f
Wavelength [nm] :	%(wavelength)14.5f
Angle [°]       :	%(angle1)14.5f
Angle2 [°]      :	%(angle2)14.5f
Filters         :       %(filters)14s
Duration [s]    :	%(duration)14d
FloatDur [ms]   :	%(floatdur)14d
Stop TP [ms]    :	  16777216
Runs            :	         1
Mode            :	"%(modes)s"
MeanCR0 [kHz]   :	%(mean0)14.5f
MeanCR1 [kHz]   :	%(mean1)14.5f
MeanCR2 [kHz]   :	%(mean2)14.5f
MeanCR3 [kHz]   :	%(mean3)14.5f

"Correlation"
'''


class DLSFileSinkHandler(DataSinkHandler):
    def _write(self, arrays):
        self._counter += 1
        for (i, card) in enumerate(self.detector._attached_cards):
            correlation = np.stack([arrays[3*i+1],
                                    arrays[3*i][:,0],
                                    arrays[3*i][:,1]], 1)
            correlation[np.isinf(correlation)] = 0.
            intensity = arrays[3*i+2]

            tmpldict = dict(
                date = time.strftime('%m.%d.%Y'),
                time = time.strftime('%H:%M:%S'),
                sample = self._meta.get(('Sample', 'samplename'),
                                        ('unknown',))[0],
                temperature = self._meta.get(('Ts', 'value'), (-1,))[0],
                viscosity = self.detector.viscosity,
                refrindex = self.detector.refrindex,
                wavelength = self.detector._get_wavelength(),
                angle1 = card.angles[0],
                angle2 = card.angles[1],
                filters = card._get_filters(),
                duration = int(self.detector.duration),
                floatdur = int(self.detector.duration * 1000),
                modes = card.mode,
                mean0 = np.mean(intensity[1:, 1]),
                mean1 = np.mean(intensity[1:, 2]),
                mean2 = 0,
                mean3 = 0,
            )

            fd = self.manager.createDataFile(
                self.dataset,
                self.sink.filenametemplate,
                self.sink.subdir,
                additionalinfo={'dlscounter': self._counter, 'dlscard': i+1})
            fd.write(FILETEMPLATE % tmpldict)
            np.savetxt(fd, correlation, '%14.5e')
            fd.write('\n"Count Rate"\n')
            np.savetxt(fd, intensity, '%14.5f')
            fd.close()

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        self._counter = 0

    def putMetainfo(self, metainfo):
        self._meta = metainfo

    def putResults(self, quality, results):
        if quality not in (INTERMEDIATE, FINAL):
            return
        if self.detector.name in results:
            result = results[self.detector.name]
            if result is None:
                return
            self._write(result[1])


class DLSFileSink(FileSink):
    handlerclass = DLSFileSinkHandler

    parameter_overrides = {
        'settypes':         Override(default=[POINT]),
        'subdir':           Override(default='dls'),
        'filenametemplate': Override(mandatory=False, userparam=False,
                                     default=['dls_%(pointcounter)d_'
                                              '%(dlscounter)03d_card%(dlscard)d.asc']),
    }
