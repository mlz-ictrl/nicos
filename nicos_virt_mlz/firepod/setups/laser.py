description = 'Adjustment laser devices'

group = 'lowlevel'

devices = dict(
    laser = device('nicos.devices.generic.ManualSwitch',
        description = 'Adjustment laser device',
        states = ['out', 'in'],
    ),
)
