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
#    Artur Glavic <artur.glavic@psi.ch>
# *****************************************************************************

from nicos.core import Attach, Value
from nicos.devices.generic.detector import RectROIChannel

from nicos_sinq.devices.just_bin_it import JustBinItImage


class CutROI(RectROIChannel):
    """
    A class which cuts a ROI out of another image for a single counter, roi is user changable.
    """

    attached_devices = {
        'raw_image': Attach('image to cut data from', devclass=JustBinItImage),
    }

    def getReadResult(self, _arrays, _results, _quality):
        raw_data = self._attached_raw_image.doReadArray(None)
        if any(self.roi):
            x, y, w, h = self.roi
            return [float(raw_data[y:y+h, x:x+w].sum())]
        return [0.]


    def valueInfo(self):
        return Value(self.name, type='counter', unit=self.unit),
