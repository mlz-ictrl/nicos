description = 'High voltage devices'

group = 'lowlevel'

tango_host = 'tango://ps01.stressi.frm2:10000/box/det/'

devices = dict(
    hv1 = device('nicos.devices.entangle.PowerSupply',
        description = 'HV power supply anode',
        requires = {'level': 'admin'},
        tangodevice = tango_host + 'hv1',
        abslimits = (0, 3200),
    ),
    hv1_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'HV power supply anode current',
        device = 'hv1',
        parameter = 'current',
    ),
    hv2 = device('nicos.devices.entangle.PowerSupply',
        description = 'HV power supply drift',
        requires = {'level': 'admin'},
        tangodevice = tango_host + 'hv2',
        abslimits = (-2500, 0),
    ),
    hv2_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'HV power supply drift current',
        device = 'hv2',
        parameter = 'current',
    ),
)
