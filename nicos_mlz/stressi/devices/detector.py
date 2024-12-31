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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from nicos.core.params import Param, tupleof
from nicos.devices.vendor.qmesydaq.tango import \
    ImageChannel as BaseImageChannel


class ImageChannel(BaseImageChannel):

    parameters = {
        'pixel_size': Param('Size of a single pixel (in mm)',
                            type=tupleof(float, float), volatile=False,
                            settable=False, default=(0.85, 0.85), unit='mm',
                            category='instrument'),
        'pixel_count': Param('Number of detector pixels',
                             type=int, volatile=True, settable=False,
                             category='instrument'),
    }

    def doReadPixel_Count(self):
        if self.arraydesc:
            return self.arraydesc.shape[0]
        return self._dev.detectorSize[0]
