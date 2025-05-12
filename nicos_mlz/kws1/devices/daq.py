# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

import numpy as np
from tango import DevState

from nicos.core import MASTER, SIMULATION, Attach, ConfigurationError, \
    Measurable, Moveable, Override, Param, Readable, Value, intrange, listof, \
    oneof, status, tupleof
from nicos.core.constants import FINAL, INTERRUPTED
from nicos.core.params import ArrayDesc
from nicos.devices.generic.detector import ActiveChannel, Detector, \
    ImageChannelMixin, PostprocessPassiveChannel
from nicos.devices.generic.virtual import VirtualImage
from nicos.devices.tango import PyTangoDevice

from nicos_mlz.jcns.devices.detector import calculateRate
from nicos_mlz.jcns.devices.fpga import FPGATimerChannel

RTMODES = ('standard', 'tof', 'realtime', 'realtime_external')


class KWSImageChannel(ImageChannelMixin, PyTangoDevice, ActiveChannel):

    attached_devices = {
        'timer':       Attach('The timer channel', Measurable),
        'highvoltage': Attach('The high voltage switch', Moveable,
                              optional=True),
    }

    parameters = {
        'mode':        Param('Measurement mode switch', type=oneof(*RTMODES),
                             settable=True, category='general'),
        'slices':      Param('Calculated TOF slices', internal=True,
                             unit='us', settable=True, type=listof(int),
                             category='general'),
    }

    def doInit(self, mode):
        self._rate_data = [0, 0]
        if mode != SIMULATION:
            self._resolution = tuple(self._dev.detectorSize)
        else:
            self._resolution = (128, 128, 1)
        shape = (self._resolution[1], self._resolution[0])
        self.arraydesc = ArrayDesc(self.name, shape, np.uint32)

    def _configure(self, tofsettings):
        value = self.mode
        if value == 'standard':
            self._setup_standard()
        elif value == 'tof':
            self._setup_tof(False, tofsettings)
        elif value == 'realtime':
            self._setup_tof(False, tofsettings)
        elif value == 'realtime_external':
            self._setup_tof(True, tofsettings)

    def _setup_standard(self):
        if self._mode != SIMULATION:
            self._dev.measureMode = 0
        self.slices = []
        shape = (self._resolution[1], self._resolution[0])
        # (y, x)
        self.arraydesc = ArrayDesc(self.name, shape, np.uint32)

    def _setup_tof(self, ext_trigger, tofsettings):
        # set timing of TOF slices
        channels, interval, q, custom = tofsettings
        if custom:
            if custom[0] != 0:
                custom = [0] + custom
            times = custom
        else:
            times = [0]
            for i in range(channels):
                times.append(times[-1] + int(interval * q**i))
        self.slices = times
        shape = (channels, self._resolution[1], self._resolution[0])
        # (t, y, x)
        self.arraydesc = ArrayDesc(self.name, shape, np.uint32)
        if self._mode == SIMULATION:
            return
        if ext_trigger:
            # RT measurement
            self._dev.measureMode = 2
            # number of external signals, != 1 not tested yet
            self._dev.rtParameter = 1
        else:
            # TOF measurement -- since the detector starts a TOF sweep
            # when the inhibit signal is taken away, this also works for
            # realtime without external signal
            self._dev.measureMode = 1
        self._dev.tofRange = times

    def doPrepare(self):
        if self._attached_highvoltage:
            self._attached_highvoltage.maw('on')
        self._dev.Clear()
        self._dev.Prepare()

    def doStart(self):
        self.readresult = [0, 0.0]
        self._dev.Start()

    def doPause(self):
        # no stop necessary, gate will be cleared by counter card
        return True

    def doResume(self):
        pass

    def doFinish(self):
        self._dev.Stop()

    def doStop(self):
        self.doFinish()

    def doStatus(self, maxage=0):
        if self._dev.State() == DevState.MOVING:
            return status.BUSY, 'counting'
        return status.OK, 'idle'

    def valueInfo(self):
        return (Value(name='total', type='counter', fmtstr='%d',
                      errors='sqrt', unit='cts'),
                Value(name='rate', type='monitor', fmtstr='%.1f', unit='cps'))

    def doReadArray(self, quality):
        shape = self.arraydesc.shape
        arr = self._dev.GetBlock([0, int(np.product(shape))])
        cts, seconds = arr.sum(), self._attached_timer.read(0)[0]
        rate = calculateRate(self._rate_data, quality, cts, seconds)
        self.readresult = [cts, rate]
        return np.asarray(arr, np.uint32).reshape(shape)


class GEImageChannel(KWSImageChannel):
    """GE detector image with the flag to rebin to 8x8 pixel size."""

    parameters = {
        'rebin8x8': Param('Rebin data to 8x8 mm pixel size', type=bool,
                          default=False, settable=True, mandatory=False),
    }

    def _configure(self, tofsettings):
        if self._mode != SIMULATION:
            self._dev.binning = [1, 2, 1] if self.rebin8x8 else [1, 1, 1]
        KWSImageChannel._configure(self, tofsettings)


class VirtualKWSImageChannel(VirtualImage):

    parameters = {
        'mode':        Param('Measurement mode switch', type=oneof(*RTMODES),
                             settable=True, category='general'),
        'slices':      Param('Calculated TOF slices', internal=True,
                             unit='us', settable=True, type=listof(int),
                             category='general'),
    }

    def _configure(self, tofsettings):
        if self.mode == 'standard':
            self.slices = []
            self.arraydesc = ArrayDesc(self.name, self.sizes[::-1], np.uint32)
        else:
            # set timing of TOF slices
            channels, interval, q, custom = tofsettings
            if custom:
                if custom[0] != 0:
                    custom = [0] + custom
                times = custom
            else:
                times = [0]
                for i in range(channels):
                    times.append(times[-1] + int(interval * q**i))
            self.slices = times
            self.arraydesc = ArrayDesc(
                self.name, (channels,) + self.sizes[::-1], np.uint32)

    def doReadArray(self, quality):
        res = VirtualImage.doReadArray(self, quality)
        if self.mode != 'standard':
            return np.repeat([res], len(self.slices) - 1, 0)
        return res


