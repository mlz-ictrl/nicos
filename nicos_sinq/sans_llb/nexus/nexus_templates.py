# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

from copy import deepcopy

from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceAttribute, DeviceDataset, NamedImageDataset, NXAttribute, NXLink, \
    NXTime
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_sinq.nexus.specialelements import SaveSampleEnv

sansllb_default = {
    'NeXus_Version': '4.4.0',
    'instrument': 'SANS at SINQ',
    'owner': DeviceAttribute('SANS-LLB', 'responsible'),
    'entry0:NXentry': {
        'title': DeviceDataset('Exp', 'title'),
        'proposal_title': DeviceDataset('Exp', 'title'),
        'proposal_id': DeviceDataset('Exp', 'proposal'),
        'start_time': NXTime(), 'end_time': NXTime(),
        'definition': ConstDataset('NXsas', 'string'),
        'user:NXuser': {
            'name': DeviceDataset('Exp', 'users'),
            'email': DeviceDataset('Exp', 'localcontact')
        },
        'proposal_user:NXuser': {
            'name': DeviceDataset('Exp', 'users'),
        },
        'control:NXmonitor': {
            'preset': DetectorDataset('preset', 'float32'),
            'mode': DetectorDataset('mode', 'string'),
            'count_time': DetectorDataset('elapsedtime', 'float32'),
            'integral': DetectorDataset('monitor1', 'int32',
                                        units=NXAttribute('counts',
                                                          'string')),
        },
        'monitor2:NXmonitor': {
            'integral': DetectorDataset('monitor2', 'int32',
                                        units=NXAttribute('counts',
                                                          'string')),
        },
        'monitor3:NXmonitor': {
            'integral': DetectorDataset('c3', 'int32',
                                        units=NXAttribute('counts',
                                                          'string')),
        },
        'protoncount:NXmonitor': {
            'integral': DetectorDataset('protoncount', 'int32',
                                        units=NXAttribute('counts',
                                                          'string')),
        },
        'central_detector:NXdata': {
            'data': NXLink('/entry0/SANS-LLB/central_detector/data'),
        },
        'left_detector:NXdata': {
            'data': NXLink('/entry0/SANS-LLB/left_detector/data'),
        },
        'bottom_detector:NXdata': {
             'data': NXLink('/entry0/SANS-LLB/bottom_detector/data'),
        },
    }
}  # root

inst_default = {
    'name': ConstDataset('SANS-LLB', 'string'),
    'attenuator:NXAttenuator': {
        'selection': DeviceDataset('att'),
    },
    'beam_stop:NXstop': {
        'x': DeviceDataset('bsx'),
        'y': DeviceDataset('bsy'),
        'distance': ConstDataset(35, 'float',
                                 units=NXAttribute('degree',
                                                   'string')),
    },
    'collimator:NXcollimator': {
        'length': DeviceDataset('coll'),
    },
    'polariser:NXpolariser': {
        'selection': DeviceDataset('pol'),
        'position': DeviceDataset('polpos'),
    },
    'SINQ:NXsource': {
        'name': ConstDataset(
            'SINQ, Paul Scherrer Institute', 'string'),
        'type': ConstDataset(
            'continuous flux spallation source', 'string'),
        'probe': ConstDataset('neutron', 'string'),
    },
    'velocity_selector:NXvelocity_selector': {
        'type': ConstDataset('Dornier Velocity Selector',
                             'string'),
        'wavelength': DeviceDataset('wavelength'),
        'wavelength_spread': DeviceDataset('wavelength', parameter='fwhm'),
        'rotation_speed': DeviceDataset('vs_speed'),
        'twist': ConstDataset(0, float,
                              units=NXAttribute('degree', 'string')),
    },
}

central_detector = {
    'x': DeviceDataset('dthx'),
    'x_set': DeviceDataset('dthx', parameter='target'),
    'x_offset': DeviceDataset('dthx', parameter='offset'),
    'distance': DeviceDataset('dthz'),
    'distance_set': DeviceDataset('dthz', parameter='target'),
    'z_offset': DeviceDataset('dthz', parameter='offset'),
    'data': NamedImageDataset('main_det'),
    'raw_data': NamedImageDataset('det_image'),
    'x_pixel_size': ConstDataset(5, float,
                                 units=NXAttribute('mm', 'string')),
    'y_pixel_size': ConstDataset(5, float,
                                 units=NXAttribute('mm', 'string')),
    'beam_center_x': ConstDataset(62.5, float,
                                  units=NXAttribute('pixel', 'string')),
    'beam_center_y': ConstDataset(62.5, float,
                                  units=NXAttribute('pixel', 'string')),
    'type': ConstDataset('monoblock', 'string'),
    'deadtime': ConstDataset(3.5E-6, 'float'),
}

