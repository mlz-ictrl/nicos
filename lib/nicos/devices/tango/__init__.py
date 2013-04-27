#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""Package for TANGO device classes in NICOS."""

from nicos.devices.tango.core import TangoDevice
from nicos.devices.tango.frm2device import FRM2Device
from nicos.devices.tango.io import AnalogInput, AnalogOutput, DigitalInput, \
     NamedDigitalInput, PartialDigitalInput, DigitalOutput, \
     NamedDigitalOutput, PartialDigitalOutput, BitsDigitalOutput, \
     MultiDigitalOutput
from nicos.devices.tango.temperature import TemperatureSensor, TemperatureController
