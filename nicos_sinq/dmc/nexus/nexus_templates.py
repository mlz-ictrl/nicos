#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

from nicos.nexus.elements import DetectorDataset, DeviceAttribute, \
    DeviceDataset, ImageDataset, NXAttribute, NXLink, NXTime
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_ess.nexus import EventStream, NXDataset
from nicos_ess.nexus.elements import CacheStream

dmc_default = {
    'NeXus_Version': '4.4.0',
    'instrument': 'DMC',
    'owner': DeviceAttribute('DMC', 'responsible'),
    'entry:NXentry': {
        'default': 'data',
        'title': DeviceDataset('Exp', 'title'),
        'user:NXuser': {
            'name': DeviceDataset('Exp', 'users'),
            'email': DeviceDataset('Exp', 'localcontact')
        },
        'proposal_id': DeviceDataset('Exp', 'proposal'),
        'start_time': NXTime(),
        'sample:NXsample': {
            'name': DeviceDataset('Sample', 'samplename'),
            'rotation_angle': DeviceDataset('a3',
                                            dtype='float32',
                                            units=NXAttribute('degree',
                                                              'string')
                                            ),
        },
        'monitor:NXmonitor': {
            'mode': DetectorDataset('mode', 'string'),
            'preset': DetectorDataset('preset', 'float32'),
            'monitor': DetectorDataset('monitor', 'float32',
                                       units=NXAttribute('counts', 'string')),
            'time': DetectorDataset('timer', 'float32',
                                    units=NXAttribute('seconds', 'string')),
            'proton_charge': DeviceDataset('proton_charge',
                                           dtype='float32',
                                           units=NXAttribute('uC', 'string')),
        },
        'DMC:NXinstrument': {
            'SINQ:NXSource': {
                'name': 'SINQ',
                'type': 'Continuous flux spallation source',
            },
            'monochromator:NXmonochromator': {
                'curvature': DeviceDataset('mcv',
                                           dtype='float32'),
                'wavelength': DeviceDataset('wavelength',
                                            dtype='float32'),
                'rotation_angle': DeviceDataset('a1',
                                                dtype='float32',
                                                units=NXAttribute('degree',
                                                                  'string')),
                'takeoff_angle': DeviceDataset('a2',
                                               dtype='float32',
                                               units=NXAttribute('degree',
                                                                 'string')),
                'type': 'Pyrolithic Graphite',

                'translation_lower': DeviceDataset('mtl',
                                                   dtype='float32',
                                                   units=NXAttribute('mm',
                                                                     'string')),
                'translation_upper': DeviceDataset('mtu',
                                                   dtype='float32',
                                                   units=NXAttribute('mm',
                                                                     'string')),
                'goniometer_lower': DeviceDataset('mgl',
                                                  dtype='float32',
                                                  units=NXAttribute('degree',
                                                                    'string')),
                'goniometer_upper': DeviceDataset('mgu',
                                                  dtype='float32',
                                                  units=NXAttribute('degree',
                                                                    'string')),
                'curvature_vertical': DeviceDataset('mcv',
                                                    dtype='float32',
                                                    units=NXAttribute('degree',
                                                                      'string')
                                                    ),
            },
            'detector:NXdetector': {
                'detector_position': DeviceDataset('a4',
                                                   dtype='float32',
                                                   units=NXAttribute('degree',
                                                                     'string')),
                'summed_counts': DetectorDataset('counts', dtype='int32',
                                                 units=NXAttribute('counts',
                                                                   'string')),
                'data': NXLink('/entry/DMC/detector/counts'),
            }
        },
        'data:NXdata': {
            'signal': NXAttribute('data', 'string'),
            'data': NXLink('/entry/DMC/detector/data')
        }
    }
}


