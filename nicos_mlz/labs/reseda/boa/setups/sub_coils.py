#  -*- coding: utf-8 -*-

description = 'Substraction coils'
group = 'lowlevel'
display_order = 26

tango_base = 'tango://%s:10000/reseda/' % configdata('gconfigs.tango_host')

devices = dict(
    nse0 = device('nicos.devices.entangle.PowerSupply',
        description = 'Subtraction coil 0',
        tangodevice = tango_base + 'nse/current',
        fmtstr = '%.5f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 119,
        unit = 'A',
        precision = 0.0005,
    ),
    # nse1 = device('nicos.devices.entangle.PowerSupply',
    #     description = 'Subtraction coil 1',
    #     tangodevice = tango_base + 'nse1/current',
    #     fmtstr = '%.5f',
    #     tangotimeout = 5.0,
    #     pollinterval = 60,
    #     maxage = 119,
    #     unit = 'A',
    #     precision = 0.0005,
    # ),
    # phase = device('nicos.devices.entangle.PowerSupply',
    #     description = 'NRSE Phase coil',
    #     tangodevice = tango_base + 'coil/phase',
    #     tangotimeout = 5.0,
    #     fmtstr = '%.3f',
    #     pollinterval = 60,
    #     maxage = 119,
    #     unit = 'A',
    #     precision = 0.005,
    # ),
)
