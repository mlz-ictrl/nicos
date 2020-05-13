description = 'Chopper 2'

group = 'optional'

devices = dict(
    ch1_speed=device('nicos.devices.generic.virtual.VirtualMotor',
        description='Rotation speed',
        abslimits=(0, 300),
        userlimits=(0, 300),
        fmtstr='%.f',
        unit='Hz',
        speed=5,
    ),
    ch1_phase=device('nicos.devices.generic.virtual.VirtualMotor',
        description='Phase angle',
        abslimits=(-180, 180),
        userlimits=(-180, 180),
        fmtstr='%.f',
        unit='Hz',
        jitter=2,
        speed=5,
    ),
)
