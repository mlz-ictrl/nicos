#  -*- coding: utf-8 -*-

description = 'Substraction coils'
group = 'lowlevel'
display_order = 26

tango_base = 'tango://heinzinger.reseda.frm2:10000/box/heinzinger'

coil_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    nse0 = device('nicos.devices.tango.PowerSupply',
        description = 'Subtraction coil 0',
        tangodevice = '%s/nse/current' % coil_base,
        fmtstr = '%.5f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 119,
        unit = 'A',
        precision = 0.0005,
    ),
    nse1 = device('nicos.devices.tango.PowerSupply',
        description = 'Subtraction coil 1',
        tangodevice = '%s/nse1/current' % coil_base,
        fmtstr = '%.5f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 119,
        unit = 'A',
        precision = 0.0005,
    ),
    phase = device('nicos.devices.tango.PowerSupply',
        description = 'NRSE Phase coil',
        tangodevice = '%s/coil/phase' % coil_base,
        tangotimeout = 5.0,
        fmtstr = '%.3f',
        pollinterval = 60,
        maxage = 119,
        unit = 'A',
        precision = 0.005,
    ),
)
