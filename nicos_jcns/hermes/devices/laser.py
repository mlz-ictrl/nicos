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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

from nicos.devices.entangle import Motor as EntangleMotor


class Motor(EntangleMotor):
    """Custom motor device for the HERMES laser whose encoder value does not
    change. To still get reasonable (mapped) values, the limit switch status is
    checked instead."""

    def doRead(self, maxage=0):
        """Check the limit switch status and return the corresponding target
        value, if one of them is active. Otherwise, the encoder value is
        returned.
        """
        status = self.doStatus(maxage)
        for ls, ls_target in (('-', self.abslimits[0]),
                              ('+', self.abslimits[1])):
            if ls in status[1]:
                return ls_target
        return EntangleMotor.doRead(self, maxage)
