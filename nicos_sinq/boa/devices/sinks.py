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
#   Edward Wall <edward.wall@psi.ch>
#
# *****************************************************************************

"""Special Live view sink for BOA EMBL Detector."""

from time import time as currenttime

import numpy as np
import scipy.constants as scconst

from nicos import session
from nicos.core.constants import LIVE
from nicos.devices.datasinks.special import LiveViewSink as BaseLiveViewSink, \
    LiveViewSinkHandler as BaseLiveViewSinkHandler
from nicos.utils import byteBuffer


class HMLiveViewSinkHandler(BaseLiveViewSinkHandler):

    def __init__(self, sink, dataset, detector):
        BaseLiveViewSinkHandler.__init__(self, sink, dataset, detector)

    def prepare(self):
        BaseLiveViewSinkHandler.prepare(self)

        # Preallocates arrays used for Live Display

        self.wv_start, self.wv_step = self.apprxWavelength()
        x_length = session.getDevice('hm_b0_ax_x').length
        y_length = session.getDevice('hm_b0_ax_y').length
        tof_length = len(session.getDevice('hm_tof_array').data) - 1

        self.psd_buffer = np.empty((x_length, y_length), dtype='uint32')
        self.intensity_by_time_buffer = np.empty((tof_length, ), dtype='uint32')
        self.x_by_time_buffer = np.empty((x_length, tof_length), dtype='uint32')
        self.y_by_time_buffer = np.empty((y_length, tof_length), dtype='uint32')

    def apprxWavelength(self):
        hm_tof_array = session.getDevice('hm_tof_array')
        bin_start = hm_tof_array.start_delay * 100 * scconst.nano
        bin_width = hm_tof_array.channel_width * 100 * scconst.nano

        distance = session.getDevice('chopper_embl_distance').read(0)

        const = scconst.Planck / (scconst.neutron_mass * distance * scconst.angstrom)
        start = const * bin_start
        step = const * bin_width

        # The extra scaling, is because Nicos doesn't seem to be able to
        # display the values correctly when they are smaller than whole
        # numbers
        return (10 * start, 10 * step)

    def putResults(self, quality, results):
        result = results.get(self.detector.name)
        if result is None or result[1] is None or result[1][0] is None:
            return

        data = result[1][0]

        databuffers = []
        datadescs = []

        # Live View 1 - PSD
        np.sum(data, (2), out=self.psd_buffer)
        databuffers.append(byteBuffer(np.ascontiguousarray(
            np.rot90(np.flip(self.psd_buffer, axis=1))
        )))
        datadescs.append(dict(
            dtype=self.psd_buffer.dtype.str,
            shape=self.psd_buffer.shape,
            labels={
                       'x': {'define': 'classic', 'title': 'x'},
                       'y': {'define': 'classic', 'title': 'y'},
                   },
            plotcount=1
        ))

        # Live View 2 - TOF
        np.sum(data, (0, 1), out=self.intensity_by_time_buffer)
        databuffers.append(byteBuffer(np.ascontiguousarray(self.intensity_by_time_buffer)))
        datadescs.append(dict(
            dtype=self.intensity_by_time_buffer.dtype.str,
            shape=self.intensity_by_time_buffer.shape,
            labels={
                       'x': {
                           'define': 'range',
                           'title': '10 x Angstrom',
                           'start': self.wv_start,
                           'length': self.intensity_by_time_buffer.shape[0],
                           'step': self.wv_step
                        },
                       'y': {'define': 'classic', 'title': 'intensity'},
                   },
            plotcount=1,
        ))

        # Live View 3 - X by TOF
        np.sum(data, (1), out=self.x_by_time_buffer)
        databuffers.append(byteBuffer(np.ascontiguousarray(
            np.rot90(self.x_by_time_buffer)
        )))
        datadescs.append(dict(
            dtype=self.x_by_time_buffer.dtype.str,
            shape=(self.x_by_time_buffer.shape[1], self.x_by_time_buffer.shape[0]),
            labels={
                       'x': {
                           'define': 'range',
                           'title': 'x',
                           'start': 0,
                           'length': self.x_by_time_buffer.shape[0],
                           'step': 1
                        },
                       'y': {
                           'define': 'range',
                           'title': '10 x Angstrom',
                           'start': self.wv_start,
                           'length': self.x_by_time_buffer.shape[1],
                           'step': self.wv_step
                        },
                   },
            plotcount=1
        ))

        # Live View 4 - Y by TOF
        np.sum(data, (0), out=self.y_by_time_buffer)
        databuffers.append(byteBuffer(np.ascontiguousarray(self.y_by_time_buffer)))
        datadescs.append(dict(
            dtype=self.y_by_time_buffer.dtype.str,
            shape=self.y_by_time_buffer.shape,
            labels={
                       'x': {
                           'define': 'range',
                           'title': '10 x Angstrom',
                           'start': self.wv_start,
                           'length': self.y_by_time_buffer.shape[1],
                           'step': self.wv_step
                        },
                       'y': {
                           'define': 'range',
                           'title': 'y',
                           'start': 0,
                           'length': self.y_by_time_buffer.shape[0],
                           'step': 1
                        },
                   },
            plotcount=1
        ))

        parameters = dict(
            uid=self.dataset.uid,
            time=currenttime() - self.dataset.started,
            det=self.detector.name,
            tag=LIVE,
            datadescs=datadescs,
        )

        session.updateLiveData(parameters, databuffers)

class HMLiveViewSink(BaseLiveViewSink):
    handlerclass = HMLiveViewSinkHandler
