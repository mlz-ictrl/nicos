description = 'Reseda arm 2 (MIEZE)'

group = 'optional'

devices = dict(
    arm2_rot = device('nicos.devices.generic.Axis',
        description = 'Rotation arm 1',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-15, 55),
            unit = 'deg',
            speed = 5,
            curvalue = 10,
        ),
        fmtstr = '%.3f',
        precision = 0.01,
    ),
)
