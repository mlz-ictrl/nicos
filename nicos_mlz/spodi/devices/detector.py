#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""SPODI detector."""

import numpy as np

from nicos import session
from nicos.core import ArrayDesc, Attach, Moveable, Override, Param, Value, \
    listof, none_or, oneof, status
from nicos.core.constants import FINAL, LIVE, SIMULATION
from nicos.devices.generic.detector import Detector as GenericDetector
from nicos.devices.generic.sequence import MeasureSequencer, SeqCall, SeqDev, \
    SeqWait


class Detector(MeasureSequencer):
    """SPODI specific detector.

    The detector moves around an axis (2theta) in a number of steps
    (`resosteps`) over a range of 2 degrees (given in `range`). The starting
    position is current position + (`resosteps` - 1) * `range` / `resosteps`.

    The detector data (image) will be stored in an accumulated image array:

        The first colums of each step will be stored in a sequence, the second
        colums will follow, and so on.

        At the end the image will be a refined picture of a single histogram.
    """

    attached_devices = {
        'motor': Attach('Axis to perform the reso(lution) steps', Moveable),
        'detector': Attach('Standard detector device', GenericDetector),
    }

    parameters = {
        'resosteps': Param('Number of steps performed by the motor to '
                           'accumulate a single spectrum',
                           type=oneof(1, 2, 4, 5, 8, 10, 20, 25, 40, 50, 80,
                                      100),
                           default=40, settable=True, userparam=True,
                           category='general',
                           ),
        'range': Param('Fullrange for the resosteps',
                       type=float, settable=False,
                       default=2.0, category='instrument',
                       ),
        'numinputs': Param('Number of detector channels',
                           type=int,
                           default=80, settable=False,
                           category='general',
                           ),
        '_startpos': Param('Store the starting position',
                           type=float, settable=True, mandatory=False,
                           userparam=False, category='instrument',
                           ),
        'liveinterval': Param('Interval to read out live images (None to '
                              'disable live readout)',
                              type=none_or(float), unit='s', settable=True,
                              default=0.5,
                              ),
        'rates': Param('The rates detected by the detector',
                       settable=False, type=listof(float),
                       userparam=False, category='status',
                       ),
    }

    parameter_overrides = {
        'fmtstr': Override(volatile=True),
    }

    _last_live = 0
    _step = 0
    _time_preset = 0
    _mon_preset = 0
    _arraydesc = None
    _det_run = False

    def doInit(self, mode):
        self._data = [0] * len(self._attached_detector.valueInfo())
        self._set_resosteps(self.resosteps)

    def doInfo(self):
        ret = self._attached_detector.doInfo()
        return ret

    def doPrepare(self):
        self._attached_detector.doPrepare()

    def doStart(self):
        self._startpos = self._attached_motor.read() + \
            (self.resosteps - 1) * self._step_size
        self.log.debug('det._startpos: %r', self._startpos)
        self._setROParam('rates', [0., 0., 0.])
        session.data.updateMetainfo()

        self._last_live = 0
        self._step = 0
        self._array_data.fill(0)
        self._data = [0] * len(self._attached_detector.valueInfo())
        MeasureSequencer.doStart(self)

    def doSetPreset(self, **preset):
        if preset:
            self._time_preset = preset['t'] if 't' in preset else 0
            self._mon_preset = preset['mon1'] if 'mon1' in preset else \
                preset['mon2'] if 'mon2' in preset else 0
            if 'resosteps' in preset:
                self.resosteps = int(preset['resosteps'])
                preset.pop('resosteps')
        self._attached_detector.doSetPreset(**preset)

    def _read_value(self):
        ret = self._attached_detector.read()
        self._data = [sum(x) for x in zip(self._data, ret)]
        # Detector is not busy anymore, but to early to consider it as
        # 'not busy'
        self._det_run = False
        imgret = self._attached_detector.readArrays(FINAL)[0].astype('<u4',
                                                                     order='F')
        # self.log.info('%r', imgret)
        if self._mode != SIMULATION:
            self._array_data[self._step::self.resosteps] = imgret

    def _incStep(self):
        if self._step < self.resosteps - 1:
            self._step += 1

    def _startDet(self):
        """Start the detector and mark it running.

        Since the detector is not really in BUSY mode after start, we need an
        additional flag to mark the detector started.
        """
        self._attached_detector.start()
        self._det_run = True

    def doReadArrays(self, quality):
        self.log.debug('doReadArrays: %d/%d: %d, %r',
                       self._step, self.resosteps, self._array_data.sum(),
                       self._array_data.shape)
        if quality == LIVE:
            imgret = self._attached_detector.readArrays(FINAL)[0].astype(
                '<u4', order='F')
            self._array_data[self._step::self.resosteps] = imgret
        return [self._array_data]

    def _generateSequence(self, *args, **kwargs):
        seq = []
        for step in range(self.resosteps):
            pos = self._startpos - step * self._step_size
            seq.append(SeqDev(self._attached_motor, pos, stoppable=True))
            seq.append(SeqCall(self._startDet))
            seq.append(SeqWait(self._attached_detector))
            seq.append(SeqCall(self._read_value))
            seq.append(SeqCall(self._incStep))
        return seq

    def doRead(self, maxage=0):
        if self._step < self.resosteps:
            if self._attached_detector.status(0)[0] == status.BUSY \
               or self._det_run:
                ret = [self._step + 1] + \
                    [sum(x) for x in
                     zip(self._data, self._attached_detector.doRead(maxage))]
            else:
                if self._step == 1 and \
                   MeasureSequencer.status(self, 0)[0] != status.BUSY:
                    ret = [self._step] + self._data
                else:
                    ret = [self._step + 1] + self._data
        else:
            ret = [self._step] + self._data
        # ret = [step, meastime, mon1, mon2, counts]
        meastime = ret[1]
        if meastime > 0.:
            ctrrate = ret[-1] / meastime
            mon1rate = ret[2] / meastime
            mon2rate = 0
            if len(self._attached_detector._attached_monitors) > 1:
                mon2rate = ret[-2] / meastime
            self._setROParam('rates', [mon1rate, mon2rate, ctrrate])
        return ret

    def doReset(self):
        self._det_run = False
        self._last_live = 0
        self._step = 0
        self._array_data.fill(0)
        self._attached_detector.doReset()
        self._data = [0] * len(self._attached_detector.valueInfo())
        MeasureSequencer.doReset(self)
        # self._attached_motor.maw(self._startpos)

    def doPause(self):
        self._attached_detector.doPause()

    def doResume(self):
        self._attached_detector.doResume()

    def doFinish(self):
        self._attached_detector.doFinish()

    def doSimulate(self, preset):
        return [self.resosteps] + self._attached_detector.doSimulate(preset)

    def _set_resosteps(self, value):
        shape = (value * self.numinputs, 256)
        self._step_size = self.range / value
        if not self._arraydesc:
            self._arraydesc = ArrayDesc('data', shape=shape, dtype='<u4')
            self._array_data = np.zeros(shape, dtype='<u4', order='F')
        else:
            self._arraydesc.shape = shape
            self._array_data = np.resize(self._array_data,
                                         shape).astype('<u4', order='F')
            self._array_data.fill(0)
        if self._mode != SIMULATION:
            self._cache.put(self, 'fmtstr', self._fmtstr(value))
        self.log.debug('%r', self._arraydesc)
        self.log.debug('stepsize: %f', self._step_size)

    def doWriteResosteps(self, value):
        self._set_resosteps(value)

    def _fmtstr(self, value):
        return 'step = %d' + '/%d, ' % value + \
            self._attached_detector.doReadFmtstr()

    def doReadFmtstr(self):
        return self._fmtstr(self.resosteps)

    def doEstimateTime(self, elapsed):
        # TODO calculate the estimated time better in case of monitor counting
        # the _time_preset value is only value for time counting mode
        mspeed = self._attached_motor.speed or 1.0
        steptime = (self.range / mspeed) / self.resosteps
        if MeasureSequencer.status(self, 0)[0] == status.BUSY:
            step = int(abs(self._attached_motor.read() - self._startpos) /
                       self._step_size)
            ret = (steptime + self._time_preset) * (self.resosteps - step)
        else:
            ret = (steptime + self._time_preset) * self.resosteps
        detTime = self._attached_detector.doEstimateTime(elapsed)
        ret += detTime if detTime is not None else 0.
        return ret

    def valueInfo(self):
        _val_info = Value('step', unit='', type='other', fmtstr='%d' + '/%d' %
                          self.resosteps),
        return _val_info + self._attached_detector.valueInfo()

    def arrayInfo(self):
        return self._arraydesc,

    def presetInfo(self):
        return set(['resosteps']) | self._attached_detector.presetInfo()

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
