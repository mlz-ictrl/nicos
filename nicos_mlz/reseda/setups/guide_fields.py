#  -*- coding: utf-8 -*-

description = 'Guide fields'
group = 'lowlevel'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

coils = [8, 14, 15, 18, 9, 7]

devices = {
    'gf%i' % i: device('nicos_mlz.reseda.devices.powersupply.PowerSupply',
        description = 'Guide field %i' % i,
        tangodevice = '%s/coil/b%i' % (tango_base, coil),
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    )
    for i, coil in enumerate(coils)
}
