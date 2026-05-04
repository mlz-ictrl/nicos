description = 'Slits'

group = 'lowlevel'

devices = dict(
    s3 = device('nicos.devices.generic.Switcher',
        description = 'Slit 3',
        moveable = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0, 300),
            speed = 5,
            unit = 'mm',
        ),
        mapping = {
            1: 10,
            2: 40,
            3: 71,
            4: 102,
            5: 130,
            6: 200,
            9: 300,
        },
        precision = 0.01,
        unit = 'mm',
    ),
)
