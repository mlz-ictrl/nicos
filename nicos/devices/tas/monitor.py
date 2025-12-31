# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""TAS specific detector devices."""

from scipy.interpolate import interp1d

from nicos.core import Attach, Param, Value, dictof
from nicos.devices.generic import PostprocessPassiveChannel
from nicos.devices.tas.spectro import Wavevector


class OrderCorrectedMonitor(PostprocessPassiveChannel):
    """Monitor corrected for higher-order influence.

    For more information have a look
    `here. <https://forge.frm2.tum.de/redmine/attachments/download/1067/monitor%20correction%20new.pdf>`_
    """

    hardware_access = False

    parameters = {
        'mapping': Param('Interpolation mapping between ki and correction '
                         'factor',
                         type=dictof(float, float), mandatory=False),
    }

    attached_devices = {
        'ki': Attach('Incoming wavevector (ki)', Wavevector),
    }

    def doInit(self, mode):
        # PostprocessPassiveChannel.doInit(self, mode)
        self._interp = interp1d(list(self.mapping.keys()),
                                list(self.mapping.values()), kind='cubic')

    def getReadResult(self, _arrays, results, _quality):
        factor = self._interp(self._attached_ki.read())
        return [v / factor for v in results]

    def valueInfo(self):
        if len(self.readresult) > 1:
            return tuple(Value(name='%s[%d]' % (self.name, i + 1),
                               type='monitor', fmtstr='%d')
                         for i in range(len(self.readresult)))
        return (Value(name=self.name, type='monitor', fmtstr='%d'), )
