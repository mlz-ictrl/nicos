description = "disc4 height"

group = 'lowlevel'

devices = dict(
    disc4 = device('nicos.devices.generic.Axis',
        description = 'disc 4 Motor',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-30, 46),
            speed = 1.,
            unit = 'mm',
        ),
        precision = 0.01,
    ),
)
