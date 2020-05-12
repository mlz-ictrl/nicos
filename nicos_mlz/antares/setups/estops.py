# -*- coding: utf-8 -*-

description = 'ANTARES cabinet emergency stops'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    EstopMain = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Emergency stop of main cabinet',
        tangodevice = tango_base + 'fzjdp_digital/EstopMain',
        mapping = {'on': 1,
                   'off': 0},
        warnlimits = ('off', 'off'),
        unit = '',
    ),
    EstopHuber = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Emergency stop of Huber cabinet',
        tangodevice = tango_base + 'fzjdp_digital/EstopHuber',
        mapping = {'on': 1,
                   'off': 0},
        warnlimits = ('off', 'off'),
        unit = '',
    ),
    EstopSlitSmall = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Emergency stop of small slit cabinet',
        tangodevice = tango_base + 'fzjdp_digital/EstopSlitSmall',
        mapping = {'on': 1,
                   'off': 0},
        warnlimits = ('off', 'off'),
        unit = '',
    ),
    EstopSlitLarge = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Emergency stop of large slit cabinet',
        tangodevice = tango_base + 'fzjdp_digital/EstopSlitLarge',
        mapping = {'on': 1,
                   'off': 0},
        warnlimits = ('off', 'off'),
        unit = '',
    ),
    EstopDetector = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Emergency stop of detector cabinet',
        tangodevice = tango_base + 'fzjdp_digital/EstopDetector',
        mapping = {'on': 1,
                   'off': 0},
        warnlimits = ('off', 'off'),
        unit = '',
    ),
)
