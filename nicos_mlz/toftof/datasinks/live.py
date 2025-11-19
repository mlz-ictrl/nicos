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

"""TOFTOF special Live view sink for NICOS."""

import numpy as np

from nicos.devices.datasinks.special import LiveViewSink as BaseLiveViewSink, \
    LiveViewSinkHandler as BaseLiveViewSinkHandler

from nicos_mlz.toftof.lib import calculations as calc


class LiveViewSinkHandler(BaseLiveViewSinkHandler):

    def processArrays(self, result):
        data = result[1][0]
        if data is not None:
            if len(data.shape) == 2:
                treated = np.transpose(data)[
                    self.detector._anglemap, :].astype('<u4')
                return [treated]

    def getLabelDescs(self, result):
        metainfo = self.dataset.metainfo

        # Scale factor to calc the right unit
        sf = 1e3
        wl = metainfo['chWL', 'value'][0]
        timeinterval = metainfo['det', 'timeinterval'][0] * sf
        nChannels = metainfo['det', 'timechannels'][0]
        # The first interval is [tof, tof + timeinterval)
        tof = timeinterval + calc.t2(0, wl, calc.Lsd) * sf
        y_classic = {
            'define': 'classic',
            'title': 'detectors',
        }
        x_tof = {
            'define': 'range',
            'title': 'time of flight (ms)',
            'start': tof,
            'length': nChannels,
            'step': timeinterval,
        }

        return {
            'x': x_tof,
            'y': y_classic,
        }


class LiveViewSink(BaseLiveViewSink):
    """A data sink that sends images to attached clients for live preview."""

    handlerclass = LiveViewSinkHandler
