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

import numpy as np

from nicos import session
from nicos.core import Attach, Device, Param, Value, listof
from nicos.core.errors import ConfigurationError
from nicos.core.utils import usermethod
from nicos.devices.generic.detector import ImageChannelMixin, PassiveChannel

from nicos_ess.devices.datasinks.imagesink.histogramdesc import \
    HistogramDesc, HistogramDimDesc
from nicos_sinq.devices.detector import ControlDetector
from nicos_sinq.devices.sinqhm.configurator import HistogramConfArray


class FocusDetector(ControlDetector):
    """
    FOCUS has up to four detector banks on different histogram memories which
    may be active or not active depending on the loaded setups. The main job
    of coordinating all these detectors is done by ControlDetector. This class
    adds discovery of the dynamic configuration
    """

    _banks = {'middle', 'lower', 'upper', 'f2d'}

    @usermethod
    def find_slaves(self):
        found_slaves = []
        for b in self._banks:
            try:
                slave = session.getDevice(b + '_detector')
                found_slaves.append(slave)
            except ConfigurationError:
                pass
        self._attached_slave_detectors = found_slaves


class Focus2DArray(HistogramConfArray):
    """
    This is the lookup array for the FOCUs 2D detector. The lookup
    data lives in a data file. This just copies the content of this file
    verbatim minus the first line as the dataText
    """
    parameters = {
        'lookup_file': Param('Path to file containing the 2D lookup data',
                             type=str),
    }

    def setData(self, dim, data):
        pass

    def dataText(self):
        with open(self.lookup_file, 'r') as fin:
            lookup = fin.readlines()
        return ''.join(lookup[1:])


class MergedImageChannel(ImageChannelMixin, PassiveChannel):
    """
    FOCUS has three main detector banks. But the most useful data is the
    merged data from the three banks. This merged data will be calculated
    by this class.
    """
    parameters = {
        'mergefile': Param('file which contains the instructions for merging',
                           type=str),
    }

    attached_devices = {
        'tof': Attach('TOF array for the length of the data',
                      HistogramConfArray)
    }

    _idx_upper = None
    _idx_middle = None
    _idx_lower = None

    def doInit(self, mode):
        with open(self.mergefile, 'r') as fin:
            fin.readline()  # skip first line
            line = fin.readline()
            merged_length = int(line)
            self._idx_upper = np.zeros((merged_length,), dtype=int)
            self._idx_middle = np.zeros((merged_length,), dtype=int)
            self._idx_lower = np.zeros((merged_length,), dtype=int)
            for i in range(merged_length):
                line = fin.readline()
                data = line.split()
                self._idx_upper[i] = int(data[2])
                self._idx_middle[i] = int(data[3])
                self._idx_lower[i] = int(data[4])

    def doReadArray(self, quality):
        banks = ['middle', 'upper', 'lower']
        data = []
        for b in banks:
            try:
                im = session.getDevice(b + '_image')
                raw = im.readArray(quality)
                data.append(np.reshape(raw, im.shape))
            except ConfigurationError:
                return None  # No merged data when not enough banks
        result = np.zeros((len(self._idx_middle), data[0].shape[1]))
        for i in range(len(self._idx_middle)):
            div = 0
            merged_row = np.zeros((data[0].shape[1],))
            if self._idx_middle[i] > 0:
                merged_row += data[0][self._idx_middle[i]-1]
                div += 1
            if self._idx_upper[i] > 0:
                merged_row += data[1][self._idx_upper[i]-1]
                div += 1
            if self._idx_lower[i] > 0:
                merged_row += data[2][self._idx_lower[i]-1]
                div += 1
            if div > 1:
                merged_row /= div
            result[i] = merged_row
        self.readresult = [result.sum()]
        return result

    @property
    def arraydesc(self):
        merged_length = len(self._idx_middle)
        tof_length = len(self._attached_tof.data) - 1
        return HistogramDesc(self.name, 'uint32', [
            HistogramDimDesc(merged_length, 'detector-id', ''),
            HistogramDimDesc(tof_length, 'time_binning', '')
        ])

    def shape(self):
        merged_length = len(self._idx_middle)
        tof_length = len(self._attached_tof.data) - 1
        return merged_length, tof_length

    def valueInfo(self):
        return [Value(self.name, type='counter', unit=self.unit)]


class Focus2DData(Device):
    """
    This is class which holds some auxiliary data for storing the
    2D detector data in the NeXus file. It is mainly here to keep
    some parameters such that they are loaded from the cache
    rather then have to load them at each invocation of NICOS
    """

    parameters = {
        'xdim': Param('x Dimension of the 2D detector',
                      type=int, settable=True,
                      userparam=False),
        'ydim': Param('y Dimension of the 2D detector',
                      type=int, settable=True,
                      userparam=False),
        'xval': Param('X coordinate for each pixel',
                      type=listof(float), unit='mm', settable=True,
                      userparam=False),
        'yval': Param('Y coordinate for each pixel',
                      type=listof(float), unit='mm', settable=True,
                      userparam=False),
        'distval': Param('Sample distance for each pixel',
                         type=listof(float), unit='mm', settable=True,
                         userparam=False),
        'eqval': Param('Equatorial angle for each pixel for each pixel',
                       type=listof(float), unit='deg', settable=True,
                       userparam=False),
        'azval': Param('Azimuthal angle for each pixel',
                       type=listof(float), unit='deg', settable=True,
                       userparam=False),
        'tthval': Param('2 Theta angle for each pixel',
                        type=listof(float), settable=True,
                        userparam=False),
    }
