#  -*- coding: utf-8 -*-

description = 'Static flippers'
group = 'lowlevel'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    sf_0a = device('nicos_mlz.reseda.devices.powersupply.PowerSupply',
        description = 'Static flipper arm 0 - A',
        tangodevice = '%s/coil/b5' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
    sf_0b = device('nicos_mlz.reseda.devices.powersupply.PowerSupply',
        description = 'Static flipper arm 0 - B',
        tangodevice = '%s/coil/b16' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
    sf_1 = device('nicos_mlz.reseda.devices.powersupply.PowerSupply',
        description = 'Static flipper arm 1',
        tangodevice = '%s/coil/b17' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
)
