description = 'FRM II neutron guide line 4a shutter'

group = 'lowlevel'

includes = ['guidehall']

devices = dict(
    NL4a = device('nicos.devices.generic.ManualSwitch',
        description = 'NL4a shutter status',
        states = ('closed', 'open'),
        pollinterval = 60,
        maxage = 120,
    ),
)
