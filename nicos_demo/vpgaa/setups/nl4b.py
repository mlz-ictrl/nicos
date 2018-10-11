description = 'FRM II neutron guide line 4b shutter'

group = 'lowlevel'

includes = ['guidehall']


devices = dict(
    NL4b = device('nicos.devices.generic.ManualSwitch',
        description = 'NL4b shutter status',
        states = ('closed', 'open'),
        pollinterval = 60,
        maxage = 120,
    ),
)
