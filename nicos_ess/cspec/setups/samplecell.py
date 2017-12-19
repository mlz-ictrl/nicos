description = 'Pressure cell'

group = 'optional'

devices = dict(
    P = device('nicos.devices.generic.virtual.VirtualMotor',
        description = 'Sample cell pressure',
        abslimits = (0, 1e8),
        fmtstr = '%.f',
        unit = 'MPa',
        jitter = 2,
        speed = 5,
    ),
)
