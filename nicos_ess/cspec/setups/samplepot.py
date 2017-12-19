description = 'Sample environment pot'

group = 'lowlevel'

devices = dict(
    vacpot = device('nicos.devices.generic.VirtualMotor',
        description = 'Vacuum sensor in sample pot',
        abslimits = (0, 1000),
        pollinterval = 10,
        maxage = 12,
        unit = 'mbar',
        curvalue = 1.1e-3,
        fmtstr = '%.2e',
        jitter = 1.e-4,
    ),
    potgate = device('nicos.devices.generic.ManualSwitch',
        description = 'Sample pot valve',
        states = ['closed', 'open']
    ),
)
