# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special device for Sans1 High Voltage supply"""


from nicos.core import Override, Param, status
from nicos.devices.entangle import PowerSupply


class VoltageSupply(PowerSupply):
    """work around a bug either in the Tango server or in the hv supply itself

    basically the idle status is returned at the end of the ramp,
    even if the output voltage is nowhere near the target value
    """
    parameters = {
        '_stopflag': Param('Supply was stopped',
                           type=bool, settable=True, mandatory=False,
                           internal=True, default=False),
    }

    parameter_overrides = {
        'timeout':   Override(default=90),
        'precision': Override(volatile=True),
    }

    _last_st = status.OK, ''

    def timeoutAction(self):
        if self.target is not None:
            self.log.warning('Timeout! retrying once to reach %s',
                             self.format(self.target, unit=True))
            # start() would clear timeoutActionCalled Flag
            self.start(self.target)

    def doStart(self, target):
        self._stopflag = False
        PowerSupply.doStart(self, target)

    def doStatus(self, maxage=0):
        # suppress intermittent tripped messages
        st = PowerSupply.doStatus(self, maxage)
        if st[0] == status.ERROR and 'trip' in st[1]:
            if 'trip' not in self._last_st[1]:
                st = (status.WARN, st[1])
        self._last_st = st
        return st

    def doStop(self):
        self._stopflag = True
        PowerSupply.doStop(self)
        self.wait()
        PowerSupply.doStart(self, self.read(0))
        self.wait()

    def doReset(self):
        self._stopflag = False
        self._dev.Reset()

    def doReadPrecision(self):
        if self.target == 1:
            return 69
        return 3
