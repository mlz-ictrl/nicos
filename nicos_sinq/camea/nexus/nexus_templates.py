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

import copy

from nicos import session
from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceAttribute, DeviceDataset, ImageDataset, NXAttribute, NXLink, \
    NXScanLink, NXTime
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_sinq.camea.nexus.camea_elements import CameaAzimuthalAngle, \
    BoundaryArrayParam
from nicos_sinq.nexus.specialelements import AbsoluteTime, ArrayParam, \
    EnvDeviceDataset, OutSampleEnv, Reflection, ScanCommand, ScanVars


class CameaTemplateProvider(NexusTemplateProvider):
    """
    Template for writing NeXus files for CAMEA
    """
    _default = {"NeXus_Version": "4.3.0", "instrument": "CAMEA",
                "owner": DeviceAttribute('CAMEA', 'responsible'),
                "entry:NXentry": {
                    "title": DeviceDataset('Exp', 'title'),
                    "proposal_title": DeviceDataset('Exp', 'title'),
                    "proposal_id": DeviceDataset('Exp', 'proposal'),
                    "comment": DeviceDataset('Exp', 'remark'),
                    "start_time": NXTime(),
                    "end_time": NXTime(),
                    "scanvars": ScanVars(),
                    "scancommand": ScanCommand(),
                    "instrument": ConstDataset('CAMEA', 'string'),
                    "user:NXuser": {
                        "name": DeviceDataset('Exp', 'users'),
                        "email": DeviceDataset('Exp', 'localcontact',
                                               dtype='string')},
                    "control:NXmonitor": {
                        "absolute_time": AbsoluteTime(),
                        "mode": DetectorDataset('mode', "string"),
                        "data": DetectorDataset('monitor1', 'float32',
                                                units=NXAttribute('counts',
                                                                  'string')),
                        "preset": DetectorDataset('preset', 'float32'),
                        "time": DetectorDataset('elapsedtime', 'float32',
                                                units=NXAttribute('seconds',
                                                                  'string')),
                    },
                    "proton_beam:NXmonitor": {
                        "data": DetectorDataset('protoncount', 'int32',
                                                units=NXAttribute('counts',
                                                                  'string'))},
                    "monitor_2:NXmonitor": {
                            "data": DetectorDataset('monitor2', 'int32',
                                                    units=NXAttribute(
                                                        'counts',
                                                        'string'))
                    },
                    "data:NXdata": {
                        "data": NXLink('/entry/CAMEA/detector/data'),
                        "summed_counts":
                            NXLink(
                            '/entry/CAMEA/detector/summed_counts'),
                        "dummy": NXScanLink(),
                        }
                    }
                }

    _camea_blocklist = ['a1', 'a2,', 'a3', 'a4', 'a5', 'a6', 'qh', 'qk', 'ql',
                        'en', 'ei', 'ef', 's2t', 'm2t', 'gl', 'gu', 'som',
                        'tl', 'tu', 'gm', 'mcv', 'omm', 'tlm', 'tum', 'mono',
                        'ana', 'msr', 'msl', 'msb', 'mst', 'mslit_height',
                        'mslit_width']

    _camea_sample = {
        "name": DeviceDataset(
            'Sample', 'samplename'),
        "hugo": OutSampleEnv(blocklist=_camea_blocklist),
        "azimuthal_angle": CameaAzimuthalAngle('CAMEA'),
        "orientation_matrix": ArrayParam('Sample', 'ubmatrix', 'float32',
                                         reshape=(3, 3)),
        "plane_normal": ArrayParam('CAMEA', 'plane_normal', 'float32'),
        "rotation_angle":
            EnvDeviceDataset('a3', dtype='float32', units=NXAttribute(
                    'degree',
                    'string')),
        "rotation_angle_zero":
            DeviceDataset('a3', parameter='offset',
                          dtype='float32',
                          units=NXAttribute('degree',
                                            'string')),
        "sgu": EnvDeviceDataset('sgu', dtype='float32',
                                units=NXAttribute('degree',
                                                  'string')),
        "sgu_zero": DeviceDataset('sgu', parameter='offset',
                                  dtype='float32',
                                  units=NXAttribute('degree',
                                                    'string')),
        "sgl": EnvDeviceDataset('sgl', dtype='float32',
                                units=NXAttribute('degree',
                                                  'string')),
        "sgl_zero": DeviceDataset('sgl', parameter='offset',
                                  dtype='float32',
                                  units=NXAttribute('degree',
                                                    'string')),
        "x": EnvDeviceDataset('tu', dtype='float32', units=NXAttribute(
            'mm', 'string')),
        "y": EnvDeviceDataset('tl', dtype='float32', units=NXAttribute(
            'mm', 'string')),
        "qh": EnvDeviceDataset('h', dtype='float32',
                               units=NXAttribute('rlu', 'string')),
        "qk": EnvDeviceDataset('k', dtype='float32',
                               units=NXAttribute('rlu', 'string')),
        "ql": EnvDeviceDataset('l', dtype='float32',
                               units=NXAttribute('rlu', 'string')),
    }

    _camea_inst = {
        "analyzer:NXcrystal": {
            "d_spacing": DeviceDataset('ana', parameter='dvalue',
                                       dtype='float32',
                                       units=NXAttribute('Angstroem',
                                                         'string')),
            "analyzer_selection": DeviceDataset('anaNo', dtype='int32',
                                                units=NXAttribute(
                                                    'selection', 'string')),
            "nominal_energy": EnvDeviceDataset('ef', dtype='float32',
                                               units=NXAttribute('mev',
                                                                 'string')),
            "type": ConstDataset('Pyrolythic Graphite', dtype='string'),
            "polar_angle": EnvDeviceDataset('a4', dtype='float32',
                                            units=NXAttribute('degree',
                                                              'string')),
            "polar_angle_offset": DeviceDataset('a4', parameter='a4offset',
                                                dtype='float32',
                                                units=NXAttribute('degree',
                                                                  'string')),
            "polar_angle_raw": EnvDeviceDataset('s2t', dtype='float32',
                                                units=NXAttribute('degree',
                                                                  'string')),
        },
        "monochromator:NXcrystal": {
            "d_spacing": DeviceDataset('mono', parameter='dvalue',
                                       dtype='float32',
                                       units=NXAttribute('Angstroem',
                                                         'string')),
            "energy": EnvDeviceDataset('ei', dtype='float32',
                                       units=NXAttribute('mev',
                                                         'string')),
            "type": ConstDataset('Pyrolythic Graphite', dtype='string'),
            "rotation_angle": EnvDeviceDataset('a1', dtype='float32',
                                               units=NXAttribute('degree',
                                                                 'string')),
            "rotation_angle_zero": DeviceDataset('a1', parameter='offset',
                                                 dtype='float32',
                                                 units=NXAttribute('degree',
                                                                   'string')),
            "gm": EnvDeviceDataset('gm', dtype='float32',
                                   units=NXAttribute('degree',
                                                     'string')),
            "gm_zero": DeviceDataset('gm', parameter='offset',
                                     dtype='float32',
                                     units=NXAttribute('degree',
                                                       'string')),
            "tlm": EnvDeviceDataset('tlm', dtype='float32',
                                    units=NXAttribute('mm', 'string')),
            "tlm_zero": DeviceDataset('tlm', parameter='offset',
                                      dtype='float32',
                                      units=NXAttribute('mm', 'string')),
            "tum": EnvDeviceDataset('tum', dtype='float32',
                                    units=NXAttribute('mm', 'string')),
            "tum_zero": DeviceDataset('tum', parameter='offset',
                                      dtype='float32',
                                      units=NXAttribute('mm', 'string')),
            "vertical_curvature": EnvDeviceDataset('mcv', dtype='float32'),
        },
        "segment_1:NXdetector": {
            "data": DetectorDataset('monitor3', dtype='int32',
                                    units=NXAttribute('counts', 'string'))
        },
        "segment_8:NXdetector": {
            "data": DetectorDataset('monitor4', dtype='int32',
                                    units=NXAttribute('counts', 'string'))
        },
        "detector:NXdetector": {
            "detector_selection": DeviceDataset('detNo', dtype='int32',
                                                units=NXAttribute('selection',
                                                                  'string')),
            "data": ImageDataset(0, 0, signal=NXAttribute(1, 'int32')),
            "summed_counts": DetectorDataset('counts', dtype='int32',
                                             units=NXAttribute('counts',
                                                               'string')),
            "total_counts": DetectorDataset('camea_detector', dtype='int32',
                                            units=NXAttribute('counts',
                                                              'string')),
        },
        "monochromator_slit:NXslit": {
            "top": EnvDeviceDataset('mst', dtype='float32',
                                    units=NXAttribute('mm', 'string')),
            "top_zero": DeviceDataset('mst', parameter='offset',
                                      dtype='float32',
                                      units=NXAttribute('mm', 'string')),
            "bottom": EnvDeviceDataset('msb', dtype='float32',
                                       units=NXAttribute('mm', 'string')),
            "bottom_zero": DeviceDataset('msb', parameter='offset',
                                         dtype='float32',
                                         units=NXAttribute('mm', 'string')),
            "right": EnvDeviceDataset('msr', dtype='float32',
                                      units=NXAttribute('mm', 'string')),
            "right_zero": DeviceDataset('msr', parameter='offset',
                                        dtype='float32',
                                        units=NXAttribute('mm', 'string')),
            "left": EnvDeviceDataset('msl', dtype='float32',
                                     units=NXAttribute('mm', 'string')),
            "left_zero": DeviceDataset('msl', parameter='offset',
                                       dtype='float32',
                                       units=NXAttribute('mm', 'string')),
            "x_gap": EnvDeviceDataset('mslit_width', dtype='float32',
                                      units=NXAttribute('mm', 'string')),
            "y_gap": EnvDeviceDataset('mslit_height', dtype='float32',
                                      units=NXAttribute('mm', 'string')),
        },
    }

    def _make_calib(self, name):
        result = {
            'a4offset': ArrayParam(name, 'a4offset', 'float32'),
            'amplitude': ArrayParam(name, 'amplitude', 'float32'),
            'background': ArrayParam(name, 'background', 'float32'),
            'boundaries': BoundaryArrayParam(name, 'boundaries', 'int32'),
            'final_energy': ArrayParam(name, 'energy', 'float32'),
            'width': ArrayParam(name, 'width', 'float32'),
        }
        return result

    def getTemplate(self):
        template = copy.deepcopy(self._default)
        template['entry:NXentry']['sample:NXsample'] =\
            copy.deepcopy(self._camea_sample)

        # Write orienting reflections
        sa_temp = template['entry:NXentry']['sample:NXsample']
        oris = session.instrument.orienting_reflections
        sa_temp['plane_vector_1'] = Reflection(oris[0], 'ublist')
        sa_temp['plane_vector_2'] = Reflection(oris[1], 'ublist')

        inst = copy.deepcopy(self._camea_inst)
        inst['calib1:NXcollection'] = self._make_calib('calib1')
        inst['calib3:NXcollection'] = self._make_calib('calib3')
        inst['calib8:NXcollection'] = self._make_calib('calib8')
        template['entry:NXentry']['CAMEA:NXinstrument'] = inst
        return template
