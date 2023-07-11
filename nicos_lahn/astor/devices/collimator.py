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
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
#
# *****************************************************************************

from nicos_mlz.antares.devices.collimator import \
    CollimatorLoverD as BaseCollimatorLoverD


class CollimatorLoverD(BaseCollimatorLoverD):

    def doRead(self, maxage=0):
        l = int(self._attached_l.read(maxage))
        Zpinhole = 4200
        try:
            d = int(self._attached_d.read(maxage))
            if d == 62:
                Zpinhole = 2540
            return [ (l - Zpinhole) / d ] * 2
        except ValueError:
            r = self._attached_d.read(maxage)
            if 'x' in r:
                return [ (l - Zpinhole) / int(x) for x in r.split('x') ]
        return [ 0 ] * 2
