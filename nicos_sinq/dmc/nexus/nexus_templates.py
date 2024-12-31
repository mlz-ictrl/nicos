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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
import copy

from nicos import session
from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceAttribute, DeviceDataset, EndTime, ImageDataset, NXAttribute, \
    NXLink, StartTime
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_ess.nexus import EventStream, NXDataset
from nicos_sinq.nexus.specialelements import AbsoluteTime, CellArray, \
    DevStat, SaveSampleEnv

dmc_base = {
    'NeXus_Version': '4.4.0',
    'instrument': 'DMC',
    'owner': DeviceAttribute('DMC', 'responsible'),
    'entry:NXentry': {
        'default':
            'data',
        'title':
            DeviceDataset('Exp', 'title'),
        'user:NXuser': {
            'name': DeviceDataset('Exp', 'users'),
            'email': DeviceDataset('Exp', 'localcontact')
            },
        'proposal_id':
            DeviceDataset('Exp', 'proposal'),
        'start_time':
            StartTime(),
        'end_time':
            EndTime(),
        'definition':
            ConstDataset(
                'NXmonopd',
                dtype='string',
                url=NXAttribute(
                    'https://raw.githubusercontent.com/nexusformat/'
                    'definitions/main/applications/NXmonopd.nxdl.xml',
                    'string'),
                ),
        'monitor:NXmonitor': {
            'mode':
                DetectorDataset('mode', 'string'),
            'preset':
                DetectorDataset('preset', 'float32'),
            'monitor1':
                DetectorDataset('m1',
                                'float32',
                                units=NXAttribute('counts', 'string')),
            'monitor2':
                DetectorDataset('m2',
                                'float32',
                                units=NXAttribute('counts', 'string')),
            'time':
                DetectorDataset('det_timer',
                                'float32',
                                units=NXAttribute('seconds', 'string')),
            'proton_charge':
                DetectorDataset('proton_charge',
                                dtype='float32',
                                units=NXAttribute('uC', 'string')),
                },
        'DMC:NXinstrument': {
            'SINQ:NXSource': {
                'name': ConstDataset('SINQ', dtype='string'),
                'type': ConstDataset('Continuous flux spallation source',
                                     dtype='string'),
                'probe': ConstDataset('neutron', dtype='string'),
            },
            'monochromator:NXmonochromator': {
                'curvature':
                    DeviceDataset('mcv', dtype='float32'),
                'wavelength':
                    DeviceDataset('wavelength_refined', dtype='float32'),
                'wavelength_raw':
                    DeviceDataset('wavelength', dtype='float32'),
                'rotation_angle':
                    DeviceDataset('a1',
                                  dtype='float32',
                                  units=NXAttribute('degree', 'string')),
                'takeoff_angle':
                    DeviceDataset('a2',
                                  dtype='float32',
                                  units=NXAttribute('degree', 'string')),
                'type':
                    'Pyrolithic Graphite',
                'translation_lower':
                    DeviceDataset('mtl',
                                  dtype='float32',
                                  units=NXAttribute('mm', 'string')),
                'translation_upper':
                    DeviceDataset('mtu',
                                  dtype='float32',
                                  units=NXAttribute('mm', 'string')),
                'goniometer_lower':
                    DeviceDataset('mgl',
                                  dtype='float32',
                                  units=NXAttribute('degree', 'string')),
                'goniometer_upper':
                    DeviceDataset('mgu',
                                  dtype='float32',
                                  units=NXAttribute('degree', 'string')),
                'curvature_vertical':
                    DeviceDataset('mcv',
                                  dtype='float32',
                                  units=NXAttribute('degree', 'string')),
            },
                },
        'data:NXdata': {
            'signal': NXAttribute('data', 'string'),
            'data': NXLink('/entry/DMC/detector/data'),
            'summed_counts': NXLink('/entry/DMC/detector/summed_counts'),
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
            'name': DeviceDataset('sample', 'samplename'),
            'rotation_angle:NXevent_data': {
                'data':
                    EventStream(topic='DMC_metadata',
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
            'time': DeviceDataset('timer', dtype='float'),
            'count_mode': DeviceDataset('dmcdet', 'mode', 'string'),
            'preset': DeviceDataset('dmcdet', 'preset'),
            'current:NXevent_data': {
                'data':
                    EventStream(topic='DMC_metadata',
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
                    'data':
                        EventStream(topic='DMC_metadata',
                                    mod='f142',
                                    source='SQ:DMC:mcu1:MCV',
                                    chunk_size=1,
                                    dtype='float')
                },
                'd_spacing': DeviceDataset('wavelength', 'dvalue'),
                'wavelength:NXevent_data': {
                    'data':
                        EventStream(topic='DMC_nicosCache',
                                    mod='f142',
                                    source='wavelength',
                                    chunk_size=1,
                                    dtype='float')
                },
                'rotation_angle:NXevent_data': {
                    'data':
                        EventStream(topic='DMC_metadata',
                                    mod='f142',
                                    source='SQ:DMC:mcu1:A1',
                                    chunk_size=1,
                                    dtype='float')
                },
                'takeoff_angle:NXevent_data': {
                    'data':
                        EventStream(topic='DMC_metadata',
                                    mod='f142',
                                    source='SQ:DMC:mcu1:A2',
                                    chunk_size=1,
                                    dtype='float')
                },
                'type': NXDataset('Pyrolithic Graphite', type='string'),
                'translation_lower:NXevent_data': {
                    'data':
                        EventStream(topic='DMC_metadata',
                                    mod='f142',
                                    source='SQ:DMC:mcu1:MTL',
                                    chunk_size=1,
                                    dtype='float')
                },
                'translation_upper:NXevent_data': {
                    'data':
                        EventStream(topic='DMC_metadata',
                                    mod='f142',
                                    source='SQ:DMC:mcu1:MTU',
                                    chunk_size=1,
                                    dtype='float')
                },
                'goniometer_lower:NXevent_data': {
                    'data':
                        EventStream(topic='DMC_metadata',
                                    mod='f142',
                                    source='SQ:DMC:mcu1:MGL',
                                    chunk_size=1,
                                    dtype='float')
                },
                'goniometer_upper:NXevent_data': {
                    'data':
                        EventStream(topic='DMC_metadata',
                                    mod='f142',
                                    source='SQ:DMC:mcu1:MGU',
                                    chunk_size=1,
                                    dtype='float')
                },
            },
            'detector:NXdetector': {
                'a4:NXevent_data': {
                    'data':
                        EventStream(topic='DMC_metadata',
                                    mod='f142',
                                    source='SQ:DMC:mcu2:A4',
                                    chunk_size=1,
                                    dtype='float'),
                },
                'data:NXevent_data': {
                    'data':
                        EventStream(
                            topic='DMC_detector',
                            mod='ev42',
                            source='DMC_detector',
                            dtype='uint32',
                            chunk_size=100,
                        ),
                },
                'data_histogram:NXevent_data': {
                    'data':
                        EventStream(
                            topic='DMC_histograms',
                            mod='hs00',
                            source='',
                            dtype='uint32',
                            chunk_size=100,
                        )
                }
            }
        },
        'data:NXdata': {
            'signal': NXAttribute('data', 'string'),
            'data': NXLink('/entry/DMC/detector/data')
        }
    }
}


def makeAdaptiveOptics():
    return 'adaptive_optics:NXguide', {
        'transformation:NXtransformations': {
            'linear_stage:NXtranslation': {
                'vector': (1, 0, 0),
                'attributes': '',
                'transformation_type': 'translation',
                'value': DeviceDataset('optics_lin', dtype='float32'),
                'units': 'mm',
            },
            'rotational_stage:NXrotation': {
                'vector': (0, -1, 0),
                'attributes': '',
                'depends_on': 'linear_stage',
                'transformation_type': 'rotation',
                'value': DeviceDataset('optics_rot', dtype='float32'),
                'units': 'deg',
            },
            'z_stage:NXtranslation': {
                'vector': (0, 1, 0),
                'attributes': '',
                'transformation_type': 'translation',
                'value': DeviceDataset('optics_z', dtype='float32'),
                'units': 'mm',
            },
        }
    }


def makeMonitor():

    if 'dmccontrol' in session.experiment.detlist:
        return {
            'absolute_time':
                AbsoluteTime(),
            'mode':
                DetectorDataset('mode', 'string'),
            'integral':
                DetectorDataset('monitorval',
                                'float32',
                                units=NXAttribute('counts', 'string')),
            'preset':
                DetectorDataset('monitorpreset', 'float32'),
            'time':
                DetectorDataset('elapsedtime',
                                'float32',
                                units=NXAttribute('seconds', 'string')),
        }

    if 'det' in session.experiment.detlist:
        return {
            'mode':
                DetectorDataset('mode', 'string'),
            'preset':
                DetectorDataset('preset', 'float32'),
            'monitor1':
                DetectorDataset('m1',
                                'float32',
                                units=NXAttribute('counts', 'string')),
            'monitor2':
                DetectorDataset('m2',
                                'float32',
                                units=NXAttribute('counts', 'string')),
            'time':
                DetectorDataset('det_timer',
                                'float32',
                                units=NXAttribute('seconds', 'string')),
        }

    return {}


def makeDetector():
    content = {
        'data': ImageDataset(0, 0, signal=NXAttribute(1, 'int32')),
    }

    if 'dmccontrol' in session.experiment.detlist:
        content['summed_counts'] = DetectorDataset('ccdwww',
                                                   dtype='int32',
                                                   units=NXAttribute(
                                                       'counts', 'string'))
        content['time_stamp'] = AbsoluteTime(),

    if 'det' in session.experiment.detlist:
        content['summed_counts'] = DetectorDataset('det_image',
                                                   dtype='int32',
                                                   units=NXAttribute(
                                                       'det_image', 'string'))
        content['detector_position'] = DeviceDataset('a4',
                                                     dtype='float32',
                                                     units=NXAttribute(
                                                         'degree', 'string'))

    return 'detector', content


def makeSample():
    sample = {
        'name':
            DeviceDataset('sample', 'samplename'),
        'rotation_angle':
            DeviceDataset('a3',
                          dtype='float32',
                          units=NXAttribute('degree', 'string')),
        "hugo": SaveSampleEnv(),
        "temperature_mean": DevStat("Ts:avg"),
        "temperature_stddev": DevStat("Ts:stddev"),
    }

    sample_device = session.experiment.sample
    if hasattr(sample_device, 'getCell'):
        nexus_sample_class = 'NXcrystal'
        sample['unit_cell'] = {
            'unit_cell': CellArray(),
        }
    else:
        nexus_sample_class = 'NXsample'

    return nexus_sample_class, sample


class DMCTemplateProvider(NexusTemplateProvider):
    """
      NeXus template generation for DMC at SINQ
    """

    def getTemplate(self):
        dmc_template = copy.deepcopy(dmc_base)
        instrument = dmc_template['entry:NXentry']['DMC:NXinstrument']

        name, content = makeDetector()
        if name:
            instrument[f'{name}:NXdetector'] = content
        else:
            session.log.info('No detector! May be: check setup???')

        sample_class, sample = makeSample()
        dmc_template['entry:NXentry'][f'sample:{sample_class}'] = sample

        monitor = makeMonitor()
        if monitor:
            dmc_template['entry:NXentry']['monitor:NXmonitor'] = monitor

        if 'adaptive_optics' in session.loaded_setups:
            name, content = makeAdaptiveOptics()
            instrument[name] = content

        return dmc_template
