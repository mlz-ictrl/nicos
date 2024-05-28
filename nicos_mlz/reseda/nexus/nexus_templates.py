#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
from nicos.nexus.elements import ConstDataset, DeviceAttribute, \
    DeviceDataset, ImageDataset, NexusSampleEnv, NXAttribute, NXLink, NXTime
from nicos.nexus.nexussink import NexusTemplateProvider, copy_nexus_template
from nicos.nexus.specialelements import NicosProgramDataset

from nicos_mlz.nexus import CounterMonitor, ReactorSource, TimerMonitor
from nicos_sinq.nexus.specialelements import OptionalDeviceDataset

all_devices_dict = {
    key: val for key, val in session.devices.items() if 'read' in dir(val)
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


reseda_detector = {
    'data': ImageDataset(0, 0, signal=NXAttribute(1, 'int32')),
    # 'distance': DeviceDataset('det1_x'),
    'x_pixel_size': ConstDataset(1.5625, 'float',
                                 units=NXAttribute('mm', 'string')),
    'y_pixel_size': ConstDataset(1.5625, 'float',
                                 units=NXAttribute('mm', 'string')),
    'polar_angle': ConstDataset(0, 'float',
                                units=NXAttribute('degree', 'string')),
    'azimuthal_angle': ConstDataset(0, 'float',
                                    units=NXAttribute('degree', 'string')),
    'rotation_angle': ConstDataset(0, 'float',
                                   units=NXAttribute('degree', 'string')),
    'aequatorial_angle': ConstDataset(0, 'float',
                                      units=NXAttribute('degree', 'string')),
    'beam_center_x': ConstDataset(0, 'float',
                                  units=NXAttribute('mm', 'string')),
    'beam_center_y': ConstDataset(0, 'float',
                                  units=NXAttribute('mm', 'string')),
    'type': ConstDataset('Cascade', 'string'),
    'layout': ConstDataset('area', 'string'),
    # 'diameter': ConstDataset(8, 'float',
    #                          units=NXAttribute('mm', 'string')),
    # TODO: find out how to set the correct value for tisane
    'acquisition_mode': ConstDataset('histogrammed', 'string'),
}

URL = 'https://manual.nexusformat.org/classes/applications/NXsas.html'

reseda_default = {
    'NeXus_Version': 'v2022.07',
    'instrument': DeviceAttribute(session.instrument.name, 'instrument'),
    'owner': DeviceAttribute(session.instrument.name, 'responsible'),
    'entry1:NXentry': {
        'entry': 'entry1',
        'program_name': NicosProgramDataset(),
        'title': DeviceDataset(session.experiment.name, 'title'),
        'experiment_description': DeviceDataset(session.experiment.name,
                                                'title'),
        'experiment_identifier': DeviceDataset(session.experiment.name,
                                               'proposal'),
        # 'collection_identifier': {},
        # 'collection_description': {},
        # 'entry_identifier': {},
        # 'entry_uuid': {},
        'start_time': NXTime(),
        'end_time': NXTime(),
        'definition': ConstDataset('NXsas', 'string',
                                   version=NXAttribute('mm', 'string'),
                                   URL=NXAttribute(URL, 'string')),
        'local_contact:NXuser': {
            'role': ConstDataset('local_contact', 'string'),
            # TODO: split name from email address
            'name': DeviceDataset(session.experiment.name, 'localcontact'),
            'email': DeviceDataset(session.experiment.name, 'localcontact'),
        },
        'proposal_user:NXuser': {
            'role': ConstDataset('principal_investigator', 'string'),
            # TODO: split name from email address
            'name': DeviceDataset(session.experiment.name, 'users'),
            'email': DeviceDataset(session.experiment.name, 'users')
        },
        'instrument:NXinstrument': {
            'source:NXsource': ReactorSource('FRM II', 'ReactorPower'),
            'monochromator:NXmonochromator': {
                'wavelength': NXLink(
                    '/entry1/instrument/monochromator/velocity_selector/wavelength'),
                'wavelength_spread': NXLink(
                    '/entry1/instrument/monochromator/velocity_selector/wavelength_spread'),
                'velocity_selector:NXvelocity_selector': {
                    'type': ConstDataset('Astrium Velocity Selector',
                                         'string'),
                    'rotation_speed': DeviceDataset('selector_speed'),
                    # TODO: 'diameter' / 2
                    'radius': DeviceDataset(
                        'selector_delta_lambda', 'diameter', dtype='float'),
                    'spwidth': DeviceDataset(
                        'selector_delta_lambda', 'd_lamellae'),
                    'length': DeviceDataset('selector_lambda', 'length'),
                    'num': DeviceDataset(
                        'selector_delta_lambda', 'n_lamellae', dtype='int'),
                    'twist': DeviceDataset('selector_lambda', 'twistangle'),
                    'wavelength': DeviceDataset(
                        'selector_lambda', dtype='float'),
                    'wavelength_spread': DeviceDataset(
                        'selector_delta_lambda', dtype='float'),
                    'beamcenter': DeviceDataset(
                        'selector_lambda', 'beamcenter'),
                    'tilt': DeviceDataset('selector_tilt'),
                },
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
            # 'all_devices:NXCollection': {
            #     device: {
            #         key: DeviceDataset(key) for key in keys
            #     } for device, keys in all_devices_dict.items()
            # },
            # 'collimator:NXcollimator': {
            #     'geometry:NXgeometry': {
            #         'shape:NXshape': {
            #             'shape': ConstDataset('nxbox', 'string'),
            #             'size': DeviceDataset('col', dtype='float'),
            #         },
            #     },
            # },
            # 'detector:NXdetector': {},
            'name': ConstDataset(session.instrument.instrument, 'string'),
            'attenuator:NXattenuator': {
                'attenuator_transmission': DeviceDataset('att', dtype='float'),
            },
            # 'beam_stop:NXbeam_stop': {
            #     'x': DeviceDataset('bs1_xax'),
            #     'y': DeviceDataset('bs1_xax'),
            #     'status': DeviceDataset('bs1'),
            #     'description': ConstDataset('rectangular', 'string'),
            # },
            'timer:NXmonitor': TimerMonitor('psd_timer'),
            'monitor1:NXmonitor': CounterMonitor('monitor1'),
            # 'monitor2:NXmonitor': CounterMonitor('monitor2'),
        },  # instrument
        # 'sample:NXSample': {},
        'control:NXmonitor': {
            'mode': NXLink('/entry1/instrument/monitor1/mode'),
            'preset': NXLink('/entry1/instrument/monitor1/preset'),
            'integral': NXLink('/entry1/instrument/monitor1/integral'),
            'type': NXLink('/entry1/instrument/monitor1/type'),
        },  # control
        'data:NXdata': {
            'signal': 'data',
            'data': NXLink('/entry1/instrument/detector/data'),
        },  # data
    }  # entry
}  # root

polarizer_1 = {
    'pol1:NXpolarizer': {
        'type': ConstDataset('supermirror', 'string'),
        # 'reflection': ConstDataset(0.99, 'float'),
        # 'composition': ConstDataset('blah blubb', 'string'),
        # 'efficiency': ConstDataset(0.7, dtype='float'),
    },
}

polarizer_2 = {
    'pol2:NXpolarizer': {
        'type': ConstDataset('supermirror', 'string'),
        # 'reflection': ConstDataset(0.99, 'float'),
        # 'composition': ConstDataset('blah blubb', 'string'),
        # 'efficiency': ConstDataset(0.7, dtype='float'),
    },
}

sample_common = {
    'name': DeviceDataset('Sample', 'samplename'),
    'hugo': NexusSampleEnv(),
    'temperature': DeviceDataset('temperature', defaultval=0.0),
    'magfield': DeviceDataset('magfield', defaultval=0.0),
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


class ResedaTemplateProvider(NexusTemplateProvider):
    def getTemplate(self):
        full = copy_nexus_template(reseda_default)
        instrument = full['entry1:NXentry']['instrument:NXinstrument']
        instrument['detector:NXdetector'] = copy_nexus_template(reseda_detector)
        instrument['pol1:NXpolarizer'] = copy_nexus_template(polarizer_1)
        instrument['pol2:NXpolarizer'] = copy_nexus_template(polarizer_2)
        if 'sample' in session.loaded_setups:
            full['entry1:NXentry']['sample:NXsample'] = \
                dict(sample_common, **sample_std)
        elif 'emagnet_sample' in session.loaded_setups:
            full['entry1:NXentry']['sample:NXsample'] = \
                dict(sample_common, **sample_magnet)
        else:
            full['entry1:NXentry']['sample:NXsample'] = sample_common
        return full
