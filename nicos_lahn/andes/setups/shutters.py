description = 'shutter devices'

group = 'lowlevel'

devices = dict(
    shutter2 = device('nicos.devices.generic.ManualSwitch',
        description = 'shutter 2',
        states = ['open', 'closed'],
    ),
    shutter3 = device('nicos.devices.generic.ManualSwitch',
        description = 'shutter 3',
        states = ['open', 'closed'],
    ),
)
