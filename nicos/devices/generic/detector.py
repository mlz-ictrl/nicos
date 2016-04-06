#  -*- coding: utf-8 -*-
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Generic detector and channel classes for NICOS."""

from nicos.core import Attach, DeviceMixinBase, Measurable, Override, Param, \
    Readable, UsageError, Value, multiStatus, status, listof, oneof, none_or, \
    LIVE, INTERMEDIATE
from nicos.utils import uniq


class PassiveChannel(Measurable):
    """Abstract base class for one channel of a aggregate detector.

    Passive channels cannot stop the measurement.
    """

    parameters = {
        'ismaster': Param('If this channel is a master', type=bool),
    }

    # methods to be implemented in concrete subclasses

    def doSetPreset(self, **preset):
        raise UsageError(self, 'This channel cannot be used as a detector')

    def doStart(self):
        pass

    def doFinish(self):
        pass

    def doStop(self):
        pass

    def doRead(self, maxage=0):
        return []

    def valueInfo(self):
        return ()

    def doStatus(self, maxage=0):
        return status.OK, 'idle'


class DummyDetector(PassiveChannel):
    """A Dummy detector just providing nameand value info

    Use for scans that add only processed values from subscans
    """

    parameter_overrides = {
        'unit':   Override(default='cts'),
        'fmtstr': Override(default='%.2f'),
    }

    def valueInfo(self):
        return Value(self.name, unit=self.unit, type='other', fmtstr=self.fmtstr),


class ActiveChannel(PassiveChannel):
    """Abstract base class for channels that can (but don't need to) end the
    measurement.
    """

    parameters = {
        'preselection': Param('Preset value for this channel', type=float,
                              settable=True),
    }

    parameter_overrides = {
        'ismaster': Override(settable=True),
    }

    # set to True to get a simplified doEstimateTime
    is_timer = False

    def doRead(self, maxage=0):
        raise NotImplementedError('implement doRead')

    def valueInfo(self):
        raise NotImplementedError('implement valueInfo')

    def doEstimateTime(self, elapsed):
        if not self.ismaster or self.doStatus()[0] != status.BUSY:
            return None
        if self.is_timer:
            return self.preselection - elapsed
        else:
            counted = float(self.doRead()[0])
            # only estimated if we have more than 3% or at least 100 counts
            if counted > 100 or counted > 0.03 * self.preselection:
                if 0 <= counted <= self.preselection:
                    return (self.preselection - counted) * elapsed / counted


class TimerChannelMixin(DeviceMixinBase):
    """Mixin for channels that return measured time."""

    is_timer = True

    parameter_overrides = {
        'unit':   Override(default='s'),
        'fmtstr': Override(default='%.2f'),
    }

    def valueInfo(self):
        return Value(self.name, unit='s', type='time', fmtstr=self.fmtstr),

    def doTime(self, preset):
        if self.ismaster:
            return self.preselection
        else:
            return 0

    def doSimulate(self, preset):
        if self.ismaster:
            return [self.preselection]
        return [0.0]


class CounterChannelMixin(DeviceMixinBase):
    """Mixin for channels that return a single counts value."""

    is_timer = False

    parameters = {
        'type': Param('Type of channel: monitor or counter',
                      type=oneof('monitor', 'counter'), mandatory=True),
    }

    parameter_overrides = {
        'unit':         Override(default='cts'),
        'fmtstr':       Override(default='%d'),
        'preselection': Override(type=int),
    }

    def valueInfo(self):
        return Value(self.name, unit='cts', errors='sqrt',
                     type=self.type, fmtstr=self.fmtstr),

    def doSimulate(self, preset):
        if self.ismaster:
            return [int(self.preselection)]
        return [0]


class ImageChannelMixin(DeviceMixinBase):
    """Mixin for channels that return images."""

    parameters = {
        'readresult': Param('Storage for scalar results from image '
                            'filtering, to be returned from doRead()',
                            type=listof(float), settable=True,
                            userparam=False),
    }

    parameter_overrides = {
        'unit':         Override(default='cts'),
        'preselection': Override(type=int),
    }

    # set this to an ArrayDesc instance, either as a class attribute
    # or dynamically as an instance attribute
    arraydesc = None

    def doRead(self, maxage=0):
        return self.readresult

    def readArray(self, quality):
        """This method should return the detector data array or `None` if no
        data is available.

        The *quality* parameter is one of the constants defined in the
        `nicos.core.constants` module:

        * LIVE is for intermediate data that should not be written to files.
        * INTERMEDIATE is for intermediate data that should be written.
        * FINAL is for final data.
        * INTERRUPTED is for data read after the counting was interrupted by
          an exception.

        For detectors which just supports FINAL images, e.g. Image plate
        detectors this method should return an array when *quality* is `FINAL`
        and `None` otherwise.  Most other detectors should also read out and
        return the data when *quality* is `INTERRUPTED`.
        """
        raise NotImplementedError('implement readArray in %s' %
                                  self.__class__.__name__)


class Detector(Measurable):
    """Detector using multiple (synchronized) channels."""

    attached_devices = {
        'timers':   Attach('Timer channel', PassiveChannel,
                           multiple=True, optional=True),
        'monitors': Attach('Monitor channels', PassiveChannel,
                           multiple=True, optional=True),
        'counters': Attach('Counter channels', PassiveChannel,
                           multiple=True, optional=True),
        'images':   Attach('Image channels', ImageChannelMixin,
                           multiple=True, optional=True),
        'others':   Attach('Channels that return e.g. filenames',
                           PassiveChannel, multiple=True, optional=True),
    }

    parameters = {
        'liveinterval':  Param('Interval to read out live images (None '
                               'to disable live readout)',
                               type=none_or(float), unit='s', settable=True),
        'saveintervals': Param('Intervals to read out intermediate images '
                               '(empty to disable); [x, y, z] will read out '
                               'after x, then after y, then every z seconds',
                               type=listof(float), unit='s', settable=True),
    }

    parameter_overrides = {
        'fmtstr': Override(volatile=True),
    }

    hardware_access = False
    multi_master = True

    _last_live = 0
    _last_save = 0
    _last_save_index = 0

    # allow overwriting in derived classes
    def _presetiter(self):
        """yields name, device tuples for all 'preset-able' devices"""
        # a device may react to more than one presetkey....
        for i, dev in enumerate(self._attached_timers):
            if isinstance(dev, ActiveChannel):
                if i == 0:
                    yield ('t', dev)
                    yield ('time', dev)
                yield ('timer%d' % (i + 1), dev)
        for i, dev in enumerate(self._attached_monitors):
            if isinstance(dev, ActiveChannel):
                yield ('mon%d' % (i + 1), dev)
        for i, dev in enumerate(self._attached_counters):
            if isinstance(dev, ActiveChannel):
                if i == 0:
                    yield ('n', dev)
                yield ('det%d' % (i + 1), dev)
                yield ('ctr%d' % (i + 1), dev)
        for i, dev in enumerate(self._attached_images):
            if isinstance(dev, ActiveChannel):
                yield ('img%d' % (i + 1), dev)

    def doPreinit(self, mode):
        presetkeys = {}
        for name, dev in self._presetiter():
            # later mentioned presetnames dont overwrite earlier ones
            presetkeys.setdefault(name, dev)
        self._channels = uniq(self._attached_timers + self._attached_monitors +
                              self._attached_counters + self._attached_images +
                              self._attached_others)
        self._presetkeys = presetkeys
        self._getMasters()

    def _getMasters(self):
        """Internal method to collect all masters."""
        masters = []
        slaves = []
        for ch in self._channels:
            if ch.ismaster:
                masters.append(ch)
            else:
                slaves.append(ch)
        self._masters, self._slaves = masters, slaves

    def doSetPreset(self, **preset):
        if not preset:
            # keep old settings
            return
        for master in self._masters:
            master.ismaster = False
        should_be_masters = set()
        for name in preset:
            if name in self._presetkeys:
                dev = self._presetkeys[name]
                dev.ismaster = True
                dev.preselection = preset[name]
                should_be_masters.add(dev)
        self._getMasters()
        if set(self._masters) != should_be_masters:
            if not self._masters:
                self.log.warning('no master configured, detector may not stop')
            else:
                self.log.warning('master setting for devices %s ignored by '
                                 'detector' % ', '.join(should_be_masters -
                                                        set(self._masters)))

    def doPrepare(self):
        for slave in self._slaves:
            slave.prepare()
        for master in self._masters:
            master.prepare()

    def doStart(self):
        self._last_live = 0
        self._last_save = 0
        self._last_save_index = 0
        for slave in self._slaves:
            slave.start()
        for master in self._masters:
            master.start()

    def doTime(self, preset):
        self.doSetPreset(**preset)  # okay in simmode
        return self.doEstimateTime(0) or 0

    def doPause(self):
        # XXX: rework pause logic (use mixin?)
        for slave in self._slaves:
            if not slave.pause():
                return False
        for master in self._masters:
            if not master.pause():
                return False
        return True

    def doResume(self):
        # XXX: rework pause logic (use mixin?)
        for slave in self._slaves:
            slave.resume()
        for master in self._masters:
            master.resume()

    def doFinish(self):
        for master in self._masters:
            master.finish()
        for slave in self._slaves:
            slave.finish()

    def doStop(self):
        for master in self._masters:
            master.stop()
        for slave in self._slaves:
            slave.stop()

    def doRead(self, maxage=0):
        ret = []
        for ch in self._channels:
            ret.extend(ch.read())
        return ret

    def doReadArrays(self, quality):
        return [img.readArray(quality) for img in self._attached_images]

    def duringMeasureHook(self, elapsed):
        if self.liveinterval is not None:
            if self._last_live + self.liveinterval < elapsed:
                self._last_live = elapsed
                return LIVE
        intervals = self.saveintervals
        if intervals:
            if self._last_save + intervals[self._last_save_index] < elapsed:
                self._last_save_index = min(self._last_save_index + 1,
                                            len(intervals) - 1)
                self._last_save = elapsed
                return INTERMEDIATE
        return None

    def doSimulate(self, preset):
        self.doSetPreset(**preset)  # okay in simmode
        return self.doRead()

    def doStatus(self, maxage=0):
        self._getMasters()
        if not self._masters:
            return status.OK, 'idle'
        st, text = multiStatus(self._adevs, maxage)
        if st == status.ERROR:
            return st, text
        # XXX: shorter status strings?
        for master in self._masters:
            masterstatus = master.status(maxage)
            if masterstatus[0] == status.OK:
                return status.OK, text
        return st, text

    def doReset(self):
        for ch in self._channels:
            ch.reset()

    def valueInfo(self):
        # XXX: the value names retrieved here contain the channel device names,
        # but the presets are generic (monX, detX)
        ret = []
        for ch in self._channels:
            ret.extend(ch.valueInfo())
        return tuple(ret)

    def arrayInfo(self):
        return tuple(img.arraydesc for img in self._attached_images)

    def doReadFmtstr(self):
        return ', '.join('%s = %s' % (v.name, v.fmtstr)
                         for v in self.valueInfo())

    def presetInfo(self):
        return set(self._presetkeys)

    def doEstimateTime(self, elapsed):
        eta = set(master.estimateTime(elapsed) for master in self._masters)
        eta.discard(None)
        if eta:
            # first master stops, so take min
            return min(eta)
        return None

    def doInfo(self):
        ret = []
        for dev in self._masters:
            for key in self._presetkeys.keys():
                if self._presetkeys[key].name == dev.name:
                    if key.startswith('mon'):
                        ret.append(('mode', 'monitor', 'monitor', '',
                                    'presets'))
                        ret.append(('preset', dev.preselection,
                                    '%s' % dev.preselection, 'cts', 'presets'))
                    elif key.startswith('t'):
                        ret.append(('mode', 'time', 'time', '', 'presets'))
                        ret.append(('preset', dev.preselection,
                                    '%s' % dev.preselection, dev.unit,
                                    'presets'))
                    else:  # n, det, ctr, img
                        ret.append(('mode', 'counts', 'counts', '', 'presets'))
                        ret.append(('preset', dev.preselection,
                                    '%s' % dev.preselection, 'cts', 'presets'))
                    break
        return ret


class DetectorForecast(Readable):
    """Forecast device for a Detector.

    It returns a list of values that gives the estimated final values at the
    end of the current counting.
    """

    attached_devices = {
        'det': Attach('The detector to forecast values.', Detector),
    }

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
    }

    hardware_access = False

    def doRead(self, maxage=0):
        # read all values of all counters and store them by device
        counter_values = dict((ch, ch.read(maxage)[0])
                              for ch in self._attached_det._channels)
        # go through the master channels and determine the one
        # closest to the preselection
        fraction_complete = 0
        for m in self._attached_det._masters:
            p = m.preselection
            if p > 0:
                fraction_complete = max(fraction_complete,
                                        counter_values[m] / p)
        if fraction_complete == 0:
            # no master or all zero?  just return the current values
            fraction_complete = 1.0
        # scale all counter values by that fraction
        return [counter_values[ch] / fraction_complete
                for ch in self._attached_det._channels]

    def doStatus(self, maxage=0):
        return status.OK, ''

    def valueInfo(self):
        return self._attached_det.valueInfo()
