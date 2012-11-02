#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from FRM2DeviceClient import FRM2DeviceClient

from nicos.devices.tango.core import TangoDevice

from nicos.core.device import Device
from nicos.core.device import usermethod

__version__ = "$Revision$"

class FRM2Device(TangoDevice, Device):
    tango_class = FRM2DeviceClient

    def doVersion(self):
        rawVersion = self._tango_guard(self._dev.version)
        versionList = rawVersion.split('\n')

        result = []

        for entry in versionList:
            splittedVersion = entry.strip().partition(' ')
            result.append((splittedVersion[0], splittedVersion[2].strip('()')))

        return result

    @usermethod
    def getErrorCode(self):
        return self._tango_guard(self._dev.errorCode)

    @usermethod
    def getErrorString(self):
        return self._tango_guard(self._dev.errorString)

