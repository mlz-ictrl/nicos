#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""Device controlling watching over high voltage output."""

from nicos.core import Param
from nicos.devices.generic import ManualSwitch


class HVWatch(ManualSwitch):
    """Implements an on-off switch for a watchdog condition that checks the
    sample temperature against its setpoint, to avoid HV sparkover.
    """

    parameters = {
        'tdelta': Param('Maximum deviation of temperature from setpoint to '
                        'switch off high voltage', type=float, default=1.5),
    }
