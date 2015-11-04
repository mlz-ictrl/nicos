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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Package for TACO device classes in NICOS."""

from nicos.devices.taco.axis import Axis, HoveringAxis
from nicos.devices.taco.coder import Coder
from nicos.devices.taco.core import TacoDevice
from nicos.devices.taco.detector import FRMChannel, FRMTimerChannel, \
     FRMCounterChannel
from nicos.devices.taco.io import AnalogInput, AnalogOutput, DigitalInput, \
     NamedDigitalInput, PartialDigitalInput, DigitalOutput, \
     NamedDigitalOutput, PartialDigitalOutput, BitsDigitalOutput, \
     MultiDigitalOutput
from nicos.devices.taco.motor import Motor
from nicos.devices.taco.power import Supply, CurrentSupply, VoltageSupply
from nicos.devices.taco.temperature import TemperatureSensor, TemperatureController