class ROIRateChannel(PostprocessPassiveChannel):
    """Calculates rate on the detector outside the beamstop."""

    attached_devices = {
        'bs_x':  Attach('Beamstop x position', Readable),
        'bs_y':  Attach('Beamstop y position', Readable),
        'timer': Attach('The timer channel', Measurable),
    }

    parameters = {
        'xscale':    Param('Pixel (scale, offset) for calculating the beamstop '
                           'X center position from motor position',
                           type=tupleof(float, float), settable=True),
        'yscale':    Param('Pixel (scale, offset) for calculating the beamstop '
                           'Y center position from motor position',
                           type=tupleof(float, float), settable=True),
        'size':      Param('Size of beamstop in pixels (w, h)',
                           type=tupleof(int, int), settable=True),
        'roi':       Param('Rectangular region of interest (x, y, w, h)',
                           type=tupleof(int, int, int, int), settable=False),
    }

    parameter_overrides = {
        'unit':   Override(default='cps'),
        'fmtstr': Override(default='%d'),
    }

    _cts_seconds = [0, 0]

    def getReadResult(self, arrays, _results, quality):
        arr = arrays[0]
        if arr is None:
            return [0, 0]

        if any(self.size):
            w, h = self.size
            bs_x = self._attached_bs_x.read() * self.xscale[0] + self.xscale[1]
            bs_y = self._attached_bs_y.read() * self.yscale[0] + self.yscale[1]
            x = int(round(bs_x - w/2.))
            y = int(round(bs_y - h/2.))
            self._setROParam('roi', (x, y, w, h))
            outer = arr[y:y+h, x:x+w].sum()
            cts = outer
        else:
            self._setROParam('roi', (0, 0, 0, 0))
            cts = arr.sum()

        seconds = self._attached_timer.read(0)[0]
        cts_per_second = 0

        if seconds > 1e-8:
            if quality in (FINAL, INTERRUPTED) or seconds <= \
                    self._cts_seconds[1]:  # rate for full detector / time
                cts_per_second = cts / seconds
            elif cts > self._cts_seconds[0]:  # live rate on detector (using deltas)
                cts_per_second = (cts - self._cts_seconds[0]) / (
                    seconds - self._cts_seconds[1])
            else:
                cts_per_second = 0
        self._cts_seconds = [cts, seconds]

        return [cts, cts_per_second]

    def valueInfo(self):
        return (
            Value(name=self.name + '.roi', type='counter', fmtstr='%d', errors='sqrt'),
            Value(name=self.name + '.signal', type='monitor', fmtstr='%.2f'),
        )


class KWSDetector(Detector):

    attached_devices = {
        'shutter':     Attach('Shutter for opening and closing', Moveable,
                              optional=True),
    }

    parameters = {
        'mode':        Param('Measurement mode switch', type=oneof(*RTMODES),
                             settable=True, volatile=True),
        'tofchannels': Param('Number of TOF channels',
                             type=intrange(1, 1023), settable=True,
                             category='general'),
        'tofinterval': Param('Interval dt between TOF channels', type=int,
                             unit='us', settable=True, category='general'),
        'tofprogression':
                       Param('Progression q of TOF intervals (t_i = dt * q^i)',
                             type=float, default=1.0, settable=True,
                             category='general'),
        'tofcustom':   Param('Custom selection of TOF slices',
                             type=listof(int), settable=True),
        'kwscounting': Param('True when taking data with kwscount()',
                             type=bool, default=False, settable=True,
                             internal=True),
        'openshutter': Param('True to open/close shutter while counting',
                             type=bool, default=True, settable=True),
    }

    _img = None

    def doInit(self, session_mode):
        Detector.doInit(self, session_mode)
        self._img = self._attached_images[0]
        if session_mode == MASTER:
            if not self._attached_images:
                raise ConfigurationError(self, 'KWSDetector needs a KWSChannel '
                                         'as attached image')
            self.kwscounting = False

    def _configure(self):
        for ch in self._channels:
            if isinstance(ch, FPGATimerChannel):
                ch.extmode = self.mode == 'realtime_external'
        # TODO: ensure that total meas. time < 2**31 usec
        self._img._configure((self.tofchannels, self.tofinterval,
                              self.tofprogression, self.tofcustom))

    def doReadMode(self):
        if self._img is None:
            return 'standard'  # bootstrap
        return self._img.mode

    def doWriteMode(self, mode):
        self._img.mode = mode

    def doSetPreset(self, **preset):
        # override time preset in realtime mode
        if self.mode in ('realtime', 'realtime_external'):
            # set counter card preset to last RT slice
            preset = {'t': self._img.slices[-1] / 1000000.0}
        Detector.doSetPreset(self, **preset)

    def doPrepare(self):
        self._configure()
        Detector.doPrepare(self)

    def doStart(self):
        if self._attached_shutter and self.openshutter:
            self._attached_shutter.maw('open')
        self.kwscounting = True
        Detector.doStart(self)

    def doFinish(self):
        Detector.doFinish(self)
        self.kwscounting = False
        if self._attached_shutter and self.openshutter:
            self._attached_shutter.maw('closed')

    def doStop(self):
        Detector.doStop(self)
        self.kwscounting = False
        if self._attached_shutter and self.openshutter:
            self._attached_shutter.maw('closed')