dmc_optics = {
    'NeXus_Version': '4.4.0',
    'instrument': 'DMC',
    'owner': DeviceAttribute('DMC', 'responsible'),
    'entry:NXentry': {
        'default': 'data',
        'title': DeviceDataset('Exp', 'title'),
        'user:NXuser': {
            'name': DeviceDataset('Exp', 'users'),
            'email': DeviceDataset('Exp', 'localcontact')
        },
        'proposal_id': DeviceDataset('Exp', 'proposal'),
        'start_time': NXTime(),
        'sample:NXsample': {
            'name': DeviceDataset('Sample', 'samplename'),
            'rotation_angle': DeviceDataset('som',
                                            dtype='float32',
                                            units=NXAttribute('degree',
                                                              'string')
                                            ),
            'polar_angle': DeviceDataset('a2',
                                         dtype='float32',
                                         units=NXAttribute('degree', 'string')
                                         ),
        },
        'monitor:NXmonitor': {
            'mode': DetectorDataset('mode', 'string'),
            'preset': DetectorDataset('preset', 'float32'),
            'monitor': DetectorDataset('monitorval', 'float32',
                                       units=NXAttribute('counts', 'string')
                                       ),
            'time': DetectorDataset('elapsedtime', 'float32',
                                    units=NXAttribute('seconds', 'string')
                                    ),
        },
        'DMC:NXinstrument': {
            'SINQ:NXSource': {
                'name': 'SINQ',
                'type': 'Continuous flux spallation source',
            },
            'monochromator:NXmonochromator': {
                'curvature': DeviceDataset('mcv',
                                           dtype='float32'),
                'wavelength': DeviceDataset('wavelength',
                                            dtype='float32'),
                'rotation_angle': DeviceDataset('a1',
                                                dtype='float32',
                                                units=NXAttribute('degree',
                                                                  'string')
                                                ),
                'type': 'Pyrolithic Graphite',

                'translation_lower': DeviceDataset('mtl',
                                                   dtype='float32',
                                                   units=NXAttribute('mm',
                                                                     'string')
                                                   ),
                'translation_upper': DeviceDataset('mtu',
                                                   dtype='float32',
                                                   units=NXAttribute('mm',
                                                                     'string')
                                                   ),
                'goniometer_lower': DeviceDataset('mgl',
                                                  dtype='float32',
                                                  units=NXAttribute('degree',
                                                                    'string')
                                                  ),
                'goniometer_upper': DeviceDataset('mgu',
                                                  dtype='float32',
                                                  units=NXAttribute('degree',
                                                                    'string')
                                                  ),
                'curvature_vertical': DeviceDataset('mcv',
                                                    dtype='float32',
                                                    units=NXAttribute('degree',
                                                                      'string')
                                                    ),
            },
            'adaptive_optics:NXgroup': {
                'taz': DeviceDataset('taz', dtype='float32'),
            },
            'detector:NXdetector': {
                'counts': ImageDataset(0, 0, signal=NXAttribute(1, 'int32')),
                'data': NXLink('/entry/DMC/detector/counts'),
            }
        },
        'data:NXdata': {
            'signal': NXAttribute('data', 'string'),
            'data': NXLink('/entry/DMC/detector/data')
        }
    }
}


# NeXus template for event mode

