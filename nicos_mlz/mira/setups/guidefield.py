#  -*- coding: utf-8 -*-

description = '4 E3633A Power supplies'

group = 'optional'

tango_base = 'tango://miractrl.mira.frm2:10000/mira'

includes = []

devices = {
    'gf1':
        device('nicos.devices.tango.PowerSupply',
            description = 'Current of gf1',
            tangodevice = '%s/gf1/current' % (tango_base,),
            abslimits = (0.000, 20.0),
            unit = 'A',
        ),
    'gf2':
        device('nicos.devices.tango.PowerSupply',
            description = 'Current of gf2',
            tangodevice = '%s/gf2/current' % (tango_base,),
            abslimits = (0.000, 20.0),
            unit = 'A',
        ),
    'gf3':
        device('nicos.devices.tango.PowerSupply',
            description = 'Current of gf3',
            tangodevice = '%s/gf3/current' % (tango_base,),
            abslimits = (0.000, 20.0),
            unit = 'A',
        ),
    'gf4':
        device('nicos.devices.tango.PowerSupply',
            description = 'Current of gf4',
            tangodevice = '%s/gf4/current' % (tango_base,),
            abslimits = (0.000, 20.0),
            unit = 'A',
        ),
}

