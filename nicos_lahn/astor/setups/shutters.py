description = 'shutter devices setup'

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
    fastshutter = device('nicos.devices.generic.ManualSwitch',
        description = 'fast shutter',
        states = ['closed', 'open'],
    ),
)
