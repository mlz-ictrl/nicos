#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Special device related to the L over d relation."""

from nicos.core.device import Readable
from nicos.core.errors import ConfigurationError
from nicos.core.params import Attach, Override


class CollimatorLoverD(Readable):
    """Special device related to the L over d relation."""

    attached_devices = {
        'l': Attach('Distance device', Readable),
        'd': Attach('Pinhole', Readable),
    }

    def doInit(self, mode):
        if self._attached_l.unit != self._attached_d.unit:
            raise ConfigurationError(self, 'different units for L and d '
                                     '(%s vs %s)' %
                                     (self._attached_l.unit,
                                      self._attached_d.unit))

    def doRead(self, maxage=0):
        try:
            ret = float(self._attached_l.read(maxage)) / \
                float(self._attached_d.read(maxage))
        except ValueError:
            ret = 0
        return ret


class GeometricBlur(Readable):
    """Special device to calculate geometric blur.

    Calculated from collimation and sample to detector distance."""

    attached_devices = {
        'l': Attach('Distance device', Readable),
        'd': Attach('Pinhole', Readable),
        'sdd': Attach('Sample Detector Distance', Readable),
    }

    parameter_overrides = {
        'unit': Override(volatile=True, mandatory=False),
    }

    def doInit(self, mode):
        units = set(d.unit for d in self._adevs.values())
        if len(units) != 1:
            raise ConfigurationError(self, 'different units for L, d and sdd '
                                     '(%s vs %s vs %s)' %
                                     (self._attached_l.unit,
                                      self._attached_d.unit,
                                      self._attached_sdd.unit))
        if 'mm' not in units:
            raise ConfigurationError(self, "attached devices units have to be "
                                     "'mm'")

    def doRead(self, maxage=0):
        try:
            ret = float(self._attached_sdd.read(maxage)) * \
                float(self._attached_d.read(maxage)) / \
                float(self._attached_l.read(maxage))
            return 1000 * ret  # convert to um
        except ValueError:
            ret = 0
        return ret

    def doReadUnit(self):
        return 'um'
