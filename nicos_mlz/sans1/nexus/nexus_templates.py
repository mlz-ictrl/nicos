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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from nicos import session
from nicos.nexus.elements import ConstDataset, DeviceDataset, ImageDataset, \
    NexusSampleEnv, NXAttribute, NXLink

from nicos_mlz.nexus import CounterMonitor, MLZTemplateProvider, Polarizer, \
    Selector, TimerMonitor, signal
from nicos_sinq.nexus.specialelements import OptionalDeviceDataset


def Collimator():
    return {
        'geometry:NXgeometry': {
            'shape:NXshape': {
                'shape': ConstDataset('nxbox', 'string'),
                'type': ConstDataset('Soller', 'string'),
                'soller_angle': DeviceDataset('col', dtype='float'),
            },
        },
    }


def BeamStop():
    return {
        'description': ConstDataset('rectangular', 'string'),
        'x': DeviceDataset('bs1_xax'),
        'y': DeviceDataset('bs1_xax'),
        # 'status': DeviceDataset('bs1'),
    }


sample_common = {
    'hugo': NexusSampleEnv(),
    'temperature': DeviceDataset('temperature', 'value', defaultval=0.0),
    'magfield': DeviceDataset('magfield', 'value', defaultval=0.0),
    'aequatorial_angle': ConstDataset(0, 'float',
                                      units=NXAttribute('degree', 'string')),
    'stick_rotation': OptionalDeviceDataset('dom'),
}

sample_std = {
    'x_position': DeviceDataset('xo'),
    'x_null': DeviceDataset('xo', 'offset'),
    'x_position_lower': DeviceDataset('xu'),
    'x_null_lower': DeviceDataset('xu', 'offset'),
    'y_position': DeviceDataset('yo'),
    'y_null': DeviceDataset('yo', 'offset'),
    'z_position': DeviceDataset('z'),
    'z_null': DeviceDataset('z', 'offset'),
    'omega': DeviceDataset('sg'),
    'omega_null': DeviceDataset('sg', 'offset'),
    'a3': DeviceDataset('a3'),
    'a3_null': DeviceDataset('a3', 'offset'),
    'position': DeviceDataset('spos'),
    'position_null': DeviceDataset('spos', 'offset'),
}

sample_magnet = {
    'magnet_omega': DeviceDataset('mom'),
    'magnet_omega_null': DeviceDataset('mom', 'offset'),
    'magnet_z': DeviceDataset('mz'),
    'magnet_z_null': DeviceDataset('mz', 'offset'),
}


class SANSTemplateProvider(MLZTemplateProvider):

    # entry = 'entry1'
    definition = 'NXsas'

    def updateInstrument(self):
        self._inst.update({
            'monochromator:NXmonochromator': {
                'wavelength': NXLink(
                    f'/{self.entry}/{self.instrument}/monochromator/velocity_selector/wavelength'),
                'wavelength_spread': NXLink(
                    f'/{self.entry}/{self.instrument}/monochromator/velocity_selector/wavelength_spread'),
                'velocity_selector:NXvelocity_selector': Selector(
                    'selector_rpm', 'selector_lambda', 'selector_delta_lambda',
                    'selector_tilt'),
            },
            'collimator:NXcollimator': Collimator(),
            'attenuator:NXattenuator': {
                'attenuator_transmission': DeviceDataset('att'),
            },
            'beam_stop:NXbeam_stop': BeamStop(),
            'polarizer:NXpolarizer': Polarizer(reflection=0.99),
        })

    def updateDetector(self):
        self._det.update({
            'data': ImageDataset(0, 0, dtype=int, signal=signal),
            'distance': DeviceDataset('det1_x'),
            'x_pixel_size': ConstDataset(
                8, 'float', units=NXAttribute('mm', 'string')),
            'y_pixel_size': ConstDataset(
                8, 'float', units=NXAttribute('mm', 'string')),
            'polar_angle': ConstDataset(
                0, 'float', units=NXAttribute('degree', 'string')),
            'azimuthal_angle': ConstDataset(
                0, 'float', units=NXAttribute('degree', 'string')),
            'rotation_angle': ConstDataset(
                0, 'float', units=NXAttribute('degree', 'string')),
            'aequatorial_angle': ConstDataset(
                0, 'float', units=NXAttribute('degree', 'string')),
            'beam_center_x': ConstDataset(
                0, 'float', units=NXAttribute('mm', 'string')),
            'beam_center_y': ConstDataset(
                0, 'float', units=NXAttribute('mm', 'string')),
            'type': ConstDataset('He3 PSD', 'string'),
            'layout': ConstDataset('area', 'string'),
            'diameter': ConstDataset(
                8, 'float', units=NXAttribute('mm', 'string')),
            # TODO: find out how to set the correct value for tisane
            'acquisition_mode': ConstDataset('histogrammed', 'string'),
        })

        self._entry.update({
            'monitor1:NXmonitor': CounterMonitor('det1_mon1'),
            'monitor2:NXmonitor': CounterMonitor('det1_mon2'),
            # 'monitor3:NXmonitor': CounterMonitor('det1_mon3'),
            'timer:NXmonitor': TimerMonitor('det1_timer'),
        })
        preset = session.getDevice('det1').preset()
        if preset.get('det1_mon1'):
            monitor = 'monitor1'
        elif preset.get('det1_mon2'):
            monitor = 'monitor2'
        elif preset.get('det1_mon3'):
            monitor = 'monitor3'
        else:
            monitor = 'timer'
        monitor_link = f'/{self.entry}/{monitor}/'
        self._entry.update({'control:NXmonitor': {
            'mode': NXLink(f'{monitor_link}/mode'),
            'preset': NXLink(f'{monitor_link}/preset'),
            'integral': NXLink(f'{monitor_link}/integral'),
        }})
        if monitor != 'timer':
            self._entry['control:NXmonitor'].update({
                'type': NXLink(f'{monitor_link}/type'),
            })

    def updateSample(self):
        # if 'sample' in session.loaded_setups:
        #     self._sample.update(dict(sample_common, **sample_std))
        # elif 'emagnet_sample' in session.loaded_setups:
        #     self._sample.update(dict(sample_common, **sample_magnet))
        # else:
        #     self._sample.update(sample_common)
        pass

    def updateData(self):
        pass

    def completeTemplate(self):
        MLZTemplateProvider.completeTemplate(self)
        self._entry.update({
            'entry': f'{self.entry}',
        })
