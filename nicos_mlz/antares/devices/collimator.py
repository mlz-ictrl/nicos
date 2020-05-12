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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Special device related to the L over d relation."""

from __future__ import absolute_import, division, print_function

from nicos.core.device import Readable
from nicos.core.errors import ConfigurationError
from nicos.core.params import Attach


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
