#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""HV power supply for HV sample stick."""

import time

from IO import StringIO

from nicos.core import status, Moveable, HasLimits, Override, CommunicationError
from nicos.devices.taco.core import TacoDevice


class HVViaHPE(TacoDevice, HasLimits, Moveable):
    """
    Device object for a FUG HV supply via external input HPE3631.
    """
    taco_class = StringIO

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='kV'),
    }

    def doInit(self, mode):
        idn = self._taco_guard(self._dev.communicate, '*IDN?')
        if 'HEWLETT-PACKARD' not in idn:
            raise CommunicationError(self, 'strange model for HPE: %r' % idn)

    def doRead(self, maxage=0):
        self._taco_guard(self._dev.writeLine, 'INSTRUMENT:NSELECT 2')
        time.sleep(1)
        return float(self._taco_guard(self._dev.communicate, 'VOLT?'))

    def doStatus(self, maxage=0):
        return status.OK, 'idle'

    def doStart(self, value):
        self._taco_guard(self._dev.writeLine, 'INSTRUMENT:NSELECT 2')
        time.sleep(1)
        self._taco_guard(self._dev.writeLine, 'VOLT %f' % value)
