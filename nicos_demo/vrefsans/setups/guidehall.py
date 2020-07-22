description = 'FRM II Neutron guide hall west infrastructure devices'

group = 'lowlevel'

devices = dict(
    Sixfold = device('nicos.devices.generic.ManualSwitch',
        description = 'Sixfold shutter status',
        states = ['closed', 'open'],
        pollinterval = 60,
        maxage = 61,
    ),
    NL2b = device('nicos.devices.generic.ManualSwitch',
        description = 'NL2b shutter status',
        states = ['closed', 'open'],
        pollinterval = 60,
        maxage = 61,
    ),
)
