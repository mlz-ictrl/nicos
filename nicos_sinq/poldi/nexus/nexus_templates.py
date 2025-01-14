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
#   Alexander Söderqvist <alexander.soederqvist@psi.ch>
#
# *****************************************************************************
import copy

from nicos.nexus.elements import DetectorDataset, DeviceAttribute, \
    DeviceDataset, EndTime, NXAttribute, StartTime, ConstDataset, \
    NamedImageDataset
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_sinq.nexus.specialelements import SaveSampleEnv

poldi_base = {
    'NeXus_Version': '4.3.3',
    'instrument': 'POLDI',
    'owner': DeviceAttribute('POLDI', 'responsible'),
    'owner_address': DeviceAttribute('POLDI', 'facility'),
    'entry1:NXentry': {
        'POLDI:NXinstrument': {
            'SINQ:NXsource': {
                'name': 'SINQ',
                'type': 'Continuous flux spallation source'
                },
            'chopper:NXchopper': {
                'name': ConstDataset('Dornier Chopper', 'string'),
                'rotation_speed': DeviceDataset('ch_speed_rbv'),
                'rotation_speed_target': DeviceDataset('ch_speed'),
                # Do we want more chopper parameters
                },
            'collimator_1:NXcollimator': {
                'y_position': DeviceDataset('ctl1'),
                'x_position': DeviceDataset('ctu1'),
                'rotation_angle': DeviceDataset('cr1'),
            },
            'detector_south:NXdetector': {
                "histogram": NamedImageDataset('det_south_hist'),
                "histogram_folded": NamedImageDataset('det_south_hist_folded'),
                "summed_counts": DetectorDataset(
                    'det_south_hist', dtype='uint32',
                    units=NXAttribute('counts', 'string')),
            },
            'diaphragm1:NXaperture': {
                'distance': ConstDataset(
                    8000.0, 'float32', units=NXAttribute("mm", "string")),
                'left': DeviceDataset('d1hl'),
                'left_zero': DeviceDataset('d1hl', 'offset', 'float32'),
                'right': DeviceDataset('d1hr'),
                'right_zero': DeviceDataset('d1hr', 'offset', 'float32'),
                },
            'diaphragm2:NXaperture': {
                'distance':  ConstDataset(
                    2200.0, 'float32', units=NXAttribute("mm", "string")),
                'left': DeviceDataset('d2hl'),
                'left_zero': DeviceDataset('d2hl', 'offset', 'float32'),
                'right': DeviceDataset('d2hr'),
                'right_zero': DeviceDataset('d2hr', 'offset', 'float32'),
                'lower': DeviceDataset('d2vl'),
                'lower_zero': DeviceDataset('d2vl', 'offset', 'float32'),
                'upper': DeviceDataset('d2vu'),
                'upper_zero': DeviceDataset('d2vu', 'offset', 'float32'),
                'z_position': DeviceDataset('d2x'),
                'z_position_null': DeviceDataset('d2x', 'offset', 'float32'),
                },
            'name': 'POLDI'

        },
        'title':
            DeviceDataset('Exp', 'title'),
        'user:NXuser': {
            'name': DeviceDataset('Exp', 'users'),
            'email': DeviceDataset('Exp', 'localcontact')
        },
        'proposal_title':
            DeviceDataset('Exp', 'title'),
        'proposal_id':
            DeviceDataset('Exp', 'proposal'),
        'start_time':
            StartTime(),
        'end_time':
            EndTime(),
        "comment": DeviceDataset("Exp", "remark"),
        'monitors:NXmonitor': {
            'monitor1_before_chopper':
                DetectorDataset('monitor3',
                                'float32',
                                units=NXAttribute('counts', 'string')),
            'monitor2_after_chopper':
                DetectorDataset('monitor2',
                                'float32',
                                units=NXAttribute('counts', 'string')),
            'monitor3_before_sample':
                DetectorDataset('monitor1',
                                'float32',
                                units=NXAttribute('counts', 'string')),
            'monitor4_proton_beam':
                DetectorDataset('protoncount',
                                'float32',
                                units=NXAttribute('counts', 'string')),
        },
        'start_time_unix': StartTime(),
        'experiment_identifier': DeviceDataset('Exp', 'Proposal')
    }
}

poldi_sample = {
    "name": DeviceDataset("Sample", "samplename"),
    "environment": SaveSampleEnv(),
    "sa": DeviceDataset('sa'),
    'sa_zero': DeviceDataset('sa', 'offset', 'float32'),
    "shl": DeviceDataset('shl'),
    'shl_zero': DeviceDataset('shl', 'offset', 'float32'),
    "shu": DeviceDataset('shu'),
    'shu_zero': DeviceDataset('shu', 'offset', 'float32'),
    "sv": DeviceDataset('sv'),
    'sv_zero': DeviceDataset('sv', 'offset', 'float32'),
}


class POLDITemplateProvider(NexusTemplateProvider):
    """
      NeXus template generation for POLDI at SINQ
    """

    def getTemplate(self):
        poldi_template = copy.deepcopy(poldi_base)
        poldi_template['entry1:NXentry']['sample:NXsample'] = \
            copy.deepcopy(poldi_sample)
        return poldi_template
