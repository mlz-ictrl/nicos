description = 'Slits'

group = 'lowlevel'

s3_offset = 0

devices = dict(
    s3 = device('nicos.devices.generic.Switcher',
        description = 'Slit 3',
        moveable = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0, 300),
            speed = 5,
            unit = 'mm',
        ),
        mapping = {
            2: 39 + s3_offset,
            4: 31 + s3_offset,
            6: 21 + s3_offset,
            10: 8 + s3_offset,
        },
        precision = 0.01,
        unit = 'mm',
    ),
)
