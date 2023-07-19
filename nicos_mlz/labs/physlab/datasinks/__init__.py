# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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

"""Live sink for XRESD instrument."""

import numpy as np

from nicos.devices.datasinks.special import LiveViewSink as BaseLiveViewSink, \
    LiveViewSinkHandler as BaseLiveViewSinkHandler


class LiveViewSinkHandler(BaseLiveViewSinkHandler):
    """Data live view handler."""

    def getLabelArrays(self, result):
        ds = self.dataset
        radius = ds.metainfo.get(('ysd', 'value'), [201.9])[0]
        pixel_count = ds.metainfo.get(('image', 'pixel_count'), [1280])[0]
        pixel_size = ds.metainfo.get(('image', 'pixel_size'), [0.05])[0]
        ttheta = ds.metainfo.get(('tths', 'value'), [0])[0]
        step = pixel_size / radius
        ttheta_range = ttheta + np.rad2deg(
            np.arctan((np.arange(0, pixel_count) - pixel_count / 2 + 0.5) * step))
        self.log.debug('start: %s, end: %s', ttheta_range[0], ttheta_range[-1])
        return [ttheta_range]

    def getLabelDescs(self, result):
        return {
            'x': {
                'title': '2θ [deg]',
                'define': 'array',
                'dtype': 'float64',
                'index': 0,
            },
        }


class LiveViewSink(BaseLiveViewSink):
    """Data live view sink."""

    handlerclass = LiveViewSinkHandler