dmc_event_mode = {
    'NeXus_Version': '4.4.0',
    'instrument': 'DMC',
    'owner': DeviceAttribute('DMC', 'responsible'),
    'entry:NXentry': {
        'default': 'data',
        'title': DeviceDataset('Exp', 'title'),
        'user:NXuser': {
            'name': DeviceDataset('Exp', 'users'),
            'email': DeviceDataset('Exp', 'localcontact')
        },
        'proposal_id': DeviceDataset('Exp', 'proposal'),
        'start_time': DeviceDataset('dataset', 'starttime'),
        'sample:NXsample': {
            'name': DeviceDataset('Sample', 'samplename'),
            'rotation_angle:NXevent_data': {
                'data': EventStream(topic='DMC_metadata',
                                    mod='f142',
                                    source='SQ:DMC:mcu1:SOM',
                                    chunk_size=1,
                                    dtype='float')
            },
            'temperature': NXDataset([0], dtype='float', units='K'),
            'temperature_mean': NXDataset([0], dtype='float', units='K'),
            'temperature_stddev': NXDataset([0], dtype='float', units='K'),
        },
        'monitor:NXmonitor': {
            'time': CacheStream('elapsedtime', dtype='float'),
            'count_mode': DeviceDataset('dmcdet', 'mode', 'string'),
            'preset': DeviceDataset('dmcdet', 'preset'),
            'current:NXevent_data': {
                'data': EventStream(topic='DMC_metadata',
                                    mod='f142',
                                    source='MHC6:IST:2',
                                    chunk_size=1,
                                    dtype='float')
            },
        },
        'DMC:NXinstrument': {
            'SINQ:NXSource': {
                'name': NXDataset('SINQ'),
                'type': NXDataset('Continuous flux spallation source')
            },
            'monochromator:NXmonochromator': {
                'curvature:NXevent_data': {
                    'data': EventStream(topic='DMC_metadata',
                                        mod='f142',
                                        source='SQ:DMC:mcu1:MCV',
                                        chunk_size=1,
                                        dtype='float')
                },
                'd_spacing': DeviceDataset('wavelength', 'dvalue'),
                'wavelength:NXevent_data': {
                    'data': EventStream(topic='DMC_nicosCache',
                                        mod='f142',
                                        source='wavelength',
                                        chunk_size=1,
                                        dtype='float')
                },
                'rotation_angle:NXevent_data': {
                    'data': EventStream(topic='DMC_metadata',
                                        mod='f142',
                                        source='SQ:DMC:mcu1:A1',
                                        chunk_size=1,
                                        dtype='float')
                },
                'takeoff_angle:NXevent_data': {
                    'data': EventStream(topic='DMC_metadata',
                                        mod='f142',
                                        source='SQ:DMC:mcu1:A2',
                                        chunk_size=1,
                                        dtype='float')
                },
                'type': NXDataset('Pyrolithic Graphite', type='string'),
                'translation_lower:NXevent_data': {
                    'data': EventStream(topic='DMC_metadata',
                                        mod='f142',
                                        source='SQ:DMC:mcu1:MTL',
                                        chunk_size=1,
                                        dtype='float')
                },
                'translation_upper:NXevent_data': {
                    'data': EventStream(topic='DMC_metadata',
                                        mod='f142',
                                        source='SQ:DMC:mcu1:MTU',
                                        chunk_size=1,
                                        dtype='float')
                },
                'goniometer_lower:NXevent_data': {
                    'data': EventStream(topic='DMC_metadata',
                                        mod='f142',
                                        source='SQ:DMC:mcu1:MGL',
                                        chunk_size=1,
                                        dtype='float')
                },
                'goniometer_upper:NXevent_data': {
                    'data': EventStream(topic='DMC_metadata',
                                        mod='f142',
                                        source='SQ:DMC:mcu1:MGU',
                                        chunk_size=1,
                                        dtype='float')
                },
            },
            'detector:NXdetector': {
                'a4:NXevent_data': {
                    'data': EventStream(topic='DMC_metadata',
                                        mod='f142',
                                        source='SQ:DMC:mcu2:A4',
                                        chunk_size=1,
                                        dtype='float'),
                },
                'data:NXevent_data': {
                    'data': EventStream(topic='DMC_detector',
                                        mod='ev42',
                                        source='DMC_detector',
                                        dtype='uint32',
                                        chunk_size=100,
                                        ),
                },
                'data_histogram:NXevent_data': {
                    'data': EventStream(topic='DMC_histograms',
                                        mod='hs00',
                                        source='',
                                        dtype='uint32',
                                        chunk_size=100,)
                }
            }
        },
        'data:NXdata': {
            'signal': NXAttribute('data', 'string'),
            'data': NXLink('/entry/DMC/detector/data')
        }
    }
}


class DMCTemplateProvider(NexusTemplateProvider):
    def getTemplate(self):
        return dmc_default
