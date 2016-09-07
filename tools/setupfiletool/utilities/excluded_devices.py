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
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************

excluded_device_classes = [
    'devices.abstract.Coder',
    'devices.abstract.Motor',
    'devices.abstract.Axis',
    'devices.abstract.MappedReadable',
    'devices.abstract.MappedMoveable',
    'core.device.Readable',
    'core.device.Moveable',
    'core.device.Measurable',
    'devices.vendor.simplecomm.SimpleCommReadable',
    'devices.vendor.simplecomm.SimpleCommMoveable'
]
