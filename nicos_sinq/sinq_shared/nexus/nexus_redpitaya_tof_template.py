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

import copy

from nicos.nexus.elements import DeviceDataset, NamedImageDataset
from nicos.nexus.nexussink import NexusTemplateProvider

redpitaya_tof_nexus_template_base = {
    'data':  NamedImageDataset('analog_ch0_tof'),

    'chopper_to_detector_distance': DeviceDataset(
        'chopper_to_detector_distance', dtype='int32'),

    'ttl_ch0_tof:NXdata': {
        'data': NamedImageDataset('ttl_ch0_tof'),
        'nbins': DeviceDataset('ttl_ch0_tof', 'nbins', dtype = 'int32'),
        'binsize': DeviceDataset('ttl_ch0_tof', 'binsize', dtype = 'int32'),
    },

    'analog_ch0_tof:NXdata': {
        'data': NamedImageDataset('analog_ch0_tof'),
        'nbins': DeviceDataset('analog_ch0_tof', 'nbins', dtype = 'int32'),
        'binsize': DeviceDataset('analog_ch0_tof', 'binsize', dtype = 'int32'),
    },

    'analog_ch1_tof:NXdata': {
        'data': NamedImageDataset('analog_ch1_tof'),
        'nbins': DeviceDataset('analog_ch1_tof', 'nbins', dtype = 'int32'),
        'binsize': DeviceDataset('analog_ch1_tof', 'binsize', dtype = 'int32'),
    },

    'analog_ch0_ph:NXdata': {
        'data': NamedImageDataset('analog_ch0_ph'),
        'nbins': DeviceDataset('analog_ch0_ph', 'nbins', dtype = 'int32'),
    },

    'analog_ch1_ph:NXdata': {
        'data': NamedImageDataset('analog_ch1_ph'),
        'nbins': DeviceDataset('analog_ch1_ph', 'nbins', dtype = 'int32'),
    }
}


class RedPitayaTOFTemplateProvider(NexusTemplateProvider):
    # Nexus template provider for TOF Measurement with RedPitaya at SINQ
    def getTemplate(self):
        redpitaya_tof_template = copy.deepcopy(redpitaya_tof_nexus_template_base)
        return redpitaya_tof_template
