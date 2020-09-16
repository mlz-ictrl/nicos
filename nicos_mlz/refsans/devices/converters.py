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
#   Matthias Pomm <matthias.pomm@hzg.de> 2018-08-06 11:18:31
#
# *****************************************************************************

from nicos.core import Override, Readable
from nicos.core.params import Attach

from nicos_mlz.stressi.devices.mixins import TransformRead


class Ttr(Readable):
    attached_devices = {
        'att': Attach('center', Readable),
    }

    unitconvs = {
        'mbar': 6.143,
        'ubar': 2.287,
        'torr': 6.304,
        'mtorr': 2.448,
        'micron': 2.448,
        'Pa': 3.572,
        'kPa': 7.429,
    }

    def doRead(self, maxage=0):
        c = self.unitconvs.get(self.unit, 0.0)
        return 10**((self._attached_att.read(maxage) - c)/1.286)


class LinearKorr(TransformRead, Readable):
    parameter_overrides = {
        'unit': Override(volatile=False),
    }
