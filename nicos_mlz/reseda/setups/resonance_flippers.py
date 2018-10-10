#  -*- coding: utf-8 -*-

description = 'Resonance flippers'
group = 'lowlevel'
display_order = 24

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    hrf_0a = device('nicos.devices.tango.PowerSupply',
        description = 'Helmholtz coils for resonant flippers arm 0 - A',
        tangodevice = '%s/heinzinger0a/current' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        precision = 0.02,
    ),
    hrf_0b = device('nicos.devices.tango.PowerSupply',
        description = 'Helmholtz coils for resonant flipper arm 0 - B',
        tangodevice = '%s/heinzinger0b/current' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        precision = 0.02,
    ),
    hrf_1a = device('nicos.devices.tango.PowerSupply',
        description = 'Helmholtz coils for resonant flipper arm 1 - A',
        tangodevice = '%s/heinzinger1a/current' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        precision = 0.02,
    ),
    hrf_1b = device('nicos.devices.tango.PowerSupply',
        description = 'Helmholtz coils for resonant flipper arm 1 - B',
        tangodevice = '%s/heinzinger1b/current' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 120,
        unit = 'A',
        precision = 0.02,
    ),
)
