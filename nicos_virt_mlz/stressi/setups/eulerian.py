description = 'STRESS-SPEC setup with Eulerian cradle'

group = 'lowlevel'

devices = dict(
    chis = device('nicos.devices.generic.Axis',
        description = 'Simulated CHIS axis',
        motor = device('nicos.devices.generic.VirtualMotor',
            fmtstr = '%.2f',
            unit = 'deg',
            abslimits = (-180, 180),
            visibility = (),
            speed = 2,
        ),
        precision = 0.001,
    ),
    phis = device('nicos.devices.generic.Axis',
        description = 'Simulated PHIS axis',
        motor = device('nicos.devices.generic.VirtualMotor',
            fmtstr = '%.2f',
            unit = 'deg',
            abslimits = (-720, 720),
            visibility = (),
            speed = 2,
        ),
        precision = 0.001,
    ),
)
