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
#   Christoph Herb <christoph.herb@frm2.tum.de>
#
# *****************************************************************************

from nicos import session
from nicos.core.device import Readable
from nicos.nexus.elements import ConstDataset, DeviceDataset, ImageDataset, \
    NexusSampleEnv, NXAttribute, NXLink

from nicos_mlz.nexus import CounterMonitor, MLZTemplateProvider, Polarizer, \
    Selector, TimerMonitor
from nicos_mlz.nexus.structures import signal
from nicos_sinq.nexus.specialelements import OptionalDeviceDataset

all_devices_dict = {
    key: val for key, val in session.devices.items()
    if isinstance(val, Readable)
}

for key in list(all_devices_dict.keys()):
    val = all_devices_dict[key]
    try:
        if len(val.read()) > 0 and not isinstance(val, str):
            all_devices_dict.pop(key, None)
        else:
            all_devices_dict[key] = DeviceDataset(key)
    except Exception:
        all_devices_dict[key] = DeviceDataset(key)

all_devices_dict = {}

# instead of what is done above without any structure we can also try to get a
# structure similar to the one found in the setupspanel
all_setups = session.getSetupInfo()  # this gets all the current setups
for key, setup in all_setups.items():
    if len(setup['devices']) > 0:  # only if the setup contains devices
        # create a subdict for the setup to contain all the devices later
        all_devices_dict[f'{key}:NXCollection'] = {}
        for devname, dev in setup['devices'].items():
            try:
                # only if the device has a value can it be read
                if 'read' in dir(session.devices[devname]):
                    t = session.devices[devname].read()
                    # lists with len > 0 create problems
                    if isinstance(t, (float, str)):
                        all_devices_dict[f'{key}:NXCollection'][devname] = dev
            except KeyError:
                continue

# final run and delete all keys with no further entries
for key in list(all_devices_dict.keys()):
    if not all_devices_dict[key]:
        all_devices_dict.pop(key)


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


class ResedaTemplateProvider(MLZTemplateProvider):

    entry = 'entry1'
    definition = 'NXsas'

    def updateInstrument(self):
        selectorlink = f'/{self.entry}/{self.instrument}/monochromator/velocity_selector'
        self._inst.update({
            'monochromator:NXmonochromator': {
                'wavelength': NXLink(f'{selectorlink}/wavelength'),
                'wavelength_spread': NXLink(
                    f'{selectorlink}/wavelength_spread'),
                'velocity_selector:NXvelocity_selector': Selector(
                    'selector_speed', 'selector_lambda', 'selector_delta_lambda',
                    'selector_tilt'),
            },
            'MiezePydata:NXResolution': {
                'cbox0a_frequency': DeviceDataset('cbox_0a_fg_freq',
                                                  dtype='float'),
                'cbox0b_frequency': DeviceDataset('cbox_0b_fg_freq',
                                                  dtype='float'),
                'L_sd': DeviceDataset('L_sd', dtype='float'),
                'L_ab': DeviceDataset('L_ab', dtype='float'),
                'L_ad': DeviceDataset('L_bd', dtype='float'),
            },
            # 'collimator:NXcollimator': {
            #     'geometry:NXgeometry': {
            #         'shape:NXshape': {
            #             'shape': ConstDataset('nxbox', 'string'),
            #             'size': DeviceDataset('col', dtype='float'),
            #         },
            #     },
            # },
            'attenuator:NXattenuator': {
                'attenuator_transmission': DeviceDataset('att', dtype='float'),
            },
            # 'beam_stop:NXbeam_stop': {
            #     'x': DeviceDataset('bs1_xax'),
            #     'y': DeviceDataset('bs1_xax'),
            #     'status': DeviceDataset('bs1'),
            #     'description': ConstDataset('rectangular', 'string'),
            # },
            'pol1:NXpolarizer': Polarizer('3He'),
            'pol2:NXpolarizer': Polarizer('3He'),
            # 'all_devices:NXCollection': {
            #     device: {
            #         key: DeviceDataset(key) for key in keys
            #     } for device, keys in all_devices_dict.items()
            # },
        })

    def updateDetector(self):
        self._det.update({
            'data': ImageDataset(0, 0, signal=signal),
            'distance': DeviceDataset('L_sd'),
            'x_pixel_size': ConstDataset(1.5625, 'float',
                                         units=NXAttribute('mm', 'string')),
            'y_pixel_size': ConstDataset(1.5625, 'float',
                                         units=NXAttribute('mm', 'string')),
            'polar_angle': ConstDataset(0, 'float',
                                        units=NXAttribute('deg', 'string')),
            'azimuthal_angle': ConstDataset(
                0, 'float', units=NXAttribute('deg', 'string')),
            'rotation_angle': ConstDataset(0, 'float',
                                           units=NXAttribute('deg', 'string')),
            'aequatorial_angle': ConstDataset(
                0, 'float', units=NXAttribute('deg', 'string')),
            'beam_center_x': ConstDataset(0, 'float',
                                          units=NXAttribute('mm', 'string')),
            'beam_center_y': ConstDataset(0, 'float',
                                          units=NXAttribute('mm', 'string')),
            'type': ConstDataset('Cascade', 'string'),
            'layout': ConstDataset('area', 'string'),
            # 'diameter': ConstDataset(8, 'float',
            #                          units=NXAttribute('mm', 'string')),
            'acquisition_mode': ConstDataset('histogrammed', 'string'),
        })
        self._inst.update({
            'timer:NXmonitor': TimerMonitor('psd_timer'),
            'monitor1:NXmonitor': CounterMonitor('monitor1'),
        })
        preset = session.getDevice('psd').preset()
        if preset.get('monitor1'):
            monitor = 'monitor1'
        else:
            monitor = 'timer'
        monitor = 'monitor1'
        monitorlink = f'/{self.entry}/{self.instrument}/{monitor}'
        self._entry.update({
            'control:NXmonitor': {
                'mode': NXLink(f'{monitorlink}/mode'),
                'preset': NXLink(f'{monitorlink}/preset'),
                'integral': NXLink(f'{monitorlink}/integral'),
            },
        })
        if monitor != 'timer':
            self._entry['control:NXmonitor'].update({
                'type': NXLink(f'{monitorlink}/type'),
            })

    def updateData(self):
        self._entry['data:NXdata'].update({
            'signal': 'data',
            'data': NXLink(f'/{self.entry}/{self.instrument}/detector/data'),
        })

    def updateSample(self):
        self._sample.update({
            'hugo': NexusSampleEnv(),
            'temperature': DeviceDataset('temperature', defaultval=0.0),
            'magfield': DeviceDataset('magfield', defaultval=0.0),
            'aequatorial_angle': ConstDataset(
                0, 'float', units=NXAttribute('degree', 'string')),
            'stick_rotation': OptionalDeviceDataset('dom'),
        })
        if 'sample' in session.loaded_setups:
            self._sample.update(sample_std)
        elif 'emagnet_sample' in session.loaded_setups:
            self._sample.update(sample_magnet)

    def completeTemplate(self):
        MLZTemplateProvider.completeTemplate(self)
        self._entry.update({
            'entry': f'{self.entry}',
        })
