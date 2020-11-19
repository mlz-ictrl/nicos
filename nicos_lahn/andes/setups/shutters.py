description = 'shutter devices'

group = 'lowlevel'

devices = dict(
    shutter1 = device('nicos.devices.generic.ManualSwitch',
        description = 'shutter 1',
        states = ['closed', 'open'],
    ),
    shutter2 = device('nicos.devices.generic.ManualSwitch',
        description = 'shutter 2',
        states = ['closed', 'open'],
    ),
    shutter3 = device('nicos.devices.generic.ManualSwitch',
        description = 'shutter 3',
        states = ['closed', 'open'],
    ),
)
