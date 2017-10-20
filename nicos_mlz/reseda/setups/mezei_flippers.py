#  -*- coding: utf-8 -*-

description = 'Helmholtz mezei flippers'
group = 'lowlevel'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    hsf_0a = device('nicos_mlz.reseda.devices.powersupply.PowerSupply',
        description = 'Helmholtz mezei flipper arm 0 - A',
        tangodevice = '%s/coil/b19' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
    hsf_0b = device('nicos_mlz.reseda.devices.powersupply.PowerSupply',
        description = 'Helmholtz mezei flipper arm 0 - B',
        tangodevice = '%s/coil/b11' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
    hsf_1 = device('nicos_mlz.reseda.devices.powersupply.PowerSupply',
        description = 'Helmholtz mezei flipper arm 1',
        tangodevice = '%s/coil/b20' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
)
