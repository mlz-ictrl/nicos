# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

from time import sleep

import numpy

from nicos.core import Value, SIMULATION
from nicos.core.constants import FINAL, INTERRUPTED
from nicos.core.params import Param, Attach, oneof, dictof, tupleof, intrange, \
    ArrayDesc
from nicos.devices.polarized.flipper import BaseFlipper, ON, OFF
from nicos.devices.generic.detector import ImageChannelMixin, PassiveChannel, \
    Detector
from nicos.devices.tango import PyTangoDevice


P_TIME = 't'
P_TIME_SF = 'tsf'
P_TIME_NSF = 'tnsf'
P_MON = 'mon0'
P_MON_SF = 'mon0sf'
P_MON_NSF = 'mon0nsf'


class TofChannel(PyTangoDevice, ImageChannelMixin, PassiveChannel):
    """Basic Tango Device for TofDetector."""

    STRSHAPE = ['x', 'y', 'z', 't']
    TOFMODE = ['notof', 'tof']

    parameters = {
        'detshape':     Param('Shape of tof detector', type=dictof(str, int)),
        'tofmode':      Param('Data acquisition mode',
                              type=oneof('notof', 'tof'), settable=True),
        'nrtimechan':   Param('Number of time channel', type=intrange(1, 1024),
                              settable=True),
        'divisor':      Param('Divisor between hard- and software time slice',
                              type=int, settable=True),
        'offsetdelay':  Param('Offset delay in measure begin', type=int,
                              unit='us', settable=True),
        'readchannels': Param('Tuple of (start, end) channel numbers will be '
                              'returned by a read', type=tupleof(int, int),
                              default=(0, 0), settable=True, mandatory=True),
        'readtimechan': Param('Tuple of (start, end) integrated time channels '
                              'will be returned by a read',
                              type=tupleof(int, int),
                              default=(0, 0), settable=True, mandatory=True),
    }

    def doInit(self, mode):
        self.log.debug("doInit")
        self.arraydesc = ArrayDesc('data',
                                   (self.detshape.get('t', 1),
                                    self.detshape.get('x', 1)),
                                   numpy.uint32)
        if mode != SIMULATION:
            self._dev.set_timeout_millis(10000)

    def doPrepare(self):
        self._dev.Clear()
        PyTangoDevice._hw_wait(self)
        self.log.debug("Detector cleared")
        self._dev.Prepare()

    def doStart(self):
        start, end = self.readchannels
        self.readresult = [0] * (end - start + 1)
        self._dev.Start()
        self.log.debug("Detector started")

    def doFinish(self):
        self._dev.Stop()
        sleep(0.2)
        PyTangoDevice._hw_wait(self)

    def doStop(self):
        self._dev.Stop()

    def doPause(self):
        self.doFinish()

    def doResume(self):
        self.doStart()

    def doReadTofmode(self):
        return self.TOFMODE[self._dev.mode]

    def doWriteTofmode(self, value):
        if value == self.TOFMODE[0]:
            self._dev.mode = 0
            self.nrtimechan = 1
        else:
            self._dev.mode = 1

    def doReadNrtimechan(self):
        return self._dev.numchan

    def doWriteNrtimechan(self, value):
        self._dev.numchan = value
        if value > 1:
            self.tofmode = self.TOFMODE[1]
        self._pollParam('detshape')

    def doReadDivisor(self):
        return self._dev.divisor

    def doWriteDivisor(self, value):
        self._dev.divisor = value

    def doReadOffsetdelay(self):
        return self._dev.delay

    def doWriteOffsetdelay(self, value):
        self._dev.delay = value

    def doReadDetshape(self):
        # XXX non-standard implementation of GetProperties; should be fixed in
        # the server
        shvalue = self._dev.GetProperties(("shape", 'device'))
        return {'x': int(shvalue[2]), 't': int(shvalue[5])}

    def valueInfo(self):
        start, end = self.readchannels
        return tuple(Value("chan-%d" % i, unit="cts", errors="sqrt",
                           type="counter", fmtstr="%d")
                     for i in range(start, end + 1))

    def readArray(self, quality):
        if quality in (FINAL, INTERRUPTED):
            self.log.debug("Tof Detector read final image")
            start, end = self.readchannels
            # get current data array from detector
            array = numpy.asarray(self._dev.value, numpy.uint32)
            array = array.reshape(self.detshape['t'], self.detshape['x'])
            if self.tofmode == 'tof':
                startT, endT = self.readtimechan
                res = array[startT:endT+1].sum(axis=0)[start:end+1]
            else:
                res = array[0, start:end+1]
            self.readresult = res.tolist()
            return array
        # live images currently not supported
        return None


class DNSDetector(Detector):
    """Detector supporting different presets for spin flipper on or off."""

    attached_devices = {
        'flipper': Attach('Spin flipper device which will be read out '
                          'with respect to setting presets.', BaseFlipper),
    }

    def doTime(self, preset):
        if P_TIME in preset:
            return preset[P_TIME]
        elif P_TIME_SF in preset and self._attached_flipper.read() == ON:
            return preset[P_TIME_SF]
        elif P_TIME_NSF in preset and self._attached_flipper.read() == OFF:
            return preset[P_TIME_NSF]
        return 0  # no preset that we can estimate found

    def presetInfo(self):
        presets = Detector.presetInfo(self)
        presets.update((P_TIME_SF, P_TIME_NSF, P_MON_SF, P_MON_NSF))
        return presets

    def doSetPreset(self, **preset):
        if P_MON_SF in preset and P_MON_NSF in preset:
            if self._attached_flipper.read() == ON:
                m = preset[P_MON_SF]
            else:
                m = preset[P_MON_NSF]
            new_preset = {P_MON: m}
        elif P_MON_SF in preset or P_MON_NSF in preset:
            self.log.warning('Incorrect preset setting. Specify either both '
                             '%s and %s or only %s.' %
                             (P_MON_SF, P_MON_NSF, P_MON))
            return
        elif P_TIME_SF in preset and P_TIME_NSF in preset:
            if self._attached_flipper.read() == ON:
                t = preset[P_TIME_SF]
            else:
                t = preset[P_TIME_NSF]
            new_preset = {P_TIME: t}
        elif P_TIME_SF in preset or P_TIME_NSF in preset:
            self.log.warning('Incorrect preset setting. Specify either both '
                             '%s and %s or only %s.' %
                             (P_TIME_SF, P_TIME_NSF, P_TIME))
            return
        elif P_MON in preset:
            new_preset = {P_MON: preset[P_MON]}
        elif P_TIME in preset:
            new_preset = {P_TIME: preset[P_TIME]}
        Detector.doSetPreset(self, **new_preset)
