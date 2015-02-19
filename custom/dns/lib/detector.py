# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

import numpy

from nicos.core import Value
from nicos.core.device import Measurable
from nicos.devices.tango import PyTangoDevice, NamedDigitalOutput
from nicos.core.params import Param, Attach, oneof, dictof, tupleof
from nicos.devices.generic.sequence import MeasureSequencer, SeqMethod
from nicos.core.image import ImageProducer, ImageType
from nicos.devices.polarized.flipper import BaseFlipper, ON


T_TIME = 't'
T_SPIN_FLIP = 'tsf'
T_NO_SPIN_FLIP = 'tnsf'


class FlipperPresets(Measurable):

    attached_devices = {
        'flipper': Attach('Spin flipper device which will be read out '
                          'with respect to setting presets.', BaseFlipper),
    }

    @property
    def flipper(self):
        return self._adevs['flipper']

    def presetInfo(self):
        return (T_TIME, T_SPIN_FLIP, T_NO_SPIN_FLIP)

    def doStart(self):
        raise NotImplementedError('Please provide an implementation for '
                                  'doStart.')

    def doStop(self):
        raise NotImplementedError('Please provide an implementation for '
                                  'doStop.')

    def doIsCompleted(self):
        raise NotImplementedError('Please provide an implementation for '
                                  'doIsCompleted.')


class TofDetectorBase(PyTangoDevice, ImageProducer, MeasureSequencer):
    """Basic Tango Device for TofDetector."""

    STRSHAPE = ['x', 'y', 'z', 't']
    TOFMODE  = ['notof', 'tof']

    attached_devices = {
        'expshutter': Attach('Experiment shutter device', NamedDigitalOutput),
        'timer':      Attach('ZEA-2 counter card timer channel', Measurable),
        'monitor':    Attach('ZEA-2 counter card monitor channel', Measurable),
    }

    parameters = {
        'detshape':    Param('Shape of tof detector', type=dictof(str, int)),
        'tofmode':     Param('Data acquisition mode', type=oneof('notof', 'tof')),
        'nrtimechan':  Param('Number of time channel', type=long),
        'divisor':     Param('Divisor between hardware and software time slice',
                             type=long, settable=False),
        'offsetdelay': Param('Offset delay in measure begin', type=long,
                             unit='microsec', settable=False),
        'readchannels': Param('Tuple of (start, end) channel numbers will be '
                              'returned by a read.', type=tupleof(int, int),
                              default=(0, 0), settable=True, mandatory=True)
    }

    def doInit(self, mode):
        self.log.debug("doInit")
        self.imagetype = ImageType((int(self.detshape["x"]),
                                    int(self.detshape["t"])),
                                   numpy.uint32)
        self._dev.set_timeout_millis(10000)

    def _generateSequence(self, *args, **kwargs):
        seq = []
        seq.append(SeqMethod(self._dev, 'Clear'))
        self.log.debug("Detector cleared")
        seq.append(SeqMethod(self._dev, 'Start'))
        self.log.debug("Detector started")
        seq.append(SeqMethod(self._adevs['timer'], 'start'))
        self.log.debug("Counter started")
        seq.append(SeqMethod(self._adevs['timer'], 'wait'))
        seq.append(SeqMethod(self._dev, 'Stop'))
        return seq

    def doSetPreset(self, **preset):
        if T_TIME in preset:
            t = preset[T_TIME]
        else:
            t = t or 1
            self.log.warning("Incorrect preset setting. Please specify " +
                             T_TIME + ". Falling back to previous value '%g'."
                             % t)
        self._adevs['timer'].preselection = t

    def doReadTofmode(self):
        return self.TOFMODE[self._dev.mode]

    def doWriteTofmode(self, value):
        self._dev.mode = 0 if value == self.TOFMODE[0] else 1

    def doReadNrtimechan(self):
        return self._dev.numchan

    def doWriteNrtimechan(self, value):
        self._dev.numchan = value

    def doReadDivisor(self):
        return self._dev.divisor

    def doWriteDivisor(self, value):
        self._dev.divisor = value

    def doReadOffsetdelay(self):
        return self._dev.delay

    def doWriteOffsetdelay(self, value):
        self._dev.delay = value

    def doReadDetshape(self):
        # shvalue = self._getProperty('shape')
        # Method currently not implemented in server
        shvalue = self._dev.get_property('shape').values()[0]
        dshape = dict()
        for i in range(4):
            dshape[self.STRSHAPE[i]] = shvalue[i]
        return dshape

    def doStart(self):
        self.wait()
        self._startSequence(self._generateSequence())

    def doPause(self):
        self._adevs['timer'].pause()
        self.log.debug("Tof Detector pause")

    def doResume(self):
        self._adevs['timer'].resume()
        self.log.debug("Tof Detector resume")

    def doStop(self):
        self._dev.Stop()
        self.log.debug("Tof Detector stop")

    def doRead(self, maxage=0):
        res = None
        array = self._dev.value.tolist()
        start, end = self.readchannels
        res = array[start:end+1]
        tval = self._adevs['timer'].read()
        mval = self._adevs['monitor'].read()
        return [tval, mval] + res

    def valueInfo(self):
        start, end = self.readchannels
        return self._adevs['timer'].valueInfo() + \
            self._adevs['monitor'].valueInfo() + \
            tuple(Value("chan-%d" % i, unit="cts", errors="sqrt",
                        type="counter", fmtstr="%d")
                  for i in range(start, end + 1))

    def readImage(self):
        # get current data array from detector
        return numpy.array(self._dev.value).reshape(int(self.detshape["x"]),
                                                    int(self.detshape["t"]))

    def readFinalImage(self):
        # get final data at end of measurement
        self.log.debug("Tof Detector read final image")
        return self.readImage()


class TofDetector(TofDetectorBase, FlipperPresets):
    """TofDetector supporting different presets for spin flipper on or off."""

    def doSetPreset(self, **preset):
        if T_SPIN_FLIP in preset and T_NO_SPIN_FLIP in preset:
            if self.flipper.read() == ON:
                t = preset[T_SPIN_FLIP]
            else:
                t = preset[T_NO_SPIN_FLIP]
        elif T_TIME in preset:
            t = preset[T_TIME]
        else:
            t = t or 1
            self.log.warning("Incorrect preset setting. Specify either " +
                             T_SPIN_FLIP + " and " + T_NO_SPIN_FLIP +
                             " or just " + T_TIME + ". Falling back to "
                             "previous value '%g'." % t)
        self._adevs['timer'].preselection = t
