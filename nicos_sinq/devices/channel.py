#  -*- Coding: utf-8 -*-
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
# Module authors:
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos.core import ArrayDesc, Attach, Param, Value
from nicos.devices.generic import ImageChannelMixin, PassiveChannel


class SelectSliceImageChannel(ImageChannelMixin, PassiveChannel):
    """This channel extracts a slice of data from a 3D data array"""

    parameters = {
        'slice_no': Param('Index of the slice to select',
                          type=int, settable=True, default=0),
    }

    attached_devices = {
        'data_channel': Attach('Image data from which to extract the slice',
                               ImageChannelMixin)
    }

    @property
    def arraydesc(self):
        datadesc = self._attached_data_channel.arraydesc
        return ArrayDesc(self.name,
                         [datadesc.shape[0], datadesc.shape[1]],
                         'uint32', ['x', 'y'])

    def doReadArray(self, quality):
        data = self._attached_data_channel.readArray(quality)
        if len(data.shape) < 3:
            return data
        zdim = data.shape[2]
        self.slice_no = max(self.slice_no, 0)
        self.slice_no = min(self.slice_no, zdim-1)
        sl = data[self.slice_no]
        self.readresult = [sl.sum(), ]
        return sl

    def valueInfo(self):
        return [Value(self.name, type='counter', unit=self.unit)]
