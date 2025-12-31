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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from nicos import session
from nicos.nexus.elements import ConstDataset, DeviceDataset, ImageDataset

from nicos_mlz.nexus import Slit, mm, signal
from nicos_mlz.nexus.elements import SampleEnv
from nicos_mlz.nexus.nexus_templates import PowderTemplateProvider

from nicos_mlz.stressi.devices import PreciseManualSwitch


def Gap(device):
    """Return a slit structure."""
    return {
        'x_gap': DeviceDataset(f'{device}.width'),
        # 'y_gap': DeviceDataset(f'{device}.height'),
        'center:NXtransformations': {
            'x': DeviceDataset(f'{device}.center'),
            # 'y': DeviceDataset(f'{device}.centery'),
        },
    }


def Collimator():
    return {
        'type': ConstDataset('soller', dtype='string'),
        'transmitting_material': ConstDataset('air', dtype='string'),
        'soller_angle': ConstDataset(0, dtype='float'),
    }


class StressiTemplateProvider(PowderTemplateProvider):

    def init(self, **kwargs):
        PowderTemplateProvider.init(self, **kwargs)
        self.xs = kwargs.get('xs', 'xt')
        self.ys = kwargs.get('ys', 'yt')
        self.zs = kwargs.get('zs', 'zt')
        self.chis = kwargs.get('chis', 'chis')
        self.phis = kwargs.get('phis', 'phis')
        self.omgs = kwargs.get('omgs', 'omgs')

    def updateInstrument(self):
        PowderTemplateProvider.updateInstrument(self)
        self._inst.update({
            'beam_intensity_profile:NXbeam': {
                # 'beam_evaluation': ,
                # 'primary_vertical_type': ,
                # 'primary_vertical_full_width': ,
                # 'primary_vertical_width': ,
                # ...
            },
        })
        if 'slits' in session.devices:
            ename = 'sample_slit:NXslit'
            self._inst.update({
                ename: Slit('slits'),
            })
            self._inst[ename].update({
                'distance': ConstDataset(200, 'float', units=mm),
            })
        if 'slitm' in session.devices:
            ename = 'monochromator_slit:NXslit'
            self._inst.update({
                ename: Slit('slitm'),
            })
            self._inst[ename].update({
                'distance': ConstDataset(100, 'float', units=mm),
            })
        if 'pss' in session.devices:
            # Check, if the device is a collimator device. Maybe there is a
            # better way, but ...
            if isinstance(session.devices['pss']._attached_horizontal,
                          PreciseManualSwitch):
                self._inst.update({
                    'primary_collimator:NXcollimator': Collimator()
                })
                self._inst['primary_collimator:NXcollimator'].update({
                    'geometry:NXgeometry': {
                        'shape:NXshape': {
                            'shape': ConstDataset('nxbox', dtype='string'),
                            'size': ConstDataset([1, 2, 3], dtype='float',
                                                 units=mm),
                        },
                    },
                })
            ename = 'pss:NXslit'
            self._inst.update({
                ename: Slit('pss'),
            })
            self._inst[ename].update({
                'distance': DeviceDataset('psx', units=mm),
            })
        if 'ssw' in session.devices:
            # Check, if the device is a collimator device. Maybe there is a
            # better way, but ...
            if isinstance(session.devices['ssw']._attached_moveable,
                          PreciseManualSwitch):
                self._inst.update({
                    'secondary_collimator:NXcollimator': Collimator()
                })
                self._inst['secondary_collimator:NXcollimator'].update({
                    'geometry:NXgeometry': {
                        'shape:NXshape': {
                            'shape': ConstDataset('nxcone', dtype='string'),
                            'size': ConstDataset([1, ], dtype='float',
                                                 units=mm),
                        },
                    },
                })
            ename = 'ssw:NXslit'
            self._inst.update({
                ename: Gap('ssw')
            })
            self._inst[ename].update({
                'distance': DeviceDataset('yss', units=mm),
            })

    def updateDetector(self):
        PowderTemplateProvider.updateDetector(self)
        self._det.update({
            'polar_angle': DeviceDataset(self.tths),
            'data': ImageDataset(0, 0, signal=signal, units='counts'),
            'type': ConstDataset('He3 PSD', 'string'),
            'layout': ConstDataset('area', 'string'),
            'acquisition_mode': ConstDataset('histogrammed', 'string'),
            'description': DeviceDataset(self.detector, 'description'),
            'x_pixel_size': DeviceDataset(
                'image', 'pixel_size[0]', 'float', 0.85, units=mm),
            'y_pixel_size': DeviceDataset(
                'image', 'pixel_size[1]', 'float', 0.85, units=mm),
            'distance': DeviceDataset('ysd'),  # units=mm),
            # 'efficiency': ,
            # 'wavelength': ,
            # 'dead_time': ,
            # 'count_time': ,
            # 'image_key': DeviceDataset('image_key'),
            # 'depends_on': ,
        })

    def updateSample(self):
        PowderTemplateProvider.updateSample(self)
        self._sample.update({
            'type': ConstDataset('sample', 'string'),
            'x:NXpositioner': {
                'value': DeviceDataset(self.xs),
            },
            'y:NXpositioner': {
                'value': DeviceDataset(self.ys),
            },
            'z:NXpositioner': {
                'value': DeviceDataset(self.zs),
            },
            'chi:NXpositioner': {
                'value': DeviceDataset(self.chis),
            },
            'phi:NXpositioner': {
                'value': DeviceDataset(self.phis),
            },
            'omega:NXpositioner': {
                'value': DeviceDataset(self.omgs),
            },
            'gauge_volume:NXparameters': {
                # 'a': ,
                # 'b': ,
                # 'h': ,
                # 'x': ,
                # 'y': ,
                # 'z': ,
            },
            # 'chemical_formula': ,
        })
        temp_env = ['T', 'Ts', ]
        if any(e in session.devices for e in temp_env):
            self._sample.update({
                'temperature_env:NXenvironment': {
                    'value_log:NXlog': SampleEnv(temp_env),
                },
            })
        stress_env = ['teload', 'tepos', 'teext', ]
        if any(e in session.devices for e in stress_env):
            self._sample.update({
                'stress_field_env:NXenvironment': {
                    'value_log:NXlog': SampleEnv(stress_env, 1),
                },
            })
