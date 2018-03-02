description = 'sample table rotations'

group = 'lowlevel'

includes = []

devices = dict(
    tths = device('nicos.devices.generic.Axis',
        description = 'Simulated TTHS',
        motor = device('nicos.devices.generic.VirtualMotor',
            fmtstr = '%.3f',
            unit = 'deg',
            abslimits = (-1.5, 60),
            speed = 1,
        ),
        precision = 0.005,
        maxtries = 10,
    ),
    omgs = device('nicos.devices.generic.Axis',
        description = 'Simulated OMGS',
        motor = device('nicos.devices.generic.VirtualMotor',
            fmtstr = '%.3f',
            unit = 'deg',
            abslimits = (-730, 730),
            speed = 2,
        ),
        precision = 0.005,
    ),
)
