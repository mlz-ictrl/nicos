#  -*- coding: utf-8 -*-

description = 'Coils'
group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = {
    'b%i' % i: device('nicos.devices.tango.PowerSupply',
        description = 'Coil b%i' % i,
        tangodevice = '%s/coil/b%i' % (tango_base, i),
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 12,
    )
    for i in range(5, 21)
}
