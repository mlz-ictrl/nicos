#  -*- coding: utf-8 -*-

description = 'Substraction coils'
group = 'lowlevel'
display_order = 26

tango_base = 'tango://heinzinger.reseda.frm2:10000/box/heinzinger'

devices = dict(
    nse0 = device('nicos.devices.tango.PowerSupply',
        description = 'Substraction coil 0',
        tangodevice = '%s2/curr' % tango_base,
        fmtstr = '%.4f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
    nse1 = device('nicos.devices.tango.PowerSupply',
        description = 'Substraction coil 1',
        tangodevice = '%s3/curr' % tango_base,
        fmtstr = '%.4f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
)
