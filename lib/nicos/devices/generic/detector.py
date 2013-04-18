#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Measurable, Readable, Param, Override, oneof, status


class Channel(Measurable):
    """Abstract base class for one channel of a counter card.

    Use one of the concrete classes `TimerChannel` or `CounterChannel`.
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

    def doStart(self, **preset):
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
    """Standard counter card-type detector using multiple channels."""

    attached_devices = {
        'timer':    (Channel, 'Timer channel'),
        'monitors': ([Channel], 'Monitor channels'),
        'counters': ([Channel], 'Counter channels')
    }

    hardware_access = False

    def doPreinit(self, mode):
        self._counters = []
        self._presetkeys = {}

        if self._adevs['timer'] is not None:
            self._counters.append(self._adevs['timer'])
            self._presetkeys['t'] = self._presetkeys['time'] = \
                self._adevs['timer']
        for i, mdev in enumerate(self._adevs['monitors']):
            self._counters.append(mdev)
            self._presetkeys['mon%d' % (i+1)] = mdev
        for i, cdev in enumerate(self._adevs['counters']):
            self._counters.append(cdev)
            self._presetkeys['det%d' % (i+1)] = \
                self._presetkeys['ctr%d' % (i+1)] = cdev
        self._getMasters()

    def doReadFmtstr(self):
        return ', '.join('%s %%s' % ctr.name for ctr in self._counters)

    def _getMasters(self):
        """Internal method to collect all masters from the card."""
        self._masters = []
        self._slaves = []
        for counter in self._counters:
            if counter.ismaster:
                self._masters.append(counter)
            else:
                self._slaves.append(counter)

    def doSetPreset(self, **preset):
        for master in self._masters:
            master.ismaster = False
            master.mode = 'normal'
        for name in preset:
            if name in self._presetkeys:
                dev = self._presetkeys[name]
                dev.ismaster = True
                dev.mode = 'preselection'
                dev.preselection = preset[name]
        self._getMasters()

    def doStart(self, **preset):
        self.doStop()
        if preset:
            self.doSetPreset(**preset)
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
        for master in self._masters:
            masterstatus = master.status(maxage)
            if masterstatus[0] == status.BUSY:
                return masterstatus
        return status.OK, 'idle'

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
        'det':  (MultiChannelDetector, 'The detector to forecast values.'),
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
            fraction_complete = max(fraction_complete, counter_values[m] / p)
        # scale all counter values by that fraction
        return [counter_values[ctr] / fraction_complete
                for ctr in self._adevs['det']._counters]

    def doStatus(self, maxage=0):
        return status.OK, ''

    def valueInfo(self):
        return self._adevs['det'].valueInfo()
