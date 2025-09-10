description = 'Graphite filter devices'

group = 'lowlevel'

devices = dict(
    fshutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Instrument fast shutter',
        states = ['closed', 'open'],
    ),
)
