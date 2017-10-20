#  -*- coding: utf-8 -*-

description = 'Resonance flippers'
group = 'lowlevel'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    hrf0 = device('nicos_mlz.reseda.devices.powersupply.PowerSupply',
        description = 'Resonance flipper 0',
        tangodevice = '%s/fug1/current' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
    hrf1 = device('nicos_mlz.reseda.devices.powersupply.PowerSupply',
        description = 'Resonance flipper 1',
        tangodevice = '%s/fug2/current' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 5,
        maxage = 15,
    ),
)
