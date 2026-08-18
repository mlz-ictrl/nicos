description = 'Optic devices'

group = 'lowlevel'

devices = dict(
    bs = device('nicos.devices.generic.ManualSwitch',
        description = 'Beamstop selection device',
        states = ['down', 'up'],
    ),
    collimator = device('nicos.devices.generic.ManualSwitch',
        description = 'Collimator insert device',
        states = ['out', 'in'],
    ),
    filter = device('nicos.devices.generic.ManualSwitch',
        description = 'Graphite filter device',
        states = ['out', 'in'],
    ),
    laser = device('nicos.devices.generic.ManualSwitch',
        description = 'Adjustment laser device',
        states = ['out', 'in'],
    ),
    shutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Instrument fast shutter',
        states = ['closed', 'open'],
    ),
)
