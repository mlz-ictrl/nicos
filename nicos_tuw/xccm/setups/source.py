description = 'Shutter'

group = 'lowlevel'

devices = dict(
    shutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Shutter',
        states = ['open', 'closed'],
    ),
)
