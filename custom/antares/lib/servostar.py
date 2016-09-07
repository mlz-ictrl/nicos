#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

'''Class to use the Servostar-Motors'''

import TACOStates
from nicos.core import status
from nicos.devices.taco import Motor as TacoMotor


# Just redefine doStatus as this doesn't work correctly with the
# ServoStarTacoServer
class ServoStarMotor(TacoMotor):
    """
    This device handles the DISABLED taco state thats given from the servostar
    server when the hardware is idle.
    """

    _TACO_STATUS_MAPPING = dict(TacoMotor._TACO_STATUS_MAPPING)
    _TACO_STATUS_MAPPING[TACOStates.DISABLED] = status.OK
