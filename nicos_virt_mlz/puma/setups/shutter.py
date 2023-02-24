description = 'Primary shutter'

group = 'lowlevel'

devices = dict(
    alpha1 = device('nicos.devices.generic.ManualSwitch',
        description = 'Primary collimator',
        states = ['closed', '120', '60', '40', '20', ],
        unit = 'min',
    ),
    erbium = device('nicos.devices.generic.ManualSwitch',
        description = 'Erbium filter',
        states = ['out', 'in'],
    ),
    sapphire = device('nicos.devices.generic.ManualSwitch',
        description = 'Sapphire filter',
        states = ['out', 'in'],
    ),
)
