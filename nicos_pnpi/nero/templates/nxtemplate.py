#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   Kirill Pshenichnyi <pshcyrill@mail.ru>
#
# *****************************************************************************

""" Nexus template for NERO machine """

from nicos.nexus.elements import DetectorDataset, DeviceAttribute, \
    DeviceDataset, ImageDataset
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_mlz.toftof.devices.datasinks.elements import EndTime, StartTime
from nicos_pnpi.nero.devices.datasinks.elements import FileName


class NxTemplateCount(NexusTemplateProvider):

    def getTemplate(self):
        template = {
            'NeXus_Version': 'nexusformat v0.5.3',
            'instrument': DeviceAttribute('Instrument', 'instrument'),
            'owner': DeviceAttribute('Instrument', 'responsible'),
            'users': DeviceAttribute('Exp', 'users'),
            'entry:NXentry': {
                'start_time': StartTime(),
                'end_time': EndTime(),
                'FileName': FileName(),
                'data:NXdata': {
                    'data': ImageDataset(0, 0),
                    'units': DeviceAttribute('det1_img', 'unit'),
                },
                'NERO:NXinstrument': {
                    'collimator:NXcollimator': {
                        'width': DeviceDataset('col.width',
                                               dtype='float32',
                                               ),
                        'height': DeviceDataset('col.height',
                                                dtype='float32',
                                                ),
                        'theta_s': DeviceDataset('theta_s',
                                                 dtype='float32',
                                                 ),
                        'x_s': DeviceDataset('x_s',
                                             dtype='float32',
                                             ),
                        'dia1_angle': DeviceDataset('dia1_angle',
                                                    dtype='float32',
                                                    ),
                        'dia1_pos': DeviceDataset('dia1_pos',
                                                  dtype='float32',
                                                  ),
                        'dia2_angle': DeviceDataset('dia2_angle',
                                                    dtype='float32',
                                                    ),
                        'dia2_pos': DeviceDataset('dia2_pos',
                                                  dtype='float32',
                                                  ),
                        'fa': DeviceDataset('fa'),
                        'fb': DeviceDataset('fb'),
                    },
                    'monochromator:NXcrystal': {
                        'chi1': DeviceDataset('chi1',
                                              dtype='float32',
                                              ),
                        'chi2': DeviceDataset('chi2',
                                              dtype='float32',
                                              ),
                        'chi3': DeviceDataset('chi3',
                                              dtype='float32',
                                              ),
                        'chi4': DeviceDataset('chi4',
                                              dtype='float32',
                                              ),
                        'omega': DeviceDataset('omega',
                                               dtype='float32',
                                               ),
                        'x': DeviceDataset('x_mon',
                                           dtype='float32',
                                           ),
                        'y': DeviceDataset('y_mon',
                                           dtype='float32',
                                           ),
                        'shutter': DeviceDataset('shutter'),
                    }
                },
                'monitor:NXmonitor': {
                    'monitor': DetectorDataset('det1_mon1',
                                               dtype='int',
                                               ),
                    'fdetecor': DetectorDataset('fdet1',
                                                dtype='int',
                                                ),
                },
                'sample:NXsample': {
                    'samplename': DeviceAttribute('Sample', 'samplename'),
                    'alpha': DeviceDataset('alpha',
                                           dtype='float32',
                                           ),
                    'magnet_field': DeviceDataset('B',
                                                  dtype='float32',
                                                  ),
                },
            },
        }
        return template
