# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos.core.device import Attach, Readable

from nicos_sinq.devices.epics.extensions import EpicsCommandReply


class EulerPresent(Readable):
    """
    This is a highly specific little class which reads the
    connection status of the eulerian cradle from the ZEBRA MCU
    """
    attached_devices = {
        'mcu': Attach('The direct connection to the MCU from which to read '
                      'the presence of the eulerian cradle',
                      EpicsCommandReply)
    }

    def doRead(self, maxage=0):
        try:
            return int(self._attached_mcu.execute('M298'))
        except Exception:
            return 0
