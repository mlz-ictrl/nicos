#  -*- coding: utf-8 -*-

description = 'Aux Motor setup'
group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    aux1_mot = device('nicos.devices.entangle.Motor',
        description = 'Aux motor 1',
        tangodevice = '%s/hupp/aux1' % tango_base,
    ),
    aux2_mot = device('nicos.devices.entangle.Motor',
        description = 'Aux motor 2',
        tangodevice = '%s/hupp/aux2' % tango_base,
    ),
    aux3_mot = device('nicos.devices.entangle.Motor',
        description = 'Aux motor 3',
        tangodevice = '%s/hupp/aux3' % tango_base,
    ),
    aux4_mot = device('nicos.devices.entangle.Motor',
        description = 'Aux motor 4',
        tangodevice = '%s/hupp/aux4' % tango_base,
    ),
    aux5_mot = device('nicos.devices.entangle.Motor',
        description = 'Aux motor 5',
        tangodevice = '%s/hupp/aux5' % tango_base,
    ),
    aux6_mot = device('nicos.devices.entangle.Motor',
        description = 'Aux motor 6',
        tangodevice = '%s/hupp/aux6' % tango_base,
    ),
)
