#  -*- coding: utf-8 -*-
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Generic 0-D channel detector classes for NICOS."""

from nicos.core import Measurable, Readable, Param, Override, oneof, status, \
    Attach, ProgrammingError


class Channel(Measurable):
    """Abstract base class for one channel of a counter card.

    Concrete implementations for TACO counter cards can be found in
    `nicos.devices.taco.detector`.
    Concrete implementations for QMesyDAQ counters can be found in
    `nicos.devices.vendor.qmesydaq`.
    """

    parameters = {
        'mode':         Param('Channel mode: normal, ratemeter, or preselection',
                              type=oneof('normal', 'ratemeter', 'preselection'),
                              default='preselection', settable=True),
        'ismaster':     Param('If this channel is a master', type=bool,
                              settable=True),
        'preselection': Param('Preselection for this channel', settable=True),
    }

    # methods to be implemented in concrete subclasses

    def doSetPreset(self, **preset):
        raise ProgrammingError(self, 'Channel.setPreset should not be called')

    def doStart(self):
        pass

    def doStop(self):
        pass

    def doRead(self, maxage=0):
        return 0

    def doStatus(self, maxage=0):
        return status.OK, 'idle'

    def doIsCompleted(self):
        return True


class MultiChannelDetector(Measurable):
    """Standard counter type detector using multiple synchronized channels."""

    attached_devices = {
        'timer':    Attach('Timer channel', Channel, optional=True),
        'monitors': Attach('Monitor channels', Channel, multiple=True, optional=True),
        'counters': Attach('Counter channels', Channel, multiple=True, optional=True)
    }

    hardware_access = False
    multi_master = True

    # allow overwriting in derived classes
    def _presetiter(self):
        """yields name, device tuples for all 'preset-able' devices"""
        # a device may react to more than one presetkey....
        dev = self._adevs['timer']
        if dev:
            yield ('t', dev)
            yield ('time', dev)
        for i, dev in enumerate(self._adevs['monitors']):
            yield ('mon%d' % (i+1), dev)
        for i, dev in enumerate(self._adevs['counters']):
            if i == 0:
                yield ('n', dev)
            yield ('ctr%d' % (i+1), dev)
            yield ('det%d' % (i+1), dev)
        for dev in self._adevs['monitors'] + self._adevs['counters']:
            yield (dev.name, dev)

    def doPreinit(self, mode):
        _counters = []
        _presetkeys = {}
        for name, dev in self._presetiter():
            if dev not in _counters:
                _counters.append(dev)
            # later mentioned presetnames dont overwrite earlier ones
            _presetkeys.setdefault(name, dev)
        self._counters = _counters
        self._presetkeys = _presetkeys
        self._getMasters()

    def doReadFmtstr(self):
        return ', '.join('%s %%s' % ctr.name for ctr in self._counters)

    def _getMasters(self):
        """Internal method to collect all masters."""
        _masters = []
        _slaves = []
        for counter in self._counters:
            if counter.ismaster:
                _masters.append(counter)
            else:
                _slaves.append(counter)
        self._masters = _masters
        self._slaves = _slaves

    def doSetPreset(self, **preset):
        self.doStop()
        if not preset:
            # keep old settings
            return
        for master in self._masters:
            master.ismaster = False
            master.mode = 'normal'
        master = None
        for name in preset:
            if name in self._presetkeys:
                if master:
                    self.log.error('Only one Master is supported, ignoring '
                                   'preset %s=%s'%(name, preset[name]))
                    continue
                dev = self._presetkeys[name]
                dev.ismaster = True
                dev.mode = 'preselection'
                dev.preselection = preset[name]
                if not self.multi_master:
                    master = dev
        if not (self.multi_master or master):
            self.log.warning('No usable preset given, '
                             'detector may not stop by itself!')
        self._getMasters()

    def doStart(self):
        self.doStop()
        for slave in self._slaves:
            slave.start()
        for master in self._masters:
            master.start()

    def doPause(self):
        for master in self._masters:
            master.doPause()
        return True

    def doResume(self):
        for master in self._masters:
            master.doResume()

    def doStop(self):
        for master in self._masters:
            master.stop()

    def doRead(self, maxage=0):
        return sum((ctr.read() for ctr in self._counters), [])

    def doStatus(self, maxage=0):
        self._getMasters()
        if not self._masters:
            return status.OK, 'idle'
        for master in self._masters:
            masterstatus = master.status(maxage)
            if masterstatus[0] == status.OK:
                return masterstatus
        return status.BUSY, 'counting'

    def doIsCompleted(self):
        for master in self._masters:
            if master.isCompleted():
                return True
        if not self._masters:
            return True
        return False

    def doReset(self):
        for counter in self._counters:
            counter.reset()

    def valueInfo(self):
        return sum((ctr.valueInfo() for ctr in self._counters), ())

    def presetInfo(self):
        return set(self._presetkeys)


class DetectorForecast(Readable):
    """Forecast device for a MultiChannelDetector.

    It returns a list of values that gives the estimated final values at the end
    of the current counting.
    """

    attached_devices = {
        'det':  Attach('The detector to forecast values.', MultiChannelDetector),
    }

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
    }

    hardware_access = False

    def doRead(self, maxage=0):
        # read all values of all counters and store them by device
        counter_values = dict((c, c.read(maxage)[0])
                              for c in self._adevs['det']._counters)
        # go through the master channels and determine the one
        # closest to the preselection
        fraction_complete = 0
        for m in self._adevs['det']._masters:
            p = m.preselection
            if p > 0:
                fraction_complete = max(fraction_complete, counter_values[m] / p)
        if fraction_complete == 0:
            # no master or all zero?  just return the current values
            fraction_complete = 1.0
        # scale all counter values by that fraction
        return [counter_values[ctr] / fraction_complete
                for ctr in self._adevs['det']._counters]

    def doStatus(self, maxage=0):
        return status.OK, ''

    def valueInfo(self):
        return self._adevs['det'].valueInfo()
