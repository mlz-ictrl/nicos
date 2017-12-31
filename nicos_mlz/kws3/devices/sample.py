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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""KWS-3 sample position switcher."""

from nicos import session
from nicos.core import Moveable, Attach, Param, Override, oneof, dictof, \
    listof, anytype, DeviceAlias, NicosError, ConfigurationError, HasPrecision
from nicos.devices.generic import Slit
from nicos.utils import num_sort
from nicos.pycompat import iteritems


class SamplePos(Moveable):
    """Control selector speed via SPS I/O devices."""

    attached_devices = {
        'active_ap': Attach('Alias for active aperture', DeviceAlias),
        'active_x':  Attach('Alias for active x translation', DeviceAlias),
        'active_y':  Attach('Alias for active y translation', DeviceAlias),
    }

    parameters = {
        'alloweddevs': Param('List of allowed devices for presets',
                             type=listof(str)),
        'presets':     Param('Presets for sample position switching',
                             type=dictof(str, dictof(str, anytype))),
    }

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
    }

    def doInit(self, mode):
        self.valuetype = oneof(*sorted(self.presets, key=num_sort))
        self._waitdevs = []
        self._aliases = {}
        self._devpos = {}
        for setting, values in iteritems(self.presets):
            values = dict(values)
            try:
                self._aliases[setting] = (values.pop('active_ap'),
                                          values.pop('active_x'),
                                          values.pop('active_y'))
            except KeyError:
                raise ConfigurationError(self, 'setting %r needs active_ap, '
                                         'active_x and active_y settings' %
                                         setting)
            try:
                for name in self._aliases[setting]:
                    session.getDevice(name)
            except NicosError:
                raise ConfigurationError(self, 'could not create/find alias '
                                         'targets for setting %r' % setting)
            for key in values:
                if key not in self.alloweddevs:
                    raise ConfigurationError(self, 'device %s is not allowed '
                                             'to be moved by sample_pos' % key)
            self._devpos[setting] = values

    def doRead(self, maxage=0):
        current_targets = (
            self._attached_active_ap.alias,
            self._attached_active_x.alias,
            self._attached_active_y.alias,
        )
        setting = None
        for setting, targets in iteritems(self._aliases):
            if targets == current_targets:
                break
        else:
            return 'unknown'
        ok = True
        for devname, devpos in iteritems(self._devpos[setting]):
            dev = session.getDevice(devname)
            devval = dev.read(maxage)
            if isinstance(dev, HasPrecision):
                ok &= abs(devval - devpos) <= dev.precision
            elif isinstance(dev, Slit):
                ok &= all(abs(v - w) <= 0.1 for (v, w) in zip(devval, devpos))
            else:
                ok &= devval == devpos
        if ok:
            return setting
        return 'unknown'

    def doStart(self, target):
        aliases = self._aliases[target]
        self._attached_active_ap.alias = aliases[0]
        self._attached_active_x.alias = aliases[1]
        self._attached_active_y.alias = aliases[2]
        self._waitdevs = []
        for dev, devpos in iteritems(self._devpos[target]):
            dev = session.getDevice(dev)
            dev.move(devpos)
            self._waitdevs.append(dev)

    def _getWaiters(self):
        if self._waitdevs:
            return self._waitdevs
        return self._adevs
