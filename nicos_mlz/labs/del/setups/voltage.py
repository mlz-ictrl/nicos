description = 'high voltage power supplies for detector'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/del/'

devices = dict(
    hv0 = device('nicos.devices.entangle.PowerSupply',
        description = 'ISEG HV power supply 1',
        # requires = {'level': 'admin'},
        tangodevice = tango_base + 'iseg1/voltage',
        abslimits = (0, 3000),
        ramp = 120,
        pollinterval = 5,
        maxage = 61,
    ),
    hv0cur = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'ISEG HV power supply 1 (current)',
        device = 'hv0',
        parameter = 'current',
        pollinterval = 5,
        maxage = 61,
        fmtstr = '%.3f',
    ),
    hv1 = device('nicos.devices.entangle.PowerSupply',
        description = 'ISEG HV power supply 2',
        # requires = {'level': 'admin'},
        tangodevice = tango_base + 'iseg2/voltage',
        abslimits = (0, 3000),
        ramp = 120,
        pollinterval = 5,
        maxage = 61,
    ),
    hv1cur = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'ISEG HV power supply 1 (current)',
        device = 'hv1',
        parameter = 'current',
        pollinterval = 5,
        maxage = 61,
        fmtstr = '%.3f',
    ),
)
