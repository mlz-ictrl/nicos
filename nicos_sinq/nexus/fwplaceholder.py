#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
# This file contains SINQ specific placeholders for the kafka-to-nexus
# streaming NeXus filewriter. The rest of the files in this package
# deal with the h5py based direct NeXus file writer
#
# Module authors:
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
from nicos_ess.nexus.placeholder import DeviceValuePlaceholder, PlaceholderBase


class DevArrayPlaceholder(PlaceholderBase):
    """
    This Placeholder generates an array from the value of a device, a step size
    and the length of the array. A good example use case is the two theta array
    for a powder diffractometer where the detector can be moved.
    """
    def __init__(self, component, step, length):
        self.component = component
        self.step = step
        self.length = length

    def fetch_info(self, metainfo):
        start = DeviceValuePlaceholder(self.component).fetch_info(metainfo)[0]
        val = []
        for i in range(self.length):
            val.append(start + i * self.step)
        return val, '', 'degree', 'general'
