#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos.core import Param

from nicos_sinq.devices.sinqhm.channel import HistogramImageChannel


class AmorSingleDetectorImageChannel(HistogramImageChannel):
    """ The three single detectors in AMOR write the data on second
    bank in the histogram memory with each row representing the TOF
    data from a particular detector
    """
    parameters = {
        'detectorid': Param('ID of the single detector', type=int),
    }

    def _dimDesc(self):
        desc = HistogramImageChannel._dimDesc(self)
        return [desc[1]]

    @property
    def startid(self):
        return self.detectorid * self.bank.shape[1]

    @property
    def endid(self):
        return (self.detectorid + 1) * self.bank.shape[1]

    @property
    def shape(self):
        return [self.bank.shape[1]]
