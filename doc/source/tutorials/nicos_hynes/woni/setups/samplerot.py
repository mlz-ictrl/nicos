description = 'Sample rotation device'

group = 'optional'

devices = dict(
    sample_rot = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample rotation',
        abslimits = (-720, 720),
        speed = 1,
        unit = 'deg',
        fmtstr = '%1.f',
    ),
)
