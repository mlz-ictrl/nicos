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
from PyTango import CommunicationFailed

from nicos.core import Value
from nicos.core.errors import CommunicationError
from nicos.core.device import Measurable
from nicos.devices.tango import PyTangoDevice, NamedDigitalOutput
from nicos.core.params import Param, oneof, dictof, tupleof
from nicos.devices.generic.sequence import MeasureSequencer, SeqCall
from nicos.core.image import ImageProducer, ImageType


class TofDetector(PyTangoDevice, MeasureSequencer, ImageProducer):
    """Basic Tango Device for TofDetector."""

    STRSHAPE = ['x', 'y', 'z', 't']
    TOFMODE  = ['notof', 'tof']

    attached_devices = {
        'expshutter':   (NamedDigitalOutput, 'Experiment shutter device'),
        'fpga':         (Measurable, 'ZEA-2 counter card'),
    }

    parameters = {
        'detshape':    Param('Shape of tof detector', type=dictof(str, int)),
        'tofmode':     Param('Data acquisition mode', type=oneof('notof', 'tof')),
        'nrtimechan':  Param('Number of time channel',type=long),
        'divisor':     Param('Divisor between hardware and software time slice',\
                           type=long,settable=False),
        'offsetdelay': Param('Offset delay in measure begin', type=long,\
                           unit='microsec',settable=False),
        'readchannels': Param('Tuple of (start, end) channel numbers will be '
                              'returned by a read.', type=tupleof(int, int),
                              default=(0, 0), settable=True, mandatory=True)
    }


    def doInit(self, mode):
        self.log.debug("doInit")
        self.imagetype = ImageType((int(self.detshape["x"]),\
                                   int(self.detshape["t"])),\
                                   numpy.uint32)
        self._dev.set_timeout_millis(10000)

    def _generateSequence(self, *args, **kwargs):
        seq = []
        seq.append(SeqCall(self._dev.Clear))
        self.log.debug("Detector cleared")
        seq.append(SeqCall(self._dev.Start))
        self.log.debug("Detector started")
        seq.append(SeqCall(self._adevs['fpga'].start))
        self.log.debug("Counter started")
        seq.append(SeqCall(self._adevs['fpga'].wait))
        seq.append(SeqCall(self._dev.Stop))
        return seq

    def doSetPreset(self, **preset):
        if 't' in preset:
            self._adevs['fpga'].preselection = preset['t']

    def doReadTofmode(self):
        return self.TOFMODE[self._dev.mode]

    def doWriteTofmode(self,value):
        self._dev.mode = 0 if value == self.TOFMODE[0] else 1

    def doReadNrtimechan(self):
        return self._dev.numchan

    def doWriteNrtimechan(self,value):
        self._dev.numchan = value

    def doReadDivisor(self):
        return self._dev.divisor

    def doWriteDivisor(self,value):
        self._dev.divisor = value

    def doReadOffsetdelay(self):
        return self._dev.delay

    def doWriteOffsetdelay(self,value):
        self._dev.delay= value

    def doReadDetshape(self):
        #shvalue = self._getProperty('shape')
        #Method currently not implemented in server
        shvalue = self._dev.get_property('shape').values()[0]
        dshape = dict()
        for i in range(4):
            dshape[self.STRSHAPE[i]] = shvalue[i]
        return dshape

    def doStart(self):
        self.wait()
        self._startSequence(self._generateSequence())

    def doPause(self):
        self._adevs['fpga'].pause()
        self.log.debug("Tof Detector pause")

    def doResume(self):
        self._adevs['fpga'].resume()
        self.log.debug("Tof Detector resume")

    def doStop(self):
        self._dev.Stop()
        self.log.debug("Tof Detector stop")

    def doRead(self, maxage=0):
        res = None
        try:
            array = self._dev.value.tolist()
            start, end = self.readchannels
            res = array[start:end+1]
        except CommunicationFailed: # PyTango
            raise CommunicationError(self, "Readout command timed out")
        return res

    def valueInfo(self):
        start, end = self.readchannels
        return tuple((Value("chan-%d" % i, unit="cts", errors="sqrt",
                            type="counter", fmtstr="%d")
                      for i in range(start, end + 1)))

    def readImage(self):
        # get current data array from detector
        return numpy.array(self._dev.value).reshape(int(self.detshape["x"]),
                                                    int(self.detshape["t"]))

    def readFinalImage(self):
        # get final data at end of measurement
        self.log.debug("Tof Detector read final image")
        return self.readImage()
