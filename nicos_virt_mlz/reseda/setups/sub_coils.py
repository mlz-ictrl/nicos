#  -*- coding: utf-8 -*-

description = 'Substraction coils'
group = 'lowlevel'
display_order = 26

devices = dict(
    nse0 = device('nicos.devices.generic.ManualMove',
        description = 'Subtraction coil 0',
        fmtstr = '%.5f',
        pollinterval = 60,
        maxage = 119,
        unit = 'A',
        abslimits = (0, 2),
        # precision = 0.0005,
    ),
    nse1 = device('nicos.devices.generic.ManualMove',
        description = 'Subtraction coil 1',
        fmtstr = '%.5f',
        pollinterval = 60,
        maxage = 119,
        unit = 'A',
        abslimits = (0, 2),
        # precision = 0.0005,
    ),
    phase = device('nicos.devices.generic.ManualMove',
        description = 'NRSE Phase coil',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 119,
        unit = 'A',
        abslimits = (0, 2),
        # precision = 0.005,
    ),
)
