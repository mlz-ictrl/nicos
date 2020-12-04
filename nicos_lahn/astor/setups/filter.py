description = 'filter selector setup'

group = 'lowlevel'

devices = dict(
    crystal_m = device('nicos.devices.generic.Axis',
        description = 'filter changer rotation',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0, 360),
            unit = 'deg',
        ),
        precision = 0.01,
        lowlevel = True,
    ),
    crystal = device('nicos.devices.generic.Switcher',
        description = 'filter changer',
        moveable = 'crystal_m',
        mapping = {
            'c1': 0,
            'c2': 60,
            'c3': 120,
            'c4': 180,
            'c5': 240,
            'c6': 300,
            'xx': 360,
        },
        precision = 0.01,
        unit = '',
    ),
)
