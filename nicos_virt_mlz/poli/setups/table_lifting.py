description = 'POLI lifting counter'

group = 'lowlevel'

devices = dict(
    liftingctr = device('nicos.devices.generic.VirtualMotor',
        description = 'lifting counter axis',
        unit = 'deg',
        fmtstr = '%.2f',
        abslimits = (-4.2, 30),
        speed = 2.0,
    ),
)
