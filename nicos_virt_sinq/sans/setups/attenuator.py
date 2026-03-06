description = 'Devices for the attenuator'

group = 'lowlevel'

devices = dict(
    attpos = device('nicos.devices.generic.VirtualMotor',
        description = 'Attenuator motor',
        abslimits = (-10.5555, 310.1096),
        unit = 'mm',
        speed = 50,
    ),
    att = device('nicos.devices.generic.switcher.Switcher',
        description = 'Attenuator choice',
        moveable = 'attpos',
        mapping = {
            '0': 0,
            '1': 60,
            '2': 120,
            '3': 180,
            '4': 240,
            '5': 300
        },
        precision = 1,
    ),
)
