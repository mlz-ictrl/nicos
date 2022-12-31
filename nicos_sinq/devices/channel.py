#  -*- Coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

from time import time as currenttime

from nicos.core import ArrayDesc, Attach, HasPrecision, Moveable, Override, \
    Param, Readable, Value, status
from nicos.devices.generic import ActiveChannel, ImageChannelMixin, \
    PassiveChannel
from nicos.utils import lazy_property


class SelectSliceImageChannel(ImageChannelMixin, PassiveChannel):
    """This channel extracts a slice of data from a 3D data array"""

    parameters = {
        'slice_no': Param('Index of the slice to select',
                          type=int, settable=True, default=0),
    }

    attached_devices = {
        'data_channel': Attach('Image data from which to extract the slice',
                               ImageChannelMixin)
    }

    @property
    def arraydesc(self):
        datadesc = self._attached_data_channel.arraydesc
        return ArrayDesc(self.name,
                         [datadesc.shape[0], datadesc.shape[1]],
                         'uint32', ['x', 'y'])

    def doReadArray(self, quality):
        data = self._attached_data_channel.readArray(quality)
        if len(data.shape) < 3:
            return data
        zdim = data.shape[2]
        self.slice_no = max(self.slice_no, 0)
        self.slice_no = min(self.slice_no, zdim-1)
        sl = data[self.slice_no]
        self.readresult = [sl.sum(), ]
        return sl

    def valueInfo(self):
        return [Value(self.name, type='counter', unit=self.unit)]


class ReadableToChannel(HasPrecision, ActiveChannel):
    """
    Allow to use a generic device (e.g. sample environment) as an Active
    channel.
    """

    attached_devices = {'dev': Attach('Device to use as a counter', Readable)}

    parameters = {
        'window': Param('Time window for which the value has to be within '
                        'precision', type=int, mandatory=False, settable=True)}

    parameter_overrides = {
        'visibility': Override(default=()),
    }

    def doPreinit(self, mode):
        self._preselection_reached = True

    def doRead(self, maxage=0):
        return self._attached_dev.doRead()

    def doStart(self):
        if not self._preselection_reached and isinstance(self._attached_dev,
                                                         Moveable):
            self._attached_dev.start(self.preselection)

    def doFinish(self):
        self._preselection_reached = True

    def doStop(self):
        self._attached_dev.stop()
        self.doFinish()

    @lazy_property
    def _history(self):
        if self._cache:
            self._cache.addCallback(self, 'value', self._cacheCB)
            self._subscriptions.append(('value', self._cacheCB))
            t = currenttime()
            return self._cache.history(self, 'value', t - self.window, t)
        return []

    # use values determined by poller or waitForCompletion loop
    # to fill our history
    def _cacheCB(self, key, value, time):
        self._history.append((time, value))
        # clean out stale values, if more than one
        stale = None
        for i, entry in enumerate(self._history):
            t, _ = entry
            if t >= time - self.window:
                stale = i
                break
        else:
            return
        # remove oldest entries, but keep one stale
        if stale > 1:
            del self._history[:stale - 1]

    def doStatus(self, maxage=0):
        vals = [v for t, v in self._history[:]]
        stable = all(
            abs(v - self.preselection) <= self.precision for v in vals)
        if stable or self._preselection_reached:
            return status.OK, 'Done'
        return status.BUSY, 'target not reached'

    def setChannelPreset(self, name, value):
        self._preselection_reached = False
        ActiveChannel.setChannelPreset(self, name, value)

    def valueInfo(self):
        return Value('%s' % self, type='other', unit=self._attached_dev.unit,
                     fmtstr=self._attached_dev.fmtstr, errors='none'),
