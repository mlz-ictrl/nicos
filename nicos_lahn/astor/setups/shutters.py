description = 'shutter devices setup'

group = 'lowlevel'

devices = dict(
    shutter2 = device('nicos.devices.generic.ManualSwitch',
        description = 'shutter 2',
        states = ['open', 'closed'],
    ),
    fastshutter = device('nicos.devices.generic.ManualSwitch',
        description = 'fast shutter',
        states = ['open', 'closed'],
    ),
)