left_detector = {
    'x': DeviceDataset('dtlx'),
    'x_set': DeviceDataset('dtlx', parameter='target'),
    'x_offset': DeviceDataset('dtlx', parameter='offset'),
    'distance': DeviceDataset('dtlz'),
    'distance_set': DeviceDataset('dtlz', parameter='target'),
    'z_offset': DeviceDataset('dtlz', parameter='offset'),
    'data': NamedImageDataset('side_det'),
    # "raw_data": SliceImage('high_q_raw', 256,  0, 16),
    'x_pixel_size': ConstDataset(12.7, float,
                                 units=NXAttribute('mm', 'string')),
    'y_pixel_size': ConstDataset(5, float,
                                 units=NXAttribute('mm', 'string')),
    'beam_center_x': NXLink('/entry0/SANS-LLB/central_detector/beam_center_x'),
    'beam_center_y': NXLink('/entry0/SANS-LLB/central_detector/beam_center_y'),
    'type': ConstDataset('monoblock', 'string'),
    'deadtime': ConstDataset(3.5E-6, 'float'),
}


bottom_detector = {
    'x': DeviceDataset('dtlx'),
    'x_set': DeviceDataset('dtlx', parameter='target'),
    'x_offset': DeviceDataset('dtlx', parameter='offset'),
    'distance': DeviceDataset('dtlz'),
    'distance_set': DeviceDataset('dtlz', parameter='target'),
    'z_offset': DeviceDataset('dtlz', parameter='offset'),
    'data': NamedImageDataset('lower_det'),
    'x_pixel_size': ConstDataset(12.7, float,
                                 units=NXAttribute('mm', 'string')),
    'y_pixel_size': ConstDataset(5, float,
                                 units=NXAttribute('mm', 'string')),
    'beam_center_x': NXLink('/entry0/SANS-LLB/central_detector/beam_center_x'),
    'beam_center_y': NXLink('/entry0/SANS-LLB/central_detector/beam_center_y'),
    'type': ConstDataset('monoblock', 'string'),
    'deadtime': ConstDataset(3.5E-6, 'float'),
}

sample_common = {
    'name': DeviceDataset('Sample', 'samplename'),
    'x': DeviceDataset('stx'),
    'x_set': DeviceDataset('stx', parameter='target'),
    'y': DeviceDataset('sty'),
    'y_set': DeviceDataset('sty', parameter='target'),
    'z': DeviceDataset('stz'),
    'z_set': DeviceDataset('stz', parameter='target'),
    'omega': DeviceDataset('stom'),
    'sgu': DeviceDataset('stgn'),
    'lieselotte': SaveSampleEnv(),
}


class SANSLLBTemplateProvider(NexusTemplateProvider):
    def makeGuide(self, no):
        result = {
            'selection': DeviceDataset('guide%d' % no),
            'position': DeviceDataset('guide%dpos' % no),
            'position_set': DeviceDataset('guide%dpos' % no,
                                          parameter='target'),
            'm_value': ConstDataset(3, float),
        }
        return result

    def makeSlit(self, no):
        result = {
            'left': DeviceDataset('sl%dxp' % no),
            'right': DeviceDataset('sl%dxn' % no),
            'bottom': DeviceDataset('sl%dyp' % no),
            'top': DeviceDataset('sl%dyn' % no),
            'left_set': DeviceDataset('sl%dxp' % no, parameter='target'),
            'right_set': DeviceDataset('sl%dxn' % no, parameter='target'),
            'bottom_set': DeviceDataset('sl%dyp' % no, parameter='target'),
            'top_set': DeviceDataset('sl%dyn' % no, parameter='target'),
            'x_gap': DeviceDataset('sl%dxw' % no),
            'y_gap': DeviceDataset('sl%dyw' % no),
            'x_center': DeviceDataset('sl%dxc' % no),
            'y_center': DeviceDataset('sl%dyc' % no),
        }
        return result

    def makeInstrument(self):
        result = deepcopy(inst_default)
        coll = result['collimator:NXcollimator']
        for i in range(0, 6):
            coll['guide%d:NXguide' % i] = self.makeGuide(i)
            coll['slit%d:NXslit' % i] = self.makeSlit(i)
        coll['slit6:NXslit'] = self.makeSlit(6)
        coll['slit6:NXslit']['distance'] = DeviceDataset('sl6_distance')
        result['central_detector:NXdetector'] = deepcopy(central_detector)
        result['left_detector:NXinstrument'] = deepcopy(left_detector)
        result['bottom_detector:NXinstrument'] = deepcopy(bottom_detector)
        return result

    def getTemplate(self):
        full = deepcopy(sansllb_default)
        entry = full['entry0:NXentry']
        entry['SANS-LLB:NXinstrument'] = self.makeInstrument()
        entry['sample:NXsample'] = deepcopy(sample_common)
        return full
