# -*- coding: utf-8 -*-

description = 'ANTARES collimator drum'

group = 'lowlevel'

devices = dict(
    collimator_io = device('nicos.devices.generic.ManualSwitch',
        description = 'Tango device for Collimator',
        states = [1, 2, 3, 4, 5, 6, 7],
        lowlevel = True,
    ),
    L = device('nicos.devices.generic.ManualMove',
        description = 'Distance ... ',
        abslimits = (5000, 18000),
        unit = 'mm',
        fmtstr = '%.1f',
    ),
    collimator = device('nicos_mlz.antares.devices.collimator.CollimatorLoverD',
        description = 'Collimator, value is L/D',
        l = 'L',
        d = 'pinhole',
        unit = 'L/D',
        fmtstr = '%d',
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
