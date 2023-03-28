description = 'Monochromator devices'

group = 'lowlevel'

devices = dict(
    mono_rot = device('nicos.devices.generic.VirtualMotor',
        description = 'Rotation of the monochromator crystal',
        abslimits = (0, 90),
        fmtstr = '%2.f',
        speed = 1,
        unit = 'deg',
    ),
)
