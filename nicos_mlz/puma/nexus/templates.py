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
from nicos.nexus.elements import ConstDataset, DeviceDataset, NXLink

from nicos_mlz.nexus import Collimator, CounterMonitor, Filter, SampleEnv, \
    Slit, TimerMonitor, mm
from nicos_mlz.nexus.nexus_templates import TasTemplateProvider

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

# sample_magnet = {
#     'magnet_omega': DeviceDataset('mom'),
#     'magnet_omega_null': DeviceDataset('mom', 'offset'),
#     'magnet_z': DeviceDataset('mz'),
#     'magnet_z_null': DeviceDataset('mz', 'offset'),
# }


class PumaTemplateProvider(TasTemplateProvider):

    def updateInstrument(self):
        TasTemplateProvider.updateInstrument(self)
        self._inst.update({
            'ca1:NXcollimator': Collimator('alpha3'),
            'ca2:NXcollimator': Collimator('alpha4'),
            'attenuator:NXattenuator': {
                'type': ConstDataset('unknown', dtype='string'),
                'thickness': ConstDataset(5, dtype='float', units=mm),
                # 'status': ,
                'attenuator_transmission': DeviceDataset('att'),
            },
            # 'polarizer:NXpolarizer': Polarizer(reflection=0.99),
            'filter_pg_1:NXfilter': Filter('fpg1', 'Pyrolytic Graphite'),
            'filter_pg_2:NXfilter': Filter('fpg1', 'Pyrolytic Graphite'),
            'erbium_filter:NXfilter': Filter('erbium', 'Erbium'),
            'sapphire_filter:NXfilter': Filter('sapphire', 'Sapphire'),
        })
        for slit, name in (('slit1', 'ss1'),
                           ('slit2', 'ss2'),
                           ('vs', 'ms1')):
            session.log.info('slit: %s', slit)
            if slit in session.devices:
                session.log.info('Add slit: %s', slit)
                self._inst.update({
                    f'{name}:NXslit': Slit(slit)
                })

    def updateDetector(self):
        TasTemplateProvider.updateDetector(self)
        self._det.update({
            # 'data': ImageDataset(0, 0, dtype=int, signal=signal),
            'distance': DeviceDataset('lad'),
            # 'x_pixel_size': ConstDataset(
            #     8, 'float', units=NXAttribute('mm', 'string')),
            # 'y_pixel_size': ConstDataset(
            #     8, 'float', units=NXAttribute('mm', 'string')),
            # 'polar_angle': ConstDataset(
            #     0, 'float', units=NXAttribute('degree', 'string')),
            # 'azimuthal_angle': ConstDataset(
            #     0, 'float', units=NXAttribute('degree', 'string')),
            # 'rotation_angle': ConstDataset(
            #     0, 'float', units=NXAttribute('degree', 'string')),
            # 'aequatorial_angle': ConstDataset(
            #     0, 'float', units=NXAttribute('degree', 'string')),
            # 'beam_center_x': ConstDataset(
            #     0, 'float', units=NXAttribute('mm', 'string')),
            # 'beam_center_y': ConstDataset(
            #     0, 'float', units=NXAttribute('mm', 'string')),
            'type': ConstDataset('He3 Gas cylinder', 'string'),
            'layout': ConstDataset('point', 'string'),
            'diameter': ConstDataset(25.4, 'float', units=mm),
            'acquisition_mode': ConstDataset('pulse counting', 'string'),
        })

        self._entry.update({
            'monitor1:NXmonitor': CounterMonitor('mon1'),
            # 'monitor2:NXmonitor': CounterMonitor('mon2'),
            # 'monitor3:NXmonitor': CounterMonitor('mon3'),
            'timer:NXmonitor': TimerMonitor('timer'),
        })
        preset = session.getDevice('det').preset()
        if preset.get('mon1'):
            monitor = 'monitor1'
        elif preset.get('mon2'):
            monitor = 'monitor2'
        elif preset.get('mon3'):
            monitor = 'monitor3'
        else:
            monitor = 'timer'
        monitor_link = f'/{self.entry}/{monitor}/'
        self._entry.update({'control:NXmonitor': {
            'mode': NXLink(f'{monitor_link}/mode'),
            'preset': NXLink(f'{monitor_link}/preset'),
            'integral': NXLink(f'{monitor_link}/integral'),
            # 'data': NXLink(f'{monitor_link}/integral'),
        }})
        if monitor != 'timer':
            self._entry['control:NXmonitor'].update({
                'type': NXLink(f'{monitor_link}/type'),
            })

    def updateSample(self):
        TasTemplateProvider.updateSample(self)
        temp_env = ['T', 'Ts', ]
        if any(e in session.devices for e in temp_env):
            self._sample.update({
                'temperature_env:NXenvironment': {
                    'value_log:NXlog': SampleEnv(temp_env),
                },
            })
        magfield_env = ['B']
        if any(e in session.devices for e in magfield_env):
            self._sample.update({
                'magnetic_field_env:NXenvironment': {
                    'value_log:NXlog': SampleEnv(magfield_env),
                },
            })

    def completeTemplate(self):
        TasTemplateProvider.completeTemplate(self)
        self._entry.update({
            'entry': f'{self.entry}',
        })
