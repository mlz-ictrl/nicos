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

import csv

from nicos.core import Device, Param, listof
from nicos.core.utils import usermethod


class CalibrationData(Device):
    """
    This is a plain data holding class for calibration data.
    A little of this data is used internally, most of it is
    needed in order to be written to the datafile.
    """

    parameters = {
        'amplitude': Param('Amplitude', type=listof(float),
                           settable=True, default=[]),
        'energy': Param('Final analyser energy', type=listof(float),
                        settable=True, default=[]),
        'a4offset': Param('Offset in A4', type=listof(float),
                          settable=True, default=[]),
        'width': Param('width', type=listof(float),
                       settable=True, default=[]),
        'background': Param('Background', type=listof(float),
                            settable=True, default=[]),
        'boundaries': Param('Analyser boundaries', type=listof(int),
                            settable=True, default=[]),

    }

    @usermethod
    def load(self, filename):
        amp = []
        e = []
        off = []
        w = []
        bck = []
        bound = []
        with open(filename, 'r', encoding='utf-8') as fin:
            csvreader = csv.reader(fin)
            next(csvreader)
            next(csvreader)
            next(csvreader)
            for data in csvreader:
                amp.append(float(data[3]))
                e.append(float(data[4]))
                w.append(float(data[5]))
                bck.append(float(data[6]))
                bound.append(int(data[7]))
                bound.append(int(data[8]))
                off.append(float(data[9]))
        self.amplitude = amp
        self.energy = e
        self.a4offset = off
        self.background = bck
        self.width = w
        self.boundaries = bound
