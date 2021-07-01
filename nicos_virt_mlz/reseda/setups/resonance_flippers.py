#  -*- coding: utf-8 -*-

description = 'Resonance flippers'
group = 'lowlevel'
display_order = 24

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    hrf_0a = device('nicos.devices.generic.ManualMove',
        description = 'Helmholtz coils for resonant flippers arm 0 - A',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        abslimits = (0, 1),
        # precision = 0.02,
    ),
    hrf_0b = device('nicos.devices.generic.ManualMove',
        description = 'Helmholtz coils for resonant flipper arm 0 - B',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        abslimits = (0, 1),
        # precision = 0.02,
    ),
    hrf_1a = device('nicos.devices.generic.ManualMove',
        description = 'Helmholtz coils for resonant flipper arm 1 - A',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        abslimits = (0, 1),
        # precision = 0.02,
    ),
    hrf_1b = device('nicos.devices.generic.ManualMove',
        description = 'Helmholtz coils for resonant flipper arm 1 - B',
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        abslimits = (0, 1),
        # precision = 0.02,
    ),
)
