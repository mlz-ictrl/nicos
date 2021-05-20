#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Attach

from nicos_ess.devices.datasinks.imagesink.histogramdesc import \
    HistogramDimDesc
from nicos_sinq.devices.sinqhm.channel import ReshapeHistogramImageChannel
from nicos_sinq.devices.sinqhm.configurator import HistogramConfAxis


class StroboHistogramImageChannel(ReshapeHistogramImageChannel):
    """
    This fixes up the raw HM data in stroboscopic and TOF modes
    """

    attached_devices = {
        'tof_axis': Attach('TOF axis to account for',
                           HistogramConfAxis),
    }

    @property
    def shape(self):
        return tuple(self.dimensions.values()) + (
            self._attached_tof_axis.length,)

    def _dimDesc(self):
        res = ReshapeHistogramImageChannel._dimDesc(self)
        res.append(
            HistogramDimDesc(self._attached_tof_axis.length, 'strobo', ''))
        return res
