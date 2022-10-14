#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
#
# *****************************************************************************

from nicos.core.device import Readable
from nicos.core.errors import ConfigurationError
from nicos.core.params import Attach


class CollimatorLoverD(Readable):
    attached_devices = {
        'l': Attach('Distance device', Readable),
        'd': Attach('Pinhole', Readable),
    }

    def doInit(self, mode):
        if self._attached_l.unit != self._attached_d.unit:
            raise ConfigurationError(self, 'different units for L and d (%s vs %s)' % (
                self._attached_l.unit, self._attached_d.unit))

    def doRead(self, maxage=0):
        try:
            Zpinhole = 4200
            v = int(self._attached_d.read(maxage))
            h = int(self._attached_d.read(maxage))
            if self._attached_d.read(maxage) == '62':
                Zpinhole = 2540
            elif 'x' in self._attached_d.read(maxage):
                v, h = self._attached_d.read(maxage).split('x')
            ret = [(int(self._attached_l.read(maxage)) - Zpinhole) / int(v),
                   (int(self._attached_l.read(maxage)) - Zpinhole) / int(h)]
        except ValueError:
            ret = [0, 0]
        return ret
