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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Generic detector and channel classes for NICOS."""

from __future__ import absolute_import, division, print_function

import numpy

from nicos import session
from nicos.core import INTERMEDIATE, LIVE, Attach, DeviceMixinBase, \
    Measurable, Moveable, Override, Param, Readable, SubscanMeasurable, \
    UsageError, Value, anytype, listof, multiStatus, none_or, oneof, \
    status, tupleof
from nicos.core.constants import FINAL
from nicos.core.errors import ConfigurationError
from nicos.core.scan import Scan
from nicos.core.utils import multiWait
from nicos.pycompat import iteritems
from nicos.utils import uniq


class PassiveChannel(Measurable):
    """Abstract base class for one channel of a aggregate detector.

    See the `Detector` documentation for an overview of channel types, and
    the difference between passive and active channels.

    Derived classes have to implement `doRead` and `valueInfo` methods.
    They can return an empty list and tuple, respectively, if the channel
    contributes no scalar values but one or more arrays, e.g. classes
    derived from `ImageChannelMixin`.
    """

    parameters = {
        'ismaster':      Param('If this channel is an active master',
                               type=bool, settable=True),
        'presetaliases': Param('Aliases for setting a preset for the first '
                               'scalar on this channel',
                               type=listof(str)),
    }

    # preset handling is slightly different in the Detector

    def doSetPreset(self, **preset):
        raise UsageError(self, 'This channel cannot be used as a detector')

    # methods that can be overridden

    _presetmap = None

    def presetInfo(self):
        """Return the preset keys that this channel supports.

        The default implementation returns all time/monitor/counter/other
        value names from `self.valueInfo()`, with '.' replaced by '_' to
        form valid identifiers.

        It also adds entries from `self.presetaliases`.
        """
        if self._presetmap is not None:
            return set(self._presetmap)
        self._presetmap = {}
        for (i, value) in enumerate(self.valueInfo()):
            if value.type in ('counter', 'monitor', 'time', 'other'):
                self._presetmap[value.name.replace('.', '_')] = i
        if self._presetmap:
            for alias in self.presetaliases:
                self._presetmap[alias] = 0
        return set(self._presetmap)

    def setChannelPreset(self, name, value):
        """Set a preset for this channel.

        This can be ignored by passive channels since soft presets are checked
        explicitly.
        """
        self.ismaster = True

    def presetReached(self, name, value, maxage):
        """Return true if the soft preset for *name* has reached the given
        *value*.
        """
        if name in self._presetmap:
            return self.read(maxage)[self._presetmap[name]] >= value
        return False

    # methods to be implemented in concrete subclasses

    def doStart(self):
        pass

    def doFinish(self):
        pass

    def doStop(self):
        pass

    def doRead(self, maxage=0):
        raise NotImplementedError('implement doRead')

    def valueInfo(self):
        raise NotImplementedError('implement valueInfo')

    def doStatus(self, maxage=0):
        return status.OK, 'idle'


class DummyDetector(PassiveChannel):
    """A Dummy detector just providing name and value info.

    Still needs to implement doRead!

    Use for scans that add only processed values from subscans.
    """

    parameter_overrides = {
        'unit':   Override(default='cts'),
        'fmtstr': Override(default='%.2f'),
    }

    def valueInfo(self):
        return Value(self.name, unit=self.unit, type='other', fmtstr=self.fmtstr),


class ActiveChannel(PassiveChannel):
    """Abstract base class for channels that can (but don't need to) end the
    measurement on their own.  See the documentation for `Detector` for an
    overview of channel types.
    """

    parameters = {
        'preselection': Param('Preset value for this channel', type=float,
                              settable=True),
    }

    # set to True to get a simplified doEstimateTime
    is_timer = False

    def setChannelPreset(self, name, value):
        PassiveChannel.setChannelPreset(self, name, value)
        self.preselection = value

    def presetReached(self, name, value, maxage):
        return self.status(maxage)[0] == status.OK

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


class PostprocessPassiveChannel(PassiveChannel):
    """Base class for postprocessing `arrays` and `results`."""

    parameters = {
        'readresult': Param('Storage for scalar results from image '
                            'filtering, to be returned from doRead()',
                            type=listof(float), settable=True,
                            internal=True),
    }

    def doRead(self, maxage=0):
        return self.readresult

    def doPause(self):
        return True

    def getReadResult(self, arrays, results, quality):
        """This method should return the new `readresult` for corresponding
        `arrays` and `results` in respect to a given `quality`."""
        raise NotImplementedError('implement getReadResult')

    def setReadResult(self, arrays, results, quality):
        """This method sets the new `readresult` which is returned in
        ``getReadResult``."""
        self.readresult = self.getReadResult(arrays, results, quality)


class RectROIChannel(PostprocessPassiveChannel):
    """Calculates counts for a rectangular region of interest."""

    parameters = {
        'roi': Param('Rectangular region of interest (x, y, width, height)',
                     tupleof(int, int, int, int),
                     settable=True, category='general'),
    }

    parameter_overrides = {
        'unit':   Override(default='cts'),
        'fmtstr': Override(default='%d'),
    }

    def getReadResult(self, arrays, _results, _quality):
        if any(self.roi):
            x, y, w, h = self.roi
            return [arr[y:y+h, x:x+w].sum() for arr in arrays]
        return [arr.sum() for arr in arrays]

    def valueInfo(self):
        if len(self.readresult) > 1:
            return tuple(Value(name=self.name + '[%d]' % i, type='counter',
                               fmtstr='%d')
                         for i in range(1, len(self.readresult) + 1))
        return Value(name=self.name, type='counter', fmtstr='%d'),


class RateChannel(PostprocessPassiveChannel):
    """Calculate total counts and rate on `arrays` assuming `results[0]` is a
    timer."""

    parameter_overrides = {
        'unit':   Override(default=''),
        'fmtstr': Override(default='%d cts (%.1f cps)'),
    }

    _cts_seconds = None

    def getReadResult(self, arrays, results, quality):
        if self._cts_seconds is None:
            self._cts_seconds = (len(arrays) + 1) * [0]
        # assuming results[0] is a timer
        seconds = results[0][0]

        result = []
        if seconds > 1e-9:
            if quality in (FINAL, INTERMEDIATE) or seconds <= \
                    self._cts_seconds[-1]:
                # rate for full detector / time
                for i, arr in enumerate(arrays):
                    cts = arr.sum()
                    result.append(cts)
                    result.append(cts / seconds)
                    self._cts_seconds[i] = cts
            else:  # live rate on detector (using deltas)
                for i, arr in enumerate(arrays):
                    cts = arr.sum()
                    result.append(cts)
                    result.append((cts - self._cts_seconds[i]) / (
                        seconds - self._cts_seconds[-1]))
                    self._cts_seconds[i] = cts
            self._cts_seconds[-1] = seconds
            return result
        return (2 * len(arrays)) * [0]

    def valueInfo(self):
        if self.readresult and len(self.readresult) > 2:
            infos = []
            for i in range(1, len(self.readresult) // 2  + 1):
                name = self.name + '[%d]' % i
                infos.extend([
                    Value(name=name + ' (total)', type='counter', fmtstr='%d',
                          errors='sqrt', unit='cts'),
                    Value(name=name + ' (rate)', type='monitor', fmtstr='%.1f',
                          unit='cps'),
                ])
            return tuple(infos)
        return (
            Value(name=self.name + ' (total)', type='counter', fmtstr='%d',
                  errors='sqrt', unit='cts'),
            Value(name=self.name + ' (rate)', type='monitor', fmtstr='%.1f',
                  unit='cps'),
        )


class RateRectROIChannel(RateChannel, RectROIChannel):
    """Calculate total counts and rate in a rectangular region of interest."""

    def getReadResult(self, arrays, results, quality):
        rs = RectROIChannel.getReadResult(self, arrays, results, quality)
        return RateChannel.getReadResult(self, [numpy.asarray([res]) for res
                                                in rs], results, quality)


class TimerChannelMixin(DeviceMixinBase):
    """Mixin for channels that return measured time."""

    is_timer = True

    parameter_overrides = {
        'unit':   Override(default='s'),
        'fmtstr': Override(default='%.2f'),
    }

    def valueInfo(self):
        return Value(self.name, unit=self.unit, type='time',
                     fmtstr=self.fmtstr),

    def doTime(self, preset):
        if self.ismaster:
            return self.preselection
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
                      type=oneof('monitor', 'counter', 'other'), mandatory=True),
    }

    parameter_overrides = {
        'unit':         Override(default='cts'),
        'fmtstr':       Override(default='%d'),
        'preselection': Override(type=int),
    }

    def valueInfo(self):
        return Value(self.name, unit=self.unit, errors='sqrt',
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
                            internal=True),
    }

    parameter_overrides = {
        'unit':         Override(default='cts'),
        'fmtstr':       Override(default='%d'),
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
        if self._sim_intercept:
            if self.arraydesc:
                return numpy.zeros(self.arraydesc.shape)
            return numpy.zeros(1)
        return self.doReadArray(quality)

    def doReadArray(self, quality):
        raise NotImplementedError('implement doReadArray in %s' %
                                  self.__class__.__name__)


class Detector(Measurable):
    """Detector using multiple (synchronized) channels.

    Each channel can have a "preset" set, which means that measurement stops if
    the channel's value (or an element thereof, for channels with multiple
    read values) has reached the preset value.

    Passive channels can only stop the measurement via soft presets (presets
    that are checked by NICOS) during the countloop and therefore may be
    overshot by some nontrivial amount.  In contrast, the derived
    `ActiveChannel` is able to stop by itself, usually implemented in hardware,
    so that the preset is reached exactly, or overshot by very little.

    In the detector, channels with a preset are called "masters", while
    channels without are called "slaves".  Which channels are masters and
    slaves can change with every count cycle.
    """

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
        'postprocess':   Param('Post processing list containing tuples of '
                               '(PostprocessPassiveChannel, '
                               'ImageChannelMixin or PassiveChannel, ...)',
                               type=listof(tuple)),
    }

    parameter_overrides = {
        'fmtstr': Override(volatile=True),
    }

    hardware_access = False
    multi_master = True

    _last_live = 0
    _last_save = 0
    _last_save_index = 0
    _last_preset = None
    _user_comment = ''

    def doInit(self, _mode):
        self._masters = []
        self._slaves = []
        self._channel_presets = {}
        self._postprocess = []
        self._postpassives = []

        for tup in self.postprocess:
            if tup[0] not in session.configured_devices:
                self.log.warning("device %r not found but configured in "
                                 "'postprocess' parameter. No "
                                 "post processing for this device. Please "
                                 "check the detector setup.", tup[0])
                continue
            postdev = session.getDevice(tup[0])
            img_or_passive_devs = [session.getDevice(name) for name in tup[1:]]
            if not isinstance(postdev, PostprocessPassiveChannel):
                raise ConfigurationError("Device '%s' is not a "
                                         "PostprocessPassiveChannel" %
                                         postdev.name)
            if postdev not in self._channels:
                raise ConfigurationError("Device '%s' has not been configured "
                                         "for this detector" % postdev.name)
            for dev in img_or_passive_devs:
                if dev not in self._channels:
                    raise ConfigurationError("Device '%s' has not been "
                                             "configured for this detector" %
                                             dev.name)
                elif isinstance(dev, PassiveChannel):
                    self._postpassives.append(dev)
            self._postprocess.append((postdev, img_or_passive_devs))

    # allow overwriting in derived classes
    def _presetiter(self):
        """Yield (name, device, type) tuples for all 'preset-able' devices."""
        # a device may react to more than one presetkey....
        for i, dev in enumerate(self._attached_timers):
            if i == 0:
                yield ('t', dev, 'time')
            for preset in dev.presetInfo():
                yield (preset, dev, 'time')
        for dev in self._attached_monitors:
            for preset in dev.presetInfo():
                yield (preset, dev, 'monitor')
        for i, dev in enumerate(self._attached_counters):
            if i == 0:
                yield ('n', dev, 'counts')
            for preset in dev.presetInfo():
                yield (preset, dev, 'counts')
        for dev in self._attached_images + self._attached_others:
            for preset in dev.presetInfo():
                yield (preset, dev, 'counts')
        yield ('live', None, None)

    def doPreinit(self, mode):
        presetkeys = {}
        for name, dev, typ in self._presetiter():
            # later mentioned presetnames dont overwrite earlier ones
            presetkeys.setdefault(name, (dev, typ))
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

    def _getPreset(self, preset):
        """Returns previous preset if no preset has been set."""
        if not preset and self._last_preset:
            return self._last_preset
        if 'live' not in preset:
            # do not store live as previous preset
            self._last_preset = preset
        return preset

    def doSetPreset(self, **preset):
        self._user_comment = preset.pop('info', '')
        preset = self._getPreset(preset)
        if not preset:
            # keep old settings
            return
        for master in self._masters:
            master.ismaster = False
        self._channel_presets = {}
        for (name, value) in iteritems(preset):
            if name in self._presetkeys and name != 'live':
                dev = self._presetkeys[name][0]
                dev.setChannelPreset(name, value)
                self._channel_presets.setdefault(dev, []).append((name, value))
        self._getMasters()
        if set(self._masters) != set(self._channel_presets):
            if not self._masters:
                self.log.warning('no master configured, detector may not stop')
            else:
                self.log.warning('master setting for devices %s ignored by '
                                 'detector',
                                 ', '.join(set(self._channel_presets) -
                                           set(self._masters)))
        self.log.debug("   presets: %s", preset)
        self.log.debug("presetkeys: %s", self._presetkeys)
        self.log.debug("   masters: %s", self._masters)
        self.log.debug("    slaves: %s", self._slaves)

    def doPrepare(self):
        for slave in self._slaves:
            slave.prepare()
        for master in self._masters:
            master.prepare()

    def doStart(self):
        # setting this to -interval, instead of 0, will send some live data at
        # the very start of each count, clearing the "live" data from last time
        self._last_live = -(self.liveinterval or 0)
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
        success = True
        for slave in self._slaves:
            success &= slave.pause()
        for master in self._masters:
            success &= master.pause()
        return success

    def doResume(self):
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
        arrays = [img.readArray(quality) for img in self._attached_images]
        results = [dev.read(0) for dev in self._postpassives]
        for postdev, img_or_passive_devs in self._postprocess:
            postarrays, postresults = [], []
            for dev in img_or_passive_devs:
                if isinstance(dev, ImageChannelMixin):
                    postarrays.append(arrays[self._attached_images.index(dev)])
                else:  # PassiveChannel
                    postresults.append(results[self._postpassives.index(dev)])
            postdev.setReadResult(postarrays, postresults, quality)
        return arrays

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
        st, text = multiStatus(self._getWaiters(), maxage)
        if st == status.ERROR:
            return st, text
        for master in self._masters:
            for (name, value) in self._channel_presets.get(master, ()):
                if master.presetReached(name, value, maxage):
                    return status.OK, text
        return st, text

    def doReset(self):
        for ch in self._channels:
            ch.reset()

    def valueInfo(self):
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
        return {'info'} | set(self._presetkeys)

    def doEstimateTime(self, elapsed):
        eta = {master.estimateTime(elapsed) for master in self._masters}
        eta.discard(None)
        if eta:
            # first master stops, so take min
            return min(eta)
        return None

    def doInfo(self):
        ret = []
        if self._user_comment:
            ret.append(('usercomment', self._user_comment, self._user_comment,
                        '', 'general'))
        presets = []
        for (_dev, devpresets) in iteritems(self._channel_presets):
            for (key, value) in devpresets:
                presets.append((self._presetkeys[key][1], value))
        if len(presets) > 1:
            mode = ' or '.join(p[0] for p in presets)
            ret.append(('mode', mode, mode, '', 'presets'))
            for (mode, value) in presets:
                ret.append(('preset_%s' % mode,
                            value, str(value), '', 'presets'))
        elif presets:
            mode, value = presets[0]
            return ret + [('mode', mode, mode, '', 'presets'),
                          ('preset', value, str(value), '', 'presets')]
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
        counter_values = {ch: ch.read(maxage)[0]
                          for ch in self._attached_det._channels}
        # go through the master channels and determine the one
        # closest to the preselection
        fraction_complete = 0
        for m in self._attached_det._masters:
            p = float(m.preselection)
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


class GatedDetector(Detector):
    """A Detector which enables some 'gates' before the measurment
    and disables them afterwards
    """

    attached_devices = {
        'gates':   Attach('Gating devices', Moveable,
                          multiple=True, optional=True),
    }

    parameters = {
        'enablevalues':  Param('List of values to enable the gates',
                               type=listof(anytype), default=[]),
        'disablevalues': Param('List of values to disable the gates',
                               type=listof(anytype), default=[]),
    }

    def _enable_gates(self):
        self.log.debug('enabling gates')
        for dev, val in zip(self._attached_gates, self.enablevalues):
            dev.move(val)
        multiWait(self._attached_gates)
        self.log.debug('gates enabled')

    def _disable_gates(self):
        self.log.debug('disabling gates')
        for dev, val in zip(reversed(self._attached_gates),
                            reversed(self.disablevalues)):
            dev.move(val)
        multiWait(self._attached_gates)
        self.log.debug('gates disabled')

    def doStart(self):
        self._enable_gates()
        Detector.doStart(self)

    def doResume(self):
        # check first gate to see if we need to (re-)enable them
        if self._attached_gates[0].read(0) != self.enablevalues[0]:
            self._enable_gates()
        Detector.doResume(self)

    def doPause(self):
        res = Detector.doPause(self)
        if res:
            self._disable_gates()
        return res

    def doStop(self):
        Detector.doStop(self)
        self._disable_gates()

    def doFinish(self):
        Detector.doFinish(self)
        self._disable_gates()


class ScanningDetector(SubscanMeasurable):
    """Generic "super" detector that scans over a configured device and counts
    with a given detector."""

    attached_devices = {
        'scandev':  Attach('Current device to scan', Moveable),
        'detector': Attach('Detector to scan', Measurable),
    }

    parameters = {
        'positions': Param('Positions to scan over', type=listof(anytype)),
        'readresult': Param('Storage for processed results from detector, to'
                            'be returned from doRead()', type=listof(anytype),
                            settable=True, internal=True),
    }

    def doInit(self, mode):
        self._preset = None

    def doSetPreset(self, **preset):
        self._preset = preset

    def doStart(self):
        positions = [[p] for p in self.positions]
        self.readresult = self._processDataset(Scan(
            [self._attached_scandev],
            positions, None, detlist=[self._attached_detector],
            preset=self._preset, subscan=True).run())

    def valueInfo(self):
        if self.readresult:
            raise NotImplementedError('Result processing implemented, but '
                                      'valueInfo missing')
        return ()

    def doRead(self, maxage=0):
        return self.readresult

    def doFinish(self):
        pass

    def _processDataset(self, dataset):
        return []  # implement in subclass if necessary
