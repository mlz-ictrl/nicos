#  -*- coding: utf-8 -*-

description = 'Resonance flippers'
group = 'lowlevel'
display_order = 24

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    hrf_0a = device('nicos.devices.tango.PowerSupply',
        description = 'Helmholtz coils for resonant flippers arm 0 - A',
        tangodevice = '%s/fug1/current' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
    hrf_0b = device('nicos.devices.tango.PowerSupply',
        description = 'Helmholtz coils for resonant flipper arm 0 - B',
        tangodevice = '%s/fug2/current' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
    hrf_1 = device('nicos.devices.tango.PowerSupply',
        description = 'Helmholtz coils for resonant flipper arm 1',
        tangodevice = '%s/fug3/current' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
)
