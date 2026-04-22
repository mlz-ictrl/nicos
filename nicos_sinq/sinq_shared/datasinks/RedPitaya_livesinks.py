# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Andrea Plank <andrea.plank@psi.ch>
#
# *****************************************************************************
import numpy as np

from time import time as currenttime
from nicos import session
from nicos.core.constants import LIVE
from nicos.devices.datasinks.special import LiveViewSink as BaseLiveViewSink, \
    LiveViewSinkHandler as BaseLiveViewSinkHandler
from nicos.utils import byteBuffer


class TofLiveViewSinkHandler(BaseLiveViewSinkHandler):
    def putResults(self, quality, results):
        databuffers = []
        datadescs = []
        result = results.get(self.detector.name)
        if result is None:
            return
        arrays = result[1]
        for i, dev in enumerate(self.detector._attached_images):
            data = arrays[i]
            if data is None:
                continue

            # X-Axis: TOF or Pulseheight
            channeltitle = dev.channel.replace('_',' ').upper()
            if dev.histtype == 'tof':
                x_title = f'{channeltitle} TOF Bin'
            else:
                x_title = f'{channeltitle} Pulse Height Bin'

            databuffers.append(byteBuffer(np.ascontiguousarray(data)))
            datadescs.append(dict(
                dtype = data.dtype.str,
                shape = data.shape,
                labels = {
                    'x': {
                        'define': 'range',
                        'title': x_title,
                        'start': 0,
                        'length': int(data.shape[0]),
                        'step': 1,
                    },
                    'y': {'define': 'classic', 'title': 'Counts'},
                },
                plotcount=1,
            ))

        parameters = dict(
            uid = self.dataset.uid,
            time = currenttime() - self.dataset.started,
            det = self.detector.name,
            tag = LIVE,
            datadescs = datadescs,
        )

        session.updateLiveData(parameters, databuffers)


class TofLiveViewSink(BaseLiveViewSink):
    handlerclass = TofLiveViewSinkHandler
