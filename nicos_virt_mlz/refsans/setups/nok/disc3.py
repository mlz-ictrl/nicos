description = "disc3 height"

group = 'lowlevel'

devices = dict(
    disc3 = device('nicos.devices.generic.Axis',
        description = 'disc 3 Motor',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-43, 48),
            speed = 1,
            unit = 'mm',
        ),
        precision = 0.01,
    ),
)
