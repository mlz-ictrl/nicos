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
#   Alexander Book <alexander.book@frm2.tum.de>
#
# *****************************************************************************

""" Moving Detector: Measures a 2Theta range and then moves to the next range
    to yield a complete 2Theta diffractogram.
"""

import math

import numpy as np
from numpy import arctan, rad2deg as deg

from nicos import session
from nicos.core import Attach, Moveable, Override, Param, none_or, oneof, \
    status
from nicos.core.constants import FINAL, LIVE, SIMULATION
from nicos.core.utils import waitForCompletion
from nicos.devices.generic.detector import Detector as GenericDetector
from nicos.devices.generic.sequence import MeasureSequencer, SeqCall, SeqDev, \
    SeqWait


class MovingDetector(MeasureSequencer):

    MODE_SCANNING = 'scanning'
    MODE_STEPPING = 'stepping'

    attached_devices = {
        'motor': Attach('Axis to move the detector', Moveable),
        'detector': Attach('Standard detector device', GenericDetector),
    }

    parameters = {
        'liveinterval': Param('Interval to read out live images (None to '
                              'disable live readout)',
                              type=none_or(float), unit='s', settable=True,
                              default=0.5,
                              ),
        'mode': Param('Scanning mode',
                      type=oneof(MODE_STEPPING, MODE_SCANNING),
                      unit='', settable=True, default=MODE_STEPPING),
        'cps': Param('Return counts as counts per second',
                     type=bool, unit='', settable=True, default=False),
        # 'overlapp': Param('Pixel overlapp of two consecutive measurements',
        #                   type=int, settable=True,
        #                   default=5, category='instrument',
        #                   ),
    }

    parameter_overrides = {
        'fmtstr': Override(volatile=True),
    }

    _ttheta_start = None
    _ttheta_end = None
    _tthetas = []
    _step = 0
    _ttheta_skip = 1
    _ttheta_resol = 1
    _ttheta = []
    _bins = []
    _cps = []
    _counts = []

    def doInit(self, mode):
        self._data = [0] * len(self._attached_detector.valueInfo())
        self._array_data = np.zeros((2, self._pixel_count()), dtype='<u4',
                                    order='F')

    def _detector_mapping(self):
        px_count = self._pixel_count()
        return (np.arange(-px_count / 2, px_count / 2, 1)
                ) * self._detector_resolution()

    def _detector_resolution(self):
        px_size = self._pixel_size()
        radius = self._ttheta_radius()
        return 2 * deg(arctan(px_size / 2 / radius))

    def doInfo(self):
        return self._attached_detector.info()

    def doPrepare(self):
        MeasureSequencer.doPrepare(self)
        self._attached_detector.prepare()

    def _pixel_size(self):
        return self._attached_detector._attached_images[0].pixel_size
        # return self.pixel_size

    def _pixel_count(self):
        return self._attached_detector._attached_images[0].pixel_count
        # return self.pixel_count

    def _ttheta_radius(self):
        return self._attached_detector._attached_images[0].radius
        # return self.detector_radius

    def doStart(self):
        px_count = self._pixel_count()
        px_size = self._pixel_size()
        radius = self._ttheta_radius()
        d2Theta = self._detector_resolution()
        det_range = 2 * deg(arctan(px_count * px_size / 2 / radius))

        if self.mode == self.MODE_STEPPING:

            if self._ttheta_start is None or self._ttheta_end is None:
                self._tthetas = [self._attached_motor.read()]
            else:
                if self._ttheta_start >= self._ttheta_end:
                    self._ttheta_start, self._ttheta_end = self._ttheta_end, \
                        self._ttheta_start

                steps = math.ceil(
                    (self._ttheta_end - self._ttheta_start) / det_range)
                measurement_range = steps * det_range
                center = 0.5 * (self._ttheta_start + self._ttheta_end)
                start = 0.5 * (2 * center - measurement_range)

                self._tthetas = [
                    start + det_range * (n + 0.5) for n in range(0, steps)]

            self._array_data = np.zeros((2, px_count * len(self._tthetas)))
            self._array_data.fill(0)
            self._array_data[0] = np.hstack(
                [ttheta + self._detector_mapping() for ttheta in self._tthetas])

        elif self.mode == self.MODE_SCANNING:

            # making finer 2Theta step increments
            resol = self._ttheta_resol
            # skipping some 2Theta points to accelerate the measurement
            incr = self._ttheta_skip

            # the ttheta values we want to measure
            self._ttheta = np.arange(self._ttheta_start, self._ttheta_end,
                                     d2Theta / resol)

            # the binning of the ttheta data, to be used with np.digitize, the
            # bin is constructed such that the bins are equally spaced around
            # every ttheta value
            self._bins = self._ttheta - d2Theta / 2 / resol
            # add an element to the end to keep the binning correct, i.e. every
            # ttheta value is surrounded by an element from self._bins from the
            # left and right, i.e.
            # self._bins[i] <= self._ttheta[i] < self._bins[i+1]
            self._bins = np.append(self._bins,
                                   [self._ttheta[-1] + (d2Theta / 2 / resol)])

            # Every pixel of the detector needs to measure every ttheta, thus
            # the right most pixel in the detector
            # forces us to start the measurement by half the detector size in
            # advance in order for the right mose pixel to cover the left most
            # ttheta.
            # Notice here the +1 in -px_count * resol / 2 + 1 which skips the
            # very first ttheta value
            # as it will be discarded anyway (lies outside the ttheta range
            # we have to measure)
            append_start = np.arange(-px_count * resol / 2 + 1, 0, 1
                                     ) * d2Theta / resol + self._ttheta[0]
            # Same argument, but with the left most pixel and the highest
            # ttheta value
            append_end = (np.arange(0, px_count * resol / 2, 1) + 1
                          ) * d2Theta / resol + self._ttheta[-1]

            self._tthetas = np.hstack((append_start, self._ttheta, append_end))

            # Skip some ttheta values, but only the ones such that every ttheta
            # value has the same measurement time
            if resol > 1 and incr > 1:
                # we don't want to get every n-th element now, but rather
                # n elements in a row, then skip the next i*n elements, then
                # get n elements, then skip etc..
                # where n is the fineness, and i the increment
                # e.g. tthetas = tthetas[::X] wont work here
                inds = [i for i in range(len(self._tthetas))
                        if (i // resol) % incr == 0]
                self._tthetas = self._tthetas[inds]
            else:
                # just take every n-th element
                self._tthetas = self._tthetas[::incr]

            # counts contains one more item (and two more than ttheta), as
            # the first and last bin contain the unused measurement data
            # i.e. (ttheta < bin[0] and ttheta > bin[-1], resp.)
            self._counts = np.zeros(len(self._bins) + 1, dtype='<u4', order='F')
            # contains the measurement time for each bin. the central element
            # should have all the same measurement time
            self._cps = np.zeros(len(self._bins) + 1, dtype='<u4', order='F')

        session.experiment.data.updateMetainfo()

        self._last_live = 0
        self._step = 0
        self._data = [0] * len(self._attached_detector.valueInfo())
        MeasureSequencer.doStart(self)

    def doSetPreset(self, **preset):
        self._ttheta_start = None
        self._ttheta_end = None
        self._ttheta_skip = 1
        self._ttheta_resol = 1
        if preset:
            if 'ttheta_start' in preset:
                self._ttheta_start = float(preset.pop('ttheta_start'))
            if 'ttheta_end' in preset:
                self._ttheta_end = float(preset.pop('ttheta_end'))
            if 'ttheta_skip' in preset:
                self._ttheta_skip = int(preset.pop('ttheta_skip'))
            if 'ttheta_resolution' in preset:
                self._ttheta_resol = int(preset.pop('ttheta_resolution'))
        self._attached_detector.setPreset(**preset)

    def _read_value(self):
        ret = self._attached_detector.read()
        self._data = [sum(x) for x in zip(self._data, ret)]
        self._det_run = False

        if self._mode == SIMULATION:
            return

        if self.mode == self.MODE_STEPPING:
            px_count = self._pixel_count()
            counts = self._attached_detector.readArrays(
                FINAL)[0].astype('f8')[1]

            self._array_data[
                1, px_count * self._step: px_count * (self._step + 1)] = counts

        elif self.mode == self.MODE_SCANNING:
            counts = self._attached_detector.readArrays(
                FINAL)[0].astype('<u4')[1]

            inds = np.digitize(
                self._detector_mapping() + self._tthetas[self._step],
                self._bins)

            # Attention here: This just works because there is no mixing up of
            # multiple indices:
            # If two measurement points belong to the same bin, the first count
            # will be discarded!
            # Note that the start and endpoint (which are discarded anyway) are
            # not correctly counted, as np.digitize will throw all points below
            # ttheta_start into the same bin (and vice versa with ttheta_end)
            #
            # If this is a problem, use
            # for i, j in enumerate(inds):
            #    self._counts[j] += counts[i]
            #    self._cps[j] += 1
            #
            self._counts[inds] += counts
            self._cps[inds] += 1

    def _incStep(self):
        self._step += 1

    def _startDet(self):
        """Start the detector and mark it running.

        Since the detector is not really in BUSY mode after start, we need an
        additional flag to mark the detector started.
        """
        self._attached_detector.prepare()
        waitForCompletion(self._attached_detector)
        self._attached_detector.start()
        self._det_run = True

    def doReadArrays(self, quality):
        if self.mode == self.MODE_STEPPING:
            return [self._array_data]

        if self.mode == self.MODE_SCANNING:
            counts = self._counts[1:-1]
            if self.cps:
                output = np.zeros(counts.shape, dtype=float)
                np.divide(counts, self._cps[1:-1], out=output,
                          where=self._cps[1:-1] > 0)
                counts = output
            return [np.array([self._ttheta, counts])]

    def _generateSequence(self):
        seq = []

        for ttheta in self._tthetas:
            seq.append(SeqDev(self._attached_motor, ttheta, stoppable=True))
            seq.append(SeqCall(self._startDet))
            seq.append(SeqWait(self._attached_detector))
            seq.append(SeqCall(self._read_value))
            seq.append(SeqCall(self._incStep))

        seq.append(SeqDev(self._attached_motor, self._tthetas[0],
                   stoppable=True))
        return seq

    def doRead(self, maxage=0):
        return self._data

    def doReset(self):
        self._det_run = False
        self._last_live = 0
        self._step = 0
        self._array_data.fill(0)
        self._attached_detector.reset()
        self._data = [0] * len(self._attached_detector.valueInfo())
        MeasureSequencer.doReset(self)
        # self._attached_motor.maw(self._startpos)

    def doPause(self):
        self._attached_detector.pause()

    def doResume(self):
        self._attached_detector.resume()

    def doFinish(self):
        self._attached_detector.finish()

    def doSimulate(self, preset):
        return self._attached_detector.doSimulate(preset)

    def _fmtstr(self, value):
        return 'step = %d' % value

    def doReadFmtstr(self):
        return self._fmtstr(self._step)

    def doEstimateTime(self, elapsed):
        return 1

    def valueInfo(self):
        return self._attached_detector.valueInfo()

    def arrayInfo(self):
        return self._attached_detector.arrayInfo()

    def presetInfo(self):
        return {'ttheta_start', 'ttheta_end', 'ttheta_skip',
                'ttheta_resolution'} | self._attached_detector.presetInfo()

    def duringMeasureHook(self, elapsed):
        if self.liveinterval is not None:
            if self._last_live + self.liveinterval < elapsed:
                self._last_live = elapsed
                return LIVE
        return None

    def _stopAction(self, nr):
        self.log.debug('_stopAction at step: %d', nr)
        self._attached_detector.stop()

    def _cleanUp(self):
        if self._seq_was_stopped:
            self._seq_was_stopped = False
            self._set_seq_status(status.OK, 'idle')
