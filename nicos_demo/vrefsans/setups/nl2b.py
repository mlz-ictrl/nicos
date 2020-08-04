description = 'FRM II neutron guide line 2a shutter'

group = 'lowlevel'

includes = ['guidehall']

devices = dict(
    NL2a = device('nicos.devices.generic.ManualSwitch',
        description = 'NL2a shutter status',
        states = ('open', 'closed'),
        pollinterval = 60,
        maxage = 120,
    ),
)
