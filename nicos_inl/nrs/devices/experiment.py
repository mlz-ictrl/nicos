#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""NICOS INL NRS experiment classes."""

from nicos.core import Override
from nicos.devices.experiment import ImagingExperiment as BaseImagingExperiment
from nicos.utils import safeName


class ImagingExperiment(BaseImagingExperiment):
    """INL NRS specific imaging experiment which provides all imaging experiment
    functionalities plus all the INL NRS specific features.
    """

    parameter_overrides = {
        'dataroot': Override(default='/data'),
    }

    def newSample(self, parameters):
        name = parameters['name']
        self.sampledir = safeName(name)

        BaseImagingExperiment.newSample(self, parameters)

        self.log.debug('new sample path: %s', self.samplepath)
        self.log.debug('new data path: %s', self.datapath)
        self.log.debug('new dark image path: %s', self.darkimagedir)
        self.log.debug('new open beam image path: %s', self.openbeamdir)
        self.log.debug('new measurement image path: %s', self.photodir)
