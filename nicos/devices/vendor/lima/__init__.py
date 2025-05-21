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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from nicos.devices.vendor.lima.andor2 import Andor2LimaCCD, \
    Andor2TemperatureController
from nicos.devices.vendor.lima.andor3 import Andor3LimaCCD, \
    Andor3TemperatureController
from nicos.devices.vendor.lima.generic import GenericLimaCCD, LimaCCDTimer
from nicos.devices.vendor.lima.zwo import ZwoTC
from nicos.devices.vendor.lima.eiger import EigerLimaCCD
