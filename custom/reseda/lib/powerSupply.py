#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Aleks Wischolit <aleks.wischolit@frm2.tum.de>
#
# *****************************************************************************

"""Readout of FUG power supplies."""

#import time

from IO import StringIO

from nicos.core import Readable, Override, status, Param, NicosError
from nicos.devices.taco.core import TacoDevice


class PowerSupplyU(TacoDevice, Readable):

    taco_class = StringIO

    parameters = {
        'channel': Param('channel of the power supply', type=int,
                         mandatory=True),
    }

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='V'),
    }

    def doRead(self, maxage=0):
        # INST:SEL 1;MEAS:VOLT?
        # INST:SEL 2;MEAS:VOLT?
        tmp = int (self._taco_guard(self._dev.communicate,'INST:NSEL?'))
        if tmp != self.channel:
            raise NicosError(self, 'wrong channel selected')
            #self._taco_guard(self._dev.writeLine, 'INST:NSEL %d' %
            #                 (self.channel))
            #time.sleep(0.05)
        tmp = self._taco_guard(self._dev.communicate,'MEAS:VOLT?')
        return float (tmp)

    def doStatus(self, maxage=0):
        return status.OK, ''



class PowerSupplyA(TacoDevice, Readable):

    taco_class = StringIO

    parameters = {
        'channel': Param('channel of the power supply', type=int,
                         mandatory=True),
    }

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='A'),
    }

    def doRead(self, maxage=0):
        tmp = int(self._taco_guard(self._dev.communicate,'INST:NSEL?'))
        if tmp != self.channel:
            raise NicosError(self, 'wrong channel selected')
            #self._taco_guard(self._dev.writeLine, 'INST:NSEL %d' %
            #                 (self.channel))
            #time.sleep(0.05)
        tmp = self._taco_guard(self._dev.communicate,'MEAS:CURR?')
        return float (tmp)

    def doStatus(self, maxage=0):
        return status.OK, ''
