description = 'SAPHiR shutter device'

group = 'lowlevel'

devices = dict(
    shutter = device('nicos.devices.generic.MultiSwitcher',
        description = 'SAPHiR instrument shutter',
        moveables = [
            device('nicos.devices.generic.VirtualMotor',
                abslimits = (-10, 10),
                speed = 1,
                unit = 'mm',
            ),
            device('nicos.devices.generic.VirtualMotor',
                abslimits = (-10, 10),
                speed = 1,
                unit = 'mm',
            ),
        ],
        mapping = {
            'closed': [-10, -10],
            'open': [10, 10],
        },
        unit = '',
        precision = [0.1, 0.1],
    ),
)
