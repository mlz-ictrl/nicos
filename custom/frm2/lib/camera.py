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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Support classes for neutron cameras at the FRM II."""

from nicos.devices.tango import ImageChannel


class CameraImage(ImageChannel):
    """Tango ImageChannel subclass that waits for the channel's status
    (for CCD readout) before reading the image.
    """

    def doReadArray(self, quality):
        # need to wait for readout of the CCD
        self._hw_wait()
        value = ImageChannel.doReadArray(self, quality)

        # due to dimension order expectations in the current image savers
        rs = tuple(self._dev.roiSize)
        return value.ravel().reshape((rs[1], rs[0]))
