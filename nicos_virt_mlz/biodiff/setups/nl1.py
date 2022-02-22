description = 'FRM II neutron guide line 4b shutter'

group = 'lowlevel'

includes = ['guidehall']


devices = dict(
    NL1 = device('nicos.devices.generic.ManualSwitch',
        description = 'NL1 shutter status',
        states = ('open', 'closed'),
        pollinterval = 60,
        maxage = 120,
    ),
)
