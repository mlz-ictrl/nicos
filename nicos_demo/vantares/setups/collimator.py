# -*- coding: utf-8 -*-

description = 'ANTARES collimator drum'

group = 'lowlevel'

devices = dict(
    collimator_io = device('nicos.devices.generic.ManualSwitch',
        description = 'Tango device for Collimator',
        states = [1, 2, 3, 4, 5, 6, 7],
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
