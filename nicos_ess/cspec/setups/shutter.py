description = 'Instrument shutter'

group = 'lowlevel'

devices = dict(
    monolithshutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Shutter close to moderator',
        states = ['open', 'closed']
    ),
    gammashutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Shutter close to moderator',
        states = ['open', 'closed']
    ),
)
