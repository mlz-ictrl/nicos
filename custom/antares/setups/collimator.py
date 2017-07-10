# -*- coding: utf-8 -*-

description = 'ANTARES collimator drum'

group = 'optional'

includes = []

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    # Collimator
    collimator_io = device('nicos.devices.tango.DigitalOutput',
        description = 'Tango device for Collimator',
        tangodevice = tango_base + 'fzjdp_digital/Collimator',
        lowlevel = True,
    ),
    collimator = device('nicos.devices.generic.Switcher',
        description = 'Collimator, value is L/D',
        moveable = 'collimator_io',
        mapping = {
            200: 2,
            400: 5,
            800: 3,
            1600: 6,
            3200: 1,
            7100: 4,
            'park': 7,
        },
        fallback = '<undefined>',
        unit = 'L/D',
        precision = 0,
    ),
    pinhole = device('nicos.devices.generic.Switcher',
        description = 'Pinhole diameter',
        moveable = 'collimator_io',
        mapping = {
            2: 4,
            4.5: 1,
            9: 6,
            18: 3,
            36: 5,
            71: 2,
            'park': 7,
        },
        fallback = '<undefined>',
        unit = 'mm',
        precision = 0,
    ),
)
