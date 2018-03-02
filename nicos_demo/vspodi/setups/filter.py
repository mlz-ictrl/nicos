description = 'Graphite filter devices'

group = 'lowlevel'

devices = dict(
    filter = device('nicos.devices.generic.ManualSwitch',
        description = 'Graphite filter device',
        states = ['out', 'in'],
    ),
)
