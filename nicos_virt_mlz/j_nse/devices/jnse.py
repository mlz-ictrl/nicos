# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

from nicos.core import Override, Param
from nicos.devices.abstract import TransformedReadable
from nicos.devices.generic.virtual import VirtualMotor
from nicos_mlz.j_nse.devices.power import HasLabel
from nicos_mlz.stressi.devices.mixins import TransformRead


class JNSEVirtualMotor(HasLabel, VirtualMotor):
    """VirtualMotor that stores additional label."""

    parameters = {
        'voltage': Param(
            'Actual voltage',
            unit='V', fmtstr='%.3f', internal=True, type=float, settable=False,
            volatile=True, category='general',
        ),
    }

    def doReadVoltage(self):
        return (self.curvalue or 0.) * 0.1


class Integrator(TransformRead, TransformedReadable):
    """A device to integrate values over time.
    """

    parameter_overrides = {
        'unit': Override(volatile=False),
    }

    def doInit(self, mode):
        self._sum = 0

    def doRead(self, maxage=0):
        self._sum += TransformedReadable.doRead(self, maxage) * self.pollinterval
        return self._sum
