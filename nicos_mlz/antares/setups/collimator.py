# -*- coding: utf-8 -*-

description = 'ANTARES collimator drum'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    # Collimator
    collimator_io = device('nicos.devices.tango.DigitalOutput',
        description = 'Tango device for Collimator',
        tangodevice = tango_base + 'fzjdp_digital/Collimator',
        lowlevel = True,
    ),
    L = device('nicos.devices.generic.ManualMove',
        description = 'Distance of detector from the pinhole',
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
    L_sample = device('nicos.devices.generic.manual.ManualMove',
        description = 'Distance of sample from the pinhole',
        unit = 'mm',
        abslimits = (0, 99999999),
    ),
)
