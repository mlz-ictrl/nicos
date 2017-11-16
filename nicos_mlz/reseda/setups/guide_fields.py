#  -*- coding: utf-8 -*-

description = 'Guide fields'
group = 'lowlevel'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = {
    'gf%i' % i: device('nicos.devices.tango.PowerSupply',
        description = 'Guide field %i' % i,
        tangodevice = '%s/coil/gf%i' % (tango_base, i),
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ) for i in ([1, 2] + list(range(4, 11)))
}
devices.update({
    'gf4': device('nicos.devices.tango.PowerSupply',
        description = 'Guide field 4',
        tangodevice = '%s/coil/gf4' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    )
})
